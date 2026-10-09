# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
"""Galbot 单臂 reach：Galbot-Reach-v0（6.4.1）与加域随机化的 Galbot-Reach-DR-v0（6.4.2）。rsl_rl 的配置入口在 6.5.1 加入。"""

import gymnasium as gym

from . import agents

_RSL_RL = f"{agents.__name__}.rsl_rl_ppo_cfg:GalbotReachPPORunnerCfg"  # 6.5.1

gym.register(
    id="Galbot-Reach-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.reach_env_cfg:GalbotReachEnvCfg", "rsl_rl_cfg_entry_point": _RSL_RL},
)

gym.register(
    id="Galbot-Reach-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.reach_env_cfg:GalbotReachEnvCfg_PLAY", "rsl_rl_cfg_entry_point": _RSL_RL},
)

# 6.4.2：加域随机化（rsl_rl 入口在 6.5.2 加入，用于有无域随机化的对照训练）
gym.register(
    id="Galbot-Reach-DR-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.reach_dr_env_cfg:GalbotReachDREnvCfg", "rsl_rl_cfg_entry_point": _RSL_RL},
)

gym.register(
    id="Galbot-Reach-DR-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.reach_dr_env_cfg:GalbotReachDREnvCfg_PLAY", "rsl_rl_cfg_entry_point": _RSL_RL},
)
