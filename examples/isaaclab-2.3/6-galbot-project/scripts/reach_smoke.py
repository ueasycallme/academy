# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""Galbot-Reach-v0 的冒烟检查（6.4.1）：零动作跑过一次超时重置，检查任务各部分是否按设计工作。

- 非任务关节（腿、头、左臂、夹爪）是否保持在默认位置；
- 第二个回合开头，右臂关节相对默认值的偏移是否落在 reset 事件的 ±0.2 rad 内
  （第一个回合不看：首次 reset 时的初速度会被夹成 0，见 4.6 常见坑四；这里位置也一并只看第二个回合）；
- 采样到的目标是否在命令范围内，以及零动作时 TCP 离目标多远；
- 有无 NaN。

    python scripts/reach_smoke.py --headless
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="reach 冒烟检查")
parser.add_argument("--task", default="Galbot-Reach-v0")
parser.add_argument("--num_envs", type=int, default=64)
parser.add_argument("--seed", type=int, default=0)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

import galbot_academy.tasks  # noqa: F401


def main() -> None:
    cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    cfg.seed = args.seed
    env = gym.make(args.task, cfg=cfg)
    base = env.unwrapped
    robot = base.scene["robot"]
    names = robot.joint_names
    arm = [i for i, n in enumerate(names) if n.startswith("right_arm_joint")]
    other = [i for i in range(len(names)) if i not in arm and "gripper" not in names[i]]
    T = int(base.max_episode_length)
    print(f"{args.task}：{args.num_envs} 个环境，控制周期 {base.step_dt:.4f} s，回合 {T} 步（{base.max_episode_length_s:.0f} s）")

    env.reset()
    zero = torch.zeros(env.action_space.shape, device=base.device)
    cmd_lo = torch.full((3,), float("inf"), device=base.device)
    cmd_hi = -cmd_lo
    err_first = None
    other_dev = 0.0
    for k in range(T + 5):
        _, _, term, trunc, _ = env.step(zero)
        cmd = base.command_manager.get_command("ee_pose")[:, :3]
        cmd_lo, cmd_hi = torch.minimum(cmd_lo, cmd.min(0).values), torch.maximum(cmd_hi, cmd.max(0).values)
        if k == 0:
            err_first = base.command_manager.get_term("ee_pose").metrics["position_error"].clone()
        if k > T // 2:
            other_dev = max(other_dev, (robot.data.joint_pos[:, other] - robot.data.default_joint_pos[:, other]).abs().max().item())
        if k == T - 1:  # 第 T 步（从 0 计为 T-1）触发超时重置，返回的已是第二个回合开头的状态
            off = robot.data.joint_pos[:, arm] - robot.data.default_joint_pos[:, arm]
            n_reset = int((term | trunc).sum().item())
    print(f"  第 {T} 步共有 {n_reset} 个环境超时重置（应为全部 {args.num_envs} 个）")
    print(f"  第二个回合开头，右臂关节相对默认值：最小 {off.min().item():+.3f}，最大 {off.max().item():+.3f} rad（reset 事件为 ±0.2）")
    print(f"  非任务关节（不含夹爪）在回合后半段离默认值最远 {other_dev:.4f} rad")
    r = cfg.commands.ee_pose.ranges
    print(f"  目标位置（根坐标系）：x [{cmd_lo[0]:.3f}, {cmd_hi[0]:.3f}]，y [{cmd_lo[1]:.3f}, {cmd_hi[1]:.3f}]，z [{cmd_lo[2]:.3f}, {cmd_hi[2]:.3f}]；"
          f"配置范围 x {r.pos_x}，y {r.pos_y}，z {r.pos_z}")
    print(f"  第 1 步 TCP 离目标：中位数 {err_first.median().item():.3f} m，最大 {err_first.max().item():.3f} m")
    print(f"  数值有限：{bool(torch.isfinite(robot.data.joint_pos).all())}")
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
