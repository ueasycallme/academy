# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""测 Cartpole 两种写法（manager-based 与 direct）在相同环境数下每秒的环境步数（headless，随机动作）。

用法::

    python bench_cartpole.py --headless --task Isaac-Cartpole-v0
    python bench_cartpole.py --headless --task Isaac-Cartpole-Direct-v0
"""

import argparse
import sys
import time

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Cartpole 两种写法的步进速度")
parser.add_argument("--task", default="Isaac-Cartpole-v0", help="任务 ID")
parser.add_argument("--num_envs", type=int, default=1024, help="环境数量")
parser.add_argument("--steps", type=int, default=1000, help="计时的环境步数")
parser.add_argument("--warmup", type=int, default=100, help="计时前先跑的步数")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch

import isaaclab_tasks  # noqa: F401  注册任务 ID
from isaaclab_tasks.utils import parse_env_cfg


def main() -> None:
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    env_cfg.seed = 42
    env = gym.make(args.task, cfg=env_cfg)
    unwrapped = env.unwrapped
    print(f"{args.task}：{type(unwrapped).__name__}，num_envs {unwrapped.num_envs}，step_dt {unwrapped.step_dt:.5f} s")

    env.reset()
    action_dim = gym.spaces.flatdim(unwrapped.single_action_space)

    def run(n: int) -> None:
        for _ in range(n):
            actions = 2.0 * torch.rand(unwrapped.num_envs, action_dim, device=unwrapped.device) - 1.0
            env.step(actions)

    run(args.warmup)
    torch.cuda.synchronize()
    start = time.perf_counter()
    run(args.steps)
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    print(f"{args.steps} 步用时 {elapsed:.2f} s：{args.steps / elapsed:.0f} step/s，"
          f"{args.steps * unwrapped.num_envs / elapsed:,.0f} 环境步/s")

    env.close()  # 环境的 close() 会释放 SimulationContext


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
