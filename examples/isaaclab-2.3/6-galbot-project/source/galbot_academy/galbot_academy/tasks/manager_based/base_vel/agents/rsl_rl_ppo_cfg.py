# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-11
"""底盘速度跟踪的 PPO 配置（6.4.5）：沿用 reach（6.5.1）的配置，只改实验名与迭代数。"""

from isaaclab.utils import configclass

from galbot_academy.tasks.manager_based.reach.agents.rsl_rl_ppo_cfg import GalbotReachPPORunnerCfg


@configclass
class GalbotBaseVelPPORunnerCfg(GalbotReachPPORunnerCfg):
    experiment_name = "galbot_base_vel"
    max_iterations = 500
