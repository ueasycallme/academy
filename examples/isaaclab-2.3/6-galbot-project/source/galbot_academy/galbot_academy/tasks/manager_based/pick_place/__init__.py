# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-11（6.4.6）；robomimic 配置入口：未验证（6.4.7）
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""Galbot 单臂 pick-place（6.4.6）：录示范用的 Galbot-PickPlace-IK-Rel-v0，Mimic 用的 Galbot-PickPlace-IK-Rel-Mimic-v0。

命名照官方风格（Isaac-Stack-Cube-Franka-IK-Rel-v0 / -Mimic-v0）：动作是 IK 相对动作。
"""

import gymnasium as gym

from . import agents

# robomimic 的 BC-RNN 配置（6.4.7）：由官方 Franka stack 的 bc_rnn_low_dim.json 改了实验名与观测键。
# 观测不用 1 维的 gripper_pos：robomimic/play.py 对每项观测做 torch.squeeze，(1, 1) 会被压成标量，
# 网络的形状检查报 AssertionError（6.4.7 坑）；夹爪位置改由 joint_pos 的最后一维提供
_BC = f"{agents.__name__}:robomimic/bc_rnn_low_dim.json"

gym.register(
    id="Galbot-PickPlace-IK-Rel-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.pick_place_env_cfg:GalbotPickPlaceEnvCfg", "robomimic_bc_cfg_entry_point": _BC},
)

gym.register(
    id="Galbot-PickPlace-IK-Rel-Mimic-v0",
    entry_point=f"{__name__}.mimic_env:GalbotPickPlaceMimicEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.mimic_env_cfg:GalbotPickPlaceMimicEnvCfg", "robomimic_bc_cfg_entry_point": _BC},
)
