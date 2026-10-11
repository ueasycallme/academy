# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；robomimic 0.4.0
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""评估 BC 策略并给失败分类（6.4.7）：回合循环与官方 robomimic/play.py 相同，另外记下每个回合走到了哪一步。

play.py 只打印每个回合成功与否。这里在同样的循环里逐步读观测，按"最远到达的阶段"把回合分成四类：
没抓住（grasp 信号从未出现）、抓住了但没送到（方块从未进入放置垫中心 3 cm 内）、送到了但没放成（进入过但 success 未满足）、成功。
种子、回合上限、每回合重新加载检查点都照 play.py，所以结果可以和 play.py 逐回合对照：本站实测前 30 回合的成败与 play.py 的前 30 回合逐个相同（6.4.7 表 3）。

    python scripts/eval_bc_pick_place.py --headless --checkpoint <model_epoch_N.pth> --num_rollouts 20
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="评估 pick-place 的 BC 策略并给失败分类")
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--num_rollouts", type=int, default=20)
parser.add_argument("--horizon", type=int, default=900)
parser.add_argument("--seed", type=int, default=101)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import copy
import random
from collections import Counter

import gymnasium as gym
import numpy as np
import robomimic.utils.file_utils as FileUtils
import robomimic.utils.torch_utils as TorchUtils
import torch

import galbot_academy.tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

TASK = "Galbot-PickPlace-IK-Rel-v0"
XY_TOL = 0.03  # 与成功判定的 PLACE_XY_TOL 相同
LIFT = 0.03  # 方块比起始高 3 cm 算"举起来了"
STAGES = ["没抓住", "抓住了但没送到", "送到了但没放成", "成功"]


def rollout(policy, env, success_term, horizon, device):
    """与 play.py 的 rollout 相同，另返回 (最远阶段, 步数, 结束原因, 是否举起过)。"""
    policy.start_episode()
    obs_dict, _ = env.reset()
    z0 = obs_dict["policy"]["object_position"][0, 2].item()
    stage, lifted = 0, False
    for i in range(horizon):
        obs = copy.deepcopy(obs_dict["policy"])
        for ob in obs:
            obs[ob] = torch.squeeze(obs[ob])
        actions = policy(obs)
        actions = torch.from_numpy(actions).to(device=device).view(1, env.action_space.shape[1])
        obs_dict, _, terminated, truncated, _ = env.step(actions)
        p = obs_dict["policy"]
        if bool(obs_dict["subtask_terms"]["grasp"][0]):
            stage = max(stage, 1)
        if p["object_position"][0, 2].item() > z0 + LIFT:
            lifted = True
        if stage >= 1 and torch.linalg.norm(p["object_position"][0, :2] - p["target_position"][0, :2]).item() <= XY_TOL:
            stage = max(stage, 2)
        if bool(success_term.func(env, **success_term.params)[0]):
            return 3, i + 1, "成功", lifted
        if terminated or truncated:
            return stage, i + 1, "方块掉落", lifted
    return stage, horizon, "到回合上限", lifted


def main() -> None:
    env_cfg = parse_env_cfg(TASK, device=args.device, num_envs=1)
    env_cfg.observations.policy.concatenate_terms = False
    env_cfg.terminations.time_out = None
    env_cfg.recorders = None
    success_term = env_cfg.terminations.success
    env_cfg.terminations.success = None
    env = gym.make(TASK, cfg=env_cfg).unwrapped
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    env.seed(args.seed)
    device = TorchUtils.get_torch_device(try_to_use_cuda=True)
    rows = []
    for trial in range(args.num_rollouts):
        policy, _ = FileUtils.policy_from_checkpoint(ckpt_path=args.checkpoint, device=device)
        stage, steps, end, lifted = rollout(policy, env, success_term, args.horizon, device)
        rows.append((stage, end))
        print(f"[eval] 回合 {trial}：{STAGES[stage]}，{steps} 步，{end}，举起过={lifted}", flush=True)
    print(f"[eval] 成功 {sum(s == 3 for s, _ in rows)} / {len(rows)}", flush=True)
    for (stage, end), n in sorted(Counter(rows).items()):
        print(f"[eval]   {STAGES[stage]}（{end}）：{n}", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
