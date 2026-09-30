# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""从任务 ID 到环境对象：查注册表 → 解析配置 → gym.make → 看 step 五元组的类型与形状。

用法::

    python run_task.py --headless                                  # 导入 academy_tasks 后运行 Academy-Cartpole-v0
    python run_task.py --headless --task Academy-Cartpole-Play-v0  # Play 变体
    python run_task.py --headless --no_import                      # 不导入 academy_tasks，看会发生什么
"""

import argparse
import os
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="任务注册演示")
parser.add_argument("--task", default="Academy-Cartpole-v0", help="任务 ID")
parser.add_argument("--num_envs", type=int, default=None, help="覆盖环境数量，默认用配置里的值")
parser.add_argument("--no_import", action="store_true", help="不导入 academy_tasks")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch

import isaaclab_tasks  # noqa: F401  注册官方任务
from isaaclab_tasks.utils import parse_env_cfg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # 让 academy_tasks 可被导入
if not args.no_import:
    import academy_tasks  # noqa: F401  注册 Academy-* 任务


def describe(x) -> str:
    if isinstance(x, torch.Tensor):
        return f"Tensor{tuple(x.shape)} {x.dtype} {x.device}"
    if isinstance(x, dict):
        return "{" + ", ".join(f"{k}: {describe(v)}" for k, v in x.items()) + "}"
    return type(x).__name__


def main() -> None:
    task_id = args.task.split(":")[-1]
    print(f"注册表中有 {task_id}：{task_id in gym.registry}")
    try:
        env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    except Exception as e:  # 演示找不到任务时的报错
        print(f"parse_env_cfg 失败：{type(e).__name__}: {e}")
        return
    print(f"配置类 {type(env_cfg).__module__}.{type(env_cfg).__name__}，num_envs {env_cfg.scene.num_envs}，"
          f"pole_pos 权重 {env_cfg.rewards.pole_pos.weight}")
    if env_cfg.scene.num_envs > 1024:  # 官方默认 4096；本站示例控制在 1024 以内
        env_cfg.scene.num_envs = 64
        print("num_envs 改为 64 运行")

    env = gym.make(args.task, cfg=env_cfg)
    print(f"gym.make 返回 {type(env).__name__}，env.unwrapped 是 {type(env.unwrapped).__name__}")
    print(f"action_space {env.action_space.shape}，single_action_space {env.unwrapped.single_action_space.shape}")
    print(f"observation_space['policy'] {env.observation_space['policy'].shape}")

    env.reset(seed=42)
    actions = 2.0 * torch.rand(env.action_space.shape, device=env.unwrapped.device) - 1.0
    obs, rew, terminated, truncated, extras = env.step(actions)
    print("step 返回：")
    for name, value in [("obs", obs), ("rew", rew), ("terminated", terminated), ("truncated", truncated), ("extras", extras)]:
        print(f"  {name:10s} {describe(value)}")

    env.close()  # 环境的 close() 会释放 SimulationContext


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
