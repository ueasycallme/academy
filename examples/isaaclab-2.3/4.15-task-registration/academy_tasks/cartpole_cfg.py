# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
"""Academy-Cartpole 的环境配置：继承官方 Cartpole，只改一处。"""

from isaaclab.utils import configclass
from isaaclab_tasks.manager_based.classic.cartpole.cartpole_env_cfg import CartpoleEnvCfg


@configclass
class AcademyCartpoleEnvCfg(CartpoleEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.rewards.pole_pos.weight = -2.0  # 唯一的改动：加大摆杆偏离的惩罚


@configclass
class AcademyCartpoleEnvCfg_PLAY(AcademyCartpoleEnvCfg):
    """回放用：环境少、间距小，其余与训练配置相同。"""

    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 16
        self.scene.env_spacing = 2.5
