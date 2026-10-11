# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-11
"""Galbot 单臂 reach 的 Direct 版：Galbot-Reach-Direct-v0（6.4.4），与 Galbot-Reach-v0 语义等价。"""

import gymnasium as gym

from . import agents

gym.register(
    id="Galbot-Reach-Direct-v0",
    entry_point=f"{__name__}.reach_env:GalbotReachDirectEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.reach_env_cfg:GalbotReachDirectEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:GalbotReachDirectPPORunnerCfg",
    },
)
