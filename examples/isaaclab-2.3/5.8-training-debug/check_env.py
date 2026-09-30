# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""训练前的环境自检：随机动作运行若干步，逐步检查观测与奖励有无 NaN / Inf，
最后打印各观测组、奖励的范围与形状，以及各终止原因的次数。

用法::

    python check_env.py --headless --task Isaac-Cartpole-v0
    python check_env.py --headless --task Isaac-Reach-Franka-v0 --steps 300
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="训练前的环境自检")
parser.add_argument("--task", default="Isaac-Cartpole-v0", help="任务 ID")
parser.add_argument("--num_envs", type=int, default=16, help="环境数量")
parser.add_argument("--steps", type=int, default=200, help="运行的环境步数")
parser.add_argument("--seed", type=int, default=42, help="随机种子")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg


def main() -> None:
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    env_cfg.seed = args.seed
    env = gym.make(args.task, cfg=env_cfg)
    base = env.unwrapped
    torch.manual_seed(args.seed)

    obs, _ = env.reset()
    lo = {k: v.min(dim=0).values.clone() for k, v in obs.items()}
    hi = {k: v.max(dim=0).values.clone() for k, v in obs.items()}
    rew_lo, rew_hi, done_counts = float("inf"), -float("inf"), {}
    for step in range(1, args.steps + 1):
        actions = 2.0 * torch.rand(env.action_space.shape, device=base.device) - 1.0
        obs, rew, terminated, truncated, _ = env.step(actions)
        # 逐步检查 NaN / Inf：第一次出现时报告步数与环境编号
        for name, t in list(obs.items()) + [("reward", rew.unsqueeze(-1))]:
            bad = ~torch.isfinite(t)
            if bad.any():
                env_ids = bad.any(dim=-1).nonzero().flatten().tolist()
                print(f"第 {step} 步 {name} 出现 NaN/Inf，环境 {env_ids[:8]}")
                env.close()
                return
        for k, v in obs.items():
            lo[k] = torch.minimum(lo[k], v.min(dim=0).values)
            hi[k] = torch.maximum(hi[k], v.max(dim=0).values)
        rew_lo, rew_hi = min(rew_lo, rew.min().item()), max(rew_hi, rew.max().item())
        for name in base.termination_manager.active_terms:
            done_counts[name] = done_counts.get(name, 0) + int(base.termination_manager.get_term(name).sum())

    print(f"{args.task}：{args.steps} 步随机动作，未出现 NaN/Inf")
    for k in obs:
        print(f"  观测组 {k} 形状 {tuple(obs[k].shape)}")
        print(f"    各维最小值 {[round(x, 2) for x in lo[k].tolist()]}")
        print(f"    各维最大值 {[round(x, 2) for x in hi[k].tolist()]}")
    print(f"  每步奖励范围 [{rew_lo:.4f}, {rew_hi:.4f}]（已乘 step_dt = {base.step_dt:.4f}）")
    print(f"  各终止项触发次数（所有环境合计）：{done_counts}")
    env.close()  # 环境的 close() 会释放 SimulationContext


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
