# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
"""演示用的任务包：导入本包时注册两个任务 ID。正式项目的结构见 4.18。"""

import gymnasium as gym

gym.register(
    id="Academy-Cartpole-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.cartpole_cfg:AcademyCartpoleEnvCfg",
        # 训练参数直接沿用官方 Cartpole 的 RSL-RL 配置
        "rsl_rl_cfg_entry_point": "isaaclab_tasks.manager_based.classic.cartpole.agents.rsl_rl_ppo_cfg:CartpolePPORunnerCfg",
    },
)

gym.register(
    id="Academy-Cartpole-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.cartpole_cfg:AcademyCartpoleEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": "isaaclab_tasks.manager_based.classic.cartpole.agents.rsl_rl_ppo_cfg:CartpolePPORunnerCfg",
    },
)
