# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）+ isaacsim.ros2.bridge 4.12.4（自带 Humble 库）
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""reach 的 ROS 2 闭环（6.7.2）：Isaac Lab 环境当"机器人"，策略在另一个进程里（ros2/reach_policy_node.py）。

每个控制步：发布观测 → 等策略节点回传同一步序号的动作（超时就保持上一步动作）→ env.step。
仿真等动作，所以结果不受两边速度影响；--delay N 让第 k 步执行第 k-N 步观测算出的动作，模拟 N 个控制步的延迟。
评估口径与 scripts/eval_reach.py 相同：每段目标（4 s）的最后一步记录 TCP 误差。

必须在"自带 ROS 2 库"的终端环境里运行（ROS_DISTRO、RMW_IMPLEMENTATION、LD_LIBRARY_PATH，见 3.10 表 1），
不要 source 系统 Humble：那样 Isaac Sim 里的 rclpy 无法导入（3.10 坑二）。

    python scripts/run_ros2_sim.py --headless --mode ros2 --episodes 128 [--delay 1] [--checkpoint …/model_999.pt]
    python scripts/run_ros2_sim.py --headless --mode inproc --episodes 128 --checkpoint …/model_999.pt
"""

import argparse
import collections
import os
import sys
import time

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="reach 策略的 ROS 2 闭环评估")
parser.add_argument("--task", default="Galbot-Reach-Play-v0")
parser.add_argument("--mode", choices=["ros2", "inproc"], default="ros2", help="ros2：策略在外部节点；inproc：进程内推理（对照）")
parser.add_argument("--checkpoint", default=None, help="inproc 必需；ros2 时可选，用来逐步比对外部节点的动作")
parser.add_argument("--episodes", type=int, default=128, help="回合数；每回合 12 s、3 段目标")
parser.add_argument("--delay", type=int, default=0, help="人为延迟的控制步数（仅 ros2）")
parser.add_argument("--timeout", type=float, default=1.0, help="等一个动作的墙上时间上限（s），超时保持上一步动作")
parser.add_argument("--seed", type=int, default=0)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
if args.mode == "ros2" and "humble/lib" not in os.environ.get("LD_LIBRARY_PATH", ""):
    print("警告：LD_LIBRARY_PATH 里没有 Bridge 自带的 humble/lib，ROS 2 Bridge 很可能启动失败（3.10 表 1）", flush=True)
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import load_cfg_from_registry, parse_env_cfg

import galbot_academy.tasks  # noqa: F401

if args.mode == "ros2":
    # 启用 Bridge 后，它把自带的 rclpy（Python 3.11）加进 sys.path（3.10"用哪套 ROS 2 库"）
    from isaacsim.core.utils.extensions import enable_extension

    enable_extension("isaacsim.ros2.bridge")
    simulation_app.update()
    import rclpy
    from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
    from std_msgs.msg import Float32MultiArray

    QOS = QoSProfile(reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST, depth=10)


class Ros2Policy:
    """把"发观测、等动作"包装成一个可调用的策略。"""

    def __init__(self, act_dim: int, device: str):
        rclpy.init()
        self.node = rclpy.create_node("galbot_reach_sim")
        self.pub = self.node.create_publisher(Float32MultiArray, "/galbot/reach/obs", QOS)
        self.node.create_subscription(Float32MultiArray, "/galbot/reach/action", self._on_action, QOS)
        self.inbox = {}
        self.step = 0
        self.timeouts = 0
        self.latency = []  # 每步"发出观测到收到动作"的墙上时间
        self.last = torch.zeros(1, act_dim, device=device)
        self.device = device

    def _on_action(self, msg):
        self.inbox[int(msg.data[0])] = list(msg.data[1:])

    def wait_for_peer(self, timeout: float = 60.0) -> None:
        t0 = time.monotonic()
        while self.pub.get_subscription_count() == 0:
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if time.monotonic() - t0 > timeout:
                raise RuntimeError("60 s 内没有策略节点订阅 /galbot/reach/obs，请先启动 ros2/reach_policy_node.py")

    def __call__(self, obs: torch.Tensor) -> torch.Tensor:
        k = self.step
        msg = Float32MultiArray()
        msg.data = [float(k)] + obs[0].tolist()
        t0 = time.monotonic()
        self.pub.publish(msg)
        while k not in self.inbox and time.monotonic() - t0 < args.timeout:
            rclpy.spin_once(self.node, timeout_sec=args.timeout)
        if k in self.inbox:
            self.latency.append(time.monotonic() - t0)
            self.last = torch.tensor([self.inbox.pop(k)], device=self.device)
        else:
            self.timeouts += 1  # 没收到：保持上一步动作
        self.step += 1
        return self.last

    def close(self):
        self.node.destroy_node()
        rclpy.try_shutdown()


def main() -> None:
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=1)
    env_cfg.seed = args.seed
    env = RslRlVecEnvWrapper(gym.make(args.task, cfg=env_cfg))  # 与 eval_reach 相同：观测是 TensorDict
    base = env.unwrapped
    robot = base.scene["robot"]
    arm = [i for i, n in enumerate(robot.joint_names) if n.startswith("right_arm_joint")]
    cmd = base.command_manager.get_term("ee_pose")
    seg = round(cmd.cfg.resampling_time_range[0] / base.step_dt)
    T = int(base.max_episode_length)
    act_dim = base.action_manager.total_action_dim

    torch_policy = None
    if args.checkpoint:
        from rsl_rl.runners import OnPolicyRunner

        agent_cfg = load_cfg_from_registry(args.task, "rsl_rl_cfg_entry_point")
        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
        runner.load(args.checkpoint)
        torch_policy = runner.get_inference_policy(device=base.device)
    if args.mode == "inproc":
        assert torch_policy is not None, "--mode inproc 需要 --checkpoint"
        policy = torch_policy
    else:
        ros = Ros2Policy(act_dim, base.device)
        ros.wait_for_peer()
        policy = lambda o: ros(o["policy"])  # noqa: E731  只把 28 维观测发出去
    queue = collections.deque()  # --delay 用：先进先出，第 k 步执行第 k-delay 步的动作
    held = torch.zeros(1, act_dim, device=base.device)

    obs = env.get_observations()
    pos_err, rot_err, max_diff = [], [], 0.0
    win = round(0.5 / base.step_dt)
    stuck = 0
    t_start = time.monotonic()
    with torch.inference_mode():
        for ep in range(args.episodes):
            q_hist = []
            for k in range(T):  # 第 T 步（k = T-1）触发超时重置，在它之前读误差，与 eval_reach 相同
                a = policy(obs)
                if torch_policy is not None and args.mode == "ros2":
                    max_diff = max(max_diff, (a - torch_policy(obs)).abs().max().item())
                queue.append(a)
                if len(queue) > args.delay:
                    held = queue.popleft()
                obs, _, _, _ = env.step(held)
                if k == T - 1:
                    break
                q_hist = (q_hist + [robot.data.joint_pos[:, arm].clone()])[-win:]
                if (k + 1) % seg == 0 or k == T - 2:
                    pe, re = cmd.metrics["position_error"].clone(), cmd.metrics["orientation_error"].clone()
                    moved = (q_hist[-1] - q_hist[0]).abs().max(dim=1).values
                    pos_err.append(pe)
                    rot_err.append(re)
                    stuck += int(((pe > 0.05) & (moved < 0.01)).sum())
            if (ep + 1) % 16 == 0:
                print(f"  {ep + 1}/{args.episodes} 回合，墙上 {time.monotonic() - t_start:.0f} s", flush=True)
    wall = time.monotonic() - t_start
    pe, re = torch.cat(pos_err), torch.cat(rot_err)
    n = len(pe)
    print(f"mode={args.mode} delay={args.delay} seed={args.seed}：{args.episodes} 回合 × 3 段 = {n} 个样本，墙上 {wall:.0f} s")
    print(f"  位置误差：中位数 {pe.median().item() * 100:.2f} cm，90% 分位 {pe.quantile(0.9).item() * 100:.2f} cm，"
          f"< 2 cm {(pe < 0.02).float().mean().item() * 100:.1f}%，< 5 cm {(pe < 0.05).float().mean().item() * 100:.1f}%")
    print(f"  位置误差：均值 {pe.mean().item() * 100:.2f} cm，最大 {pe.max().item() * 100:.2f} cm")
    print(f"  姿态误差：中位数 {re.median().item():.3f} rad，90% 分位 {re.quantile(0.9).item():.3f} rad")
    print(f"  停住但没到：{stuck} / {n}")
    if args.mode == "ros2":
        lat = torch.tensor(ros.latency) * 1000
        print(f"  往返延迟（发观测→收动作）：中位数 {lat.median().item():.2f} ms，99% 分位 {lat.quantile(0.99).item():.2f} ms，"
              f"超时 {ros.timeouts} 次 / {ros.step} 步")
        if torch_policy is not None:
            print(f"  外部节点动作与进程内 torch 策略的最大差：{max_diff:.2e}")
        ros.close()
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
