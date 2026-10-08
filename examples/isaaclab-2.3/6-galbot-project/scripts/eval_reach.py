# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""评估一个 reach 策略（6.5.1）：跑一个完整回合，在每段目标（4 s）的最后一步记录 TCP 误差。

报告位置误差的中位数、90% 分位、小于 2 cm / 5 cm 的比例，姿态误差的中位数；
并统计"停住但没到"的样本：误差大于 5 cm、而最后 0.5 s 内右臂几乎没动的（用位置变化判断，不用速度读数，见 6.1.5）。

    python scripts/eval_reach.py --headless --checkpoint logs/rsl_rl/galbot_reach/<运行>/model_999.pt
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="评估 reach 策略")
parser.add_argument("--task", default="Galbot-Reach-Play-v0")
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--num_envs", type=int, default=256)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--action_scale", type=float, default=None, help="训练时改过动作 scale 的，评估时要用同一个值（6.5.2）")
parser.add_argument("--vel_limit", type=float, default=None, help="评估时把右臂关节速度上限改为该值（rad/s，诊断用）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch
from rsl_rl.runners import OnPolicyRunner

import isaaclab_tasks  # noqa: F401
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from isaaclab_tasks.utils import load_cfg_from_registry, parse_env_cfg

import galbot_academy.tasks  # noqa: F401


def main() -> None:
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    env_cfg.seed = args.seed
    if args.action_scale is not None:
        env_cfg.actions.arm_action.scale = args.action_scale
    agent_cfg = load_cfg_from_registry(args.task, "rsl_rl_cfg_entry_point")
    env = RslRlVecEnvWrapper(gym.make(args.task, cfg=env_cfg))
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    runner.load(args.checkpoint)
    policy = runner.get_inference_policy(device=env.unwrapped.device)

    base = env.unwrapped
    robot = base.scene["robot"]
    arm = [i for i, n in enumerate(robot.joint_names) if n.startswith("right_arm_joint")]
    arm = arm or list(range(robot.num_joints))  # 其他机器人（如官方 Franka 对照）：看全部关节
    cmd = base.command_manager.get_term("ee_pose")
    seg = round(cmd.cfg.resampling_time_range[0] / base.step_dt)  # 每段目标的控制步数
    T = int(base.max_episode_length)

    if args.vel_limit is not None:
        lim = robot.data.joint_vel_limits.clone()
        lim[:, arm] = args.vel_limit
        robot.write_joint_velocity_limit_to_sim(lim)
    win = round(0.5 / base.step_dt)  # 每段最后 0.5 s：用位置变化判断手臂是否还在动（速度读数有静止偏置，见 6.1.5）
    q_hist = []
    obs = env.get_observations()
    pos_err, rot_err, stuck = [], [], 0
    with torch.inference_mode():
        for k in range(T - 1):  # 最后一步会触发超时重置，在它之前读
            obs, _, _, _ = env.step(policy(obs))
            q_hist = (q_hist + [robot.data.joint_pos[:, arm].clone()])[-win:]
            if (k + 1) % seg == 0 or k == T - 2:
                pe, re = cmd.metrics["position_error"].clone(), cmd.metrics["orientation_error"].clone()
                moved = (q_hist[-1] - q_hist[0]).abs().max(dim=1).values  # 最后 0.5 s 内关节位置的最大变化
                pos_err.append(pe)
                rot_err.append(re)
                stuck += int(((pe > 0.05) & (moved < 0.01)).sum())
    pe, re = torch.cat(pos_err), torch.cat(rot_err)
    n = len(pe)
    print(f"{args.checkpoint}：{args.num_envs} 个环境 × {n // args.num_envs} 段目标 = {n} 个样本（每段末尾）")
    print(f"  位置误差：中位数 {pe.median().item() * 100:.2f} cm，90% 分位 {pe.quantile(0.9).item() * 100:.2f} cm，"
          f"< 2 cm {(pe < 0.02).float().mean().item() * 100:.1f}%，< 5 cm {(pe < 0.05).float().mean().item() * 100:.1f}%")
    print(f"  姿态误差：中位数 {re.median().item():.3f} rad，90% 分位 {re.quantile(0.9).item():.3f} rad")
    print(f"  误差 > 5 cm 且最后 0.5 s 内右臂关节位置变化 < 0.01 rad 的样本（停住但没到）：{stuck} / {n}")
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
