# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-11
"""轮式 Galbot 的底盘速度跟踪：Galbot-BaseVel-v0（6.4.5）。"""

import gymnasium as gym

from . import agents

gym.register(
    id="Galbot-BaseVel-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.base_vel_env_cfg:GalbotBaseVelEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:GalbotBaseVelPPORunnerCfg",
    },
)
