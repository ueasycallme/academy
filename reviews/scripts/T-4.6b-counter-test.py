# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""探针：第一次 env.reset() 时，reset 事件随机出的关节速度被夹成 0。

官方 Cartpole 的 reset 事件用 reset_joints_by_offset 给关节位置与速度加随机偏移，速度会按
data.soft_joint_vel_limits 夹紧；而这个缓冲在第一次 write_data_to_sim() 之前全是 0。
脚本在几个时刻打印速度上限与 env 0 的观测，对比第一次 reset、第 1 步之后、step 内重置、第二次 reset。

用法::

    python first_reset_velocity.py --headless
    python first_reset_velocity.py --headless --device cpu
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="第一次 reset 的关节速度")
parser.add_argument("--seed", type=int, default=42, help="随机种子")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

from isaaclab.envs import ManagerBasedRLEnv
from isaaclab_tasks.manager_based.classic.cartpole.cartpole_env_cfg import CartpoleEnvCfg


def main() -> None:
    cfg = CartpoleEnvCfg()
    cfg.scene.num_envs = 2
    cfg.seed = args.seed
    cfg.sim.device = args.device
    env = ManagerBasedRLEnv(cfg=cfg)
    robot = env.scene["robot"]
    zero = torch.zeros(env.num_envs, 1, device=env.device)

    def row(tag: str, obs: dict) -> None:
        lim = [round(v, 1) for v in robot.data.soft_joint_vel_limits[0].tolist()]
        pos = [round(v, 3) for v in obs["policy"][0, :2].tolist()]
        vel = [round(v, 3) for v in obs["policy"][0, 2:].tolist()]
        print(f"  {tag:16s} | 速度上限 {lim} | 位置 {pos} | 速度 {vel}")

    print(f"device {env.device}；速度上限即 data.soft_joint_vel_limits（小车、摆杆），位置与速度取自 env 0 的观测")
    print(f"  {'构造完成后':16s} | 速度上限 {robot.data.soft_joint_vel_limits[0].tolist()}")
    env.scene.write_data_to_sim()  # counter-test: fill soft_joint_vel_limits before first reset
    print("  填充后速度上限", robot.data.soft_joint_vel_limits[0].tolist())
    obs, _ = env.reset()
    row("第一次 reset()", obs)
    obs, *_ = env.step(zero)
    row("第 1 步之后", obs)
    env.episode_length_buf[:] = env.max_episode_length - 1  # 下一步所有环境超时，在 step 内重置
    obs, _, _, truncated, _ = env.step(zero)
    row(f"step 内重置（超时 {int(truncated.sum())} 个）", obs)
    obs, _ = env.reset()
    row("第二次 reset()", obs)

    env.close()  # 环境的 close() 会释放 SimulationContext


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
