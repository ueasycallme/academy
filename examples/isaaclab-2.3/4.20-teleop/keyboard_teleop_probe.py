# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""不碰键盘，用脚本"按键"，验证 Se3Keyboard → IK 动作 → 环境这条链（4.20）。

做法与 teleop_se3_agent.py 相同：官方 Isaac-Lift-Cube-Franka-IK-Rel-v0，1 个环境，关掉超时；
设备用脚本里的后备键盘 Se3Keyboard(pos_sensitivity=0.05, rot_sensitivity=0.05)。
按键有两种注入方式：
- provider（默认）：经 carb.input 的 InputProvider 把按键事件放进输入缓冲，再分发，
  走的是 Se3Keyboard 自己订阅的那条回调路径，只绕过了键盘硬件和窗口；
- direct：直接调用 Se3Keyboard._on_keyboard_event，传一个假事件（provider 不可用时的后备）。

每段按住一个键若干步、再松开，打印末端（panda_hand + 0.107 m 偏移，即 IK 跟踪的那个点）在机器人根坐标系下的
位移、姿态变化的转轴，以及夹爪指关节位置。

用法::

    python keyboard_teleop_probe.py --headless
    python keyboard_teleop_probe.py --headless --inject direct
"""

import argparse
import sys
import time

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="脚本触发 Se3Keyboard 回调，验证遥操作链路")
parser.add_argument("--task", default="Isaac-Lift-Cube-Franka-IK-Rel-v0")
parser.add_argument("--inject", choices=["provider", "direct"], default="provider", help="按键注入方式")
parser.add_argument("--hold", type=int, default=25, help="每个键按住的控制步数")
parser.add_argument("--settle", type=int, default=25, help="松开后再走的步数")
parser.add_argument("--enable_appwindow", action="store_true", help="headless 时手动启用 omni.appwindow 扩展")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

from types import SimpleNamespace

import carb
import gymnasium as gym
import torch

if args.enable_appwindow:
    from isaacsim.core.utils.extensions import enable_extension

    enable_extension("omni.appwindow")
    simulation_app.update()
try:
    import omni.appwindow
except ModuleNotFoundError as e:
    print(f"[probe] 无法导入 omni.appwindow：{e}", flush=True)

import isaaclab.utils.math as math_utils
from isaaclab.devices import Se3Keyboard, Se3KeyboardCfg

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

# 每段：(按住的键, 说明)；"K" 是切换夹爪，按一下即可
SEQUENCE = [("W", "+x"), ("Q", "+z"), ("A", "+y"), ("C", "绕 z 转"), ("K", "夹爪开/合")]


class KeyInjector:
    """把"按下 / 松开"送进 Se3Keyboard。"""

    def __init__(self, device: Se3Keyboard, mode: str):
        self.device, self.mode = device, mode
        if mode == "provider":
            self.keyboard = omni.appwindow.get_default_app_window().get_keyboard()
            self.provider = carb.input.acquire_input_provider()
            self.input = carb.input.acquire_input_interface()

    def send(self, key: str, pressed: bool):
        etype = carb.input.KeyboardEventType.KEY_PRESS if pressed else carb.input.KeyboardEventType.KEY_RELEASE
        if self.mode == "provider":
            self.provider.buffer_keyboard_key_event(self.keyboard, etype, getattr(carb.input.KeyboardInput, key), 0)
            self.input.distribute_buffered_events()  # 立即分发，不等下一次 app.update
        else:
            self.device._on_keyboard_event(SimpleNamespace(type=etype, input=SimpleNamespace(name=key)))


def main() -> None:
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=1)
    env_cfg.terminations.time_out = None  # 与 teleop_se3_agent.py 相同
    env_cfg.commands.object_pose.resampling_time_range = (1.0e9, 1.0e9)
    env = gym.make(args.task, cfg=env_cfg).unwrapped
    print(f"[probe] step_dt {env.step_dt:.3f} s，动作维数 {env.action_manager.total_action_dim}："
          f"{env.action_manager.active_terms}", flush=True)

    try:
        device = Se3Keyboard(Se3KeyboardCfg(pos_sensitivity=0.05, rot_sensitivity=0.05))
    except Exception as e:  # headless 下没有窗口与键盘
        print(f"[probe] 创建 Se3Keyboard 失败：{type(e).__name__}: {e}", flush=True)
        env.close()
        return
    kb = omni.appwindow.get_default_app_window().get_keyboard()
    print(f"[probe] 默认窗口的键盘：{carb.input.acquire_input_interface().get_keyboard_name(kb)!r}；注入方式 {args.inject}", flush=True)
    inj = KeyInjector(device, args.inject)
    arm = env.action_manager.get_term("arm_action")
    robot = env.scene["robot"]
    fingers = [i for i, n in enumerate(robot.joint_names) if n.startswith("panda_finger")]

    env.reset()
    device.reset()
    n_steps, t0 = 0, time.monotonic()

    def run(steps: int) -> torch.Tensor:
        nonlocal n_steps
        cmd = None
        with torch.inference_mode():
            for _ in range(steps):
                cmd = device.advance()
                env.step(cmd.repeat(env.num_envs, 1))
                n_steps += 1
        return cmd

    run(args.settle)  # 先让手臂停稳
    for key, label in SEQUENCE:
        p0, q0 = (t.clone() for t in arm._compute_frame_pose())
        f0 = robot.data.joint_pos[0, fingers].clone()
        inj.send(key, True)
        cmd_held = run(1 if key == "K" else args.hold)
        inj.send(key, False)
        cmd_after = run(args.settle)
        p1, q1 = arm._compute_frame_pose()
        dq = math_utils.quat_mul(q1, math_utils.quat_inv(q0))  # 根坐标系下的转动
        angle = 2 * torch.acos(dq[0, 0].abs().clamp(max=1.0)).item()
        axis = dq[0, 1:] / max(torch.linalg.norm(dq[0, 1:]).item(), 1e-9) * torch.sign(dq[0, 0])
        dp = (p1 - p0)[0] * 100
        print(f"[probe] {key}（{label}）：按住时命令 {[round(x, 3) for x in cmd_held.tolist()]}，松开后 {[round(x, 3) for x in cmd_after.tolist()]}")
        print(f"        末端位移（根坐标系）[{dp[0]:+.1f}, {dp[1]:+.1f}, {dp[2]:+.1f}] cm；转角 {angle:.3f} rad，"
              f"转轴（根坐标系）[{axis[0]:+.2f}, {axis[1]:+.2f}, {axis[2]:+.2f}]；指关节 {f0.tolist()} → "
              f"{[round(x, 4) for x in robot.data.joint_pos[0, fingers].tolist()]}", flush=True)
    wall = time.monotonic() - t0
    print(f"[probe] 共 {n_steps} 步，墙上 {wall:.1f} s，{n_steps / wall:.0f} 步/s（仿真时间 {n_steps * env.step_dt:.1f} s）", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
