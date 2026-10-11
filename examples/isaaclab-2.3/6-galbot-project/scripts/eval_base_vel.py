# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""评估底盘速度跟踪策略（6.4.5，口径同 6.6.2）：固定几组指令，每组 --num_envs 个回合。

每组：reset 后给定一个固定指令（底盘坐标系），跑 --seconds 秒；在末 --window 秒内，按环境平均底盘的实际速度，
算线速度误差 ‖v_xy − v_cmd‖ 与角速度误差 |wz − wz_cmd|。报中位数、90% 分位，以及"成功"比例：
线速度误差 < 0.1 m/s 且角速度误差 < 0.2 rad/s（即本页的目标门槛，逐回合判断）。
另外记录全程（所有组、所有步）主动轮速度目标与施加力矩的最大绝对值，用来判断执行器上限有没有被碰到。

    python scripts/eval_base_vel.py --headless --checkpoint logs/rsl_rl/galbot_base_vel/<运行>/model_499.pt
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="评估底盘速度跟踪（6.4.5）")
parser.add_argument("--task", default="Galbot-BaseVel-v0")
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--num_envs", type=int, default=64)
parser.add_argument("--seconds", type=float, default=4.0)
parser.add_argument("--window", type=float, default=2.0)
parser.add_argument("--seed", type=int, default=0)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym  # noqa: E402
import torch  # noqa: E402
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper  # noqa: E402
from isaaclab_tasks.utils import load_cfg_from_registry, parse_env_cfg  # noqa: E402

import galbot_academy.tasks  # noqa: E402, F401
from galbot_academy.assets.omni_base import WHEEL_JOINTS  # noqa: E402

SCENARIOS = {  # 名称 → (vx, vy, wz)，底盘坐标系
    "直行 0.5 m/s": (0.5, 0.0, 0.0),
    "侧移 0.5 m/s": (0.0, 0.5, 0.0),
    "原地转 0.5 rad/s": (0.0, 0.0, 0.5),
    "组合": (0.3, 0.3, 0.3),
}
LIN_OK, ANG_OK = 0.1, 0.2


def main() -> None:
    cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    cfg.seed = args.seed
    cfg.commands.base_velocity.rel_standing_envs = 0.0
    cfg.commands.base_velocity.resampling_time_range = (1.0e6, 1.0e6)  # 一个回合内不换指令
    cfg.episode_length_s = args.seconds + 1.0
    agent = load_cfg_from_registry(args.task, "rsl_rl_cfg_entry_point")
    env = RslRlVecEnvWrapper(gym.make(args.task, cfg=cfg))
    runner = OnPolicyRunner(env, agent.to_dict(), log_dir=None, device=agent.device)
    runner.load(args.checkpoint)
    policy = runner.get_inference_policy(device=env.unwrapped.device)
    base = env.unwrapped
    ranges = base.command_manager.get_term("base_velocity").cfg.ranges
    robot = base.scene["robot"]
    steps, win = round(args.seconds / base.step_dt), round(args.window / base.step_dt)
    wheel_ids = robot.find_joints(WHEEL_JOINTS, preserve_order=True)[0]
    all_lin, all_ang = [], []
    max_target, max_torque = 0.0, 0.0
    with torch.inference_mode():
        for name, (vx, vy, wz) in SCENARIOS.items():
            ranges.lin_vel_x, ranges.lin_vel_y, ranges.ang_vel_z = (vx, vx), (vy, vy), (wz, wz)
            obs, _ = env.reset()  # 重置时按新范围重采样指令
            acc = torch.zeros(args.num_envs, 3, device=base.device)
            for k in range(steps):
                obs, _, _, _ = env.step(policy(obs))
                max_target = max(max_target, robot.data.joint_vel_target[:, wheel_ids].abs().max().item())
                max_torque = max(max_torque, robot.data.applied_torque[:, wheel_ids].abs().max().item())
                if k >= steps - win:
                    acc += torch.cat([robot.data.root_lin_vel_b[:, :2], robot.data.root_ang_vel_b[:, 2:3]], dim=1) / win
            cmd = torch.tensor([vx, vy, wz], device=base.device)
            lin = (acc[:, :2] - cmd[:2]).norm(dim=1)
            ang = (acc[:, 2] - cmd[2]).abs()
            ok = ((lin < LIN_OK) & (ang < ANG_OK)).float().mean().item()
            all_lin.append(lin)
            all_ang.append(ang)
            print(f"[6.4.5] {name}：实际均值 vx {acc[:, 0].mean():.3f}、vy {acc[:, 1].mean():.3f} m/s、wz {acc[:, 2].mean():.3f} rad/s；"
                  f"线速度误差 中位 {lin.median():.3f}、90% {lin.quantile(0.9):.3f} m/s；角速度误差 中位 {ang.median():.3f}、"
                  f"90% {ang.quantile(0.9):.3f} rad/s；成功 {ok * 100:.1f}%（{args.num_envs} 回合）", flush=True)
    lin, ang = torch.cat(all_lin), torch.cat(all_ang)
    print(f"[6.4.5] 合计 {len(lin)} 回合：线速度误差 中位 {lin.median():.3f} m/s，角速度误差 中位 {ang.median():.3f} rad/s；"
          f"成功 {((lin < LIN_OK) & (ang < ANG_OK)).float().mean().item() * 100:.1f}%", flush=True)
    limits = (robot.data.joint_vel_limits[0, wheel_ids].max().item(), robot.data.joint_effort_limits[0, wheel_ids].max().item())
    print(f"[6.4.5] 主动轮全程最大：速度目标 {max_target:.2f} rad/s，施加力矩 {max_torque:.2f} N·m（上限 {limits[0]:.4g} rad/s、{limits[1]:.4g} N·m）", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
