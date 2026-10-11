# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-11
"""Direct 版 reach 的 PPO 配置（6.4.4）：与 Manager 版（6.5.1）完全相同，只改实验名，日志分开存放。"""

from isaaclab.utils import configclass

from galbot_academy.tasks.manager_based.reach.agents.rsl_rl_ppo_cfg import GalbotReachPPORunnerCfg


@configclass
class GalbotReachDirectPPORunnerCfg(GalbotReachPPORunnerCfg):
    experiment_name = "galbot_reach_direct"
