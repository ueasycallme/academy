# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab 3.0.0（v3.0.0 tag，commit e3f7d9ff1）+ Isaac Sim 6.2.0（pip）
# 验证日期：2026-10-23
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04
"""注册一个外部任务 Academy-Cartpole-Direct。环境类与配置直接复用 Isaac Lab 自带的 Cartpole（Direct），只换任务名。

与 2.3 的写法相同，仍是 gym.register；区别只在怎么让 `isaaclab` 命令导入这个模块（见 __init__.py）。
"""

import gymnasium as gym

_CARTPOLE = "isaaclab_tasks.core.cartpole"

gym.register(
    id="Academy-Cartpole-Direct",
    entry_point=f"{_CARTPOLE}.cartpole_direct_env:CartpoleEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{_CARTPOLE}.cartpole_direct_env_cfg:CartpoleEnvCfg",
        "rsl_rl_cfg_entry_point": f"{_CARTPOLE}.agents.rsl_rl_ppo_cfg:CartpoleDirectPPORunnerCfg",
        # 不给 --rl_library 时，train / play 用这一项选 RL 库（dispatch.py 的 _resolve_default_library）
        "default_agent": "rsl_rl",
    },
)
