# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-09
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""Galbot 单臂 lift：Galbot-Lift-v0 与回放用的 Galbot-Lift-Play-v0（6.4.3）。"""

import gymnasium as gym

from . import agents

_RSL_RL = f"{agents.__name__}.rsl_rl_ppo_cfg:GalbotLiftPPORunnerCfg"

gym.register(
    id="Galbot-Lift-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.lift_env_cfg:GalbotLiftEnvCfg", "rsl_rl_cfg_entry_point": _RSL_RL},
)

gym.register(
    id="Galbot-Lift-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.lift_env_cfg:GalbotLiftEnvCfg_PLAY", "rsl_rl_cfg_entry_point": _RSL_RL},
)
