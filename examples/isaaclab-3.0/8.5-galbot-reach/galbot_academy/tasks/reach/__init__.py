# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""Galbot 单臂 reach（3.0 EA 版，8.5）：Galbot-Reach 与 Galbot-Reach-Play。3.0 的任务名不带 -v0；
2.3 项目里的域随机化变体（Galbot-Reach-DR-v0）子集不带。"""

import gymnasium as gym

from . import agents

_RSL_RL = f"{agents.__name__}.rsl_rl_ppo_cfg:GalbotReachPPORunnerCfg"  # 6.5.1

gym.register(
    id="Galbot-Reach",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.reach_env_cfg:GalbotReachEnvCfg", "rsl_rl_cfg_entry_point": _RSL_RL},
)

gym.register(
    id="Galbot-Reach-Play",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.reach_env_cfg:GalbotReachEnvCfg_PLAY", "rsl_rl_cfg_entry_point": _RSL_RL},
)

# 6.4.2：加域随机化（rsl_rl 入口在 6.5.2 加入，用于有无域随机化的对照训练）
