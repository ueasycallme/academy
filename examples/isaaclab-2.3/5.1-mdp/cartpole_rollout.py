# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""用随机动作跑官方 Cartpole，逐步打印 env 0 的观测、动作、奖励与结束标志，并算出第一个回合的回报。

用法::

    python cartpole_rollout.py --headless
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Cartpole 的一次 rollout")
parser.add_argument("--num_envs", type=int, default=4, help="环境数量")
parser.add_argument("--gamma", type=float, default=0.99, help="折扣因子（官方 Cartpole 的 RSL-RL 配置为 0.99）")
parser.add_argument("--seed", type=int, default=42, help="随机种子")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

from isaaclab.envs import ManagerBasedRLEnv
from isaaclab_tasks.manager_based.classic.cartpole.cartpole_env_cfg import CartpoleEnvCfg


def main() -> None:
    cfg = CartpoleEnvCfg()
    cfg.scene.num_envs = args.num_envs
    cfg.seed = args.seed
    env = ManagerBasedRLEnv(cfg=cfg)
    torch.manual_seed(args.seed)

    obs, _ = env.reset()
    print(f"观测形状 {tuple(obs['policy'].shape)}（环境数 × 观测维度），step_dt {env.step_dt:.4f} s，回合上限 {env.max_episode_length} 步")
    print("env 0 的观测依次为：小车位置、摆杆角度、小车速度、摆杆角速度（相对默认值）")
    print(" 步 | 动作   | 奖励    | 失败  | 超时  | 这一步之后的观测")

    rewards_env0 = []
    for step in range(1, 400):
        action = 2.0 * torch.rand(env.num_envs, 1, device=env.device) - 1.0
        obs, rew, terminated, truncated, _ = env.step(action)
        rewards_env0.append(rew[0].item())
        done = bool(terminated[0] or truncated[0])
        if step <= 5 or done:
            o = "  ".join(f"{v:+.3f}" for v in obs["policy"][0].tolist())
            print(f"{step:3d} | {action[0, 0].item():+.3f} | {rew[0].item():+.4f} | {bool(terminated[0])!s:5} | {bool(truncated[0])!s:5} | {o}")
        if done:
            break
        if step == 5:
            print("... |")

    ret = sum(r * args.gamma**k for k, r in enumerate(rewards_env0))
    print(f"env 0 的第一个回合共 {len(rewards_env0)} 步：奖励之和 {sum(rewards_env0):+.4f}，折扣回报（γ={args.gamma}）{ret:+.4f}")
    print("最后一行的观测已是新回合的初始观测：超时的环境在同一次 step() 里被重置")
    print(f"奖励张量形状 {tuple(rew.shape)}，失败标志形状 {tuple(terminated.shape)}")

    env.close()  # 环境的 close() 会释放 SimulationContext


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
