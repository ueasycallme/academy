# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-11
"""Galbot 单臂 reach 的 Direct 版配置（6.4.4）。

与 Manager-based 版（tasks/manager_based/reach/reach_env_cfg.py）逐项对应：那边的每个管理器配置，在这里变成几个普通字段，
逻辑写在 reach_env.py。数值全部取自 Manager 版，改一边要同步改另一边。
"""

from isaaclab.envs import DirectRLEnvCfg
from isaaclab.sim import SimulationCfg
from isaaclab.utils import configclass

from galbot_academy.scenes.reach import GalbotReachSceneCfg
from galbot_academy.tasks.manager_based.reach.reach_env_cfg import TARGET_RPY


@configclass
class GalbotReachDirectEnvCfg(DirectRLEnvCfg):
    # 时间与场景：同 Manager 版的 __post_init__（物理步 1/120 s × 4 = 30 Hz 控制，回合 12 s）
    decimation = 4
    episode_length_s = 12.0
    sim: SimulationCfg = SimulationCfg(dt=1 / 120, render_interval=4)
    scene: GalbotReachSceneCfg = GalbotReachSceneCfg(num_envs=1024, env_spacing=2.5)

    # 空间：动作 7 维（右臂关节）；观测 28 维 = 关节位置 7 + 关节速度 7 + 目标位姿 7 + 上一步动作 7
    action_space = 7
    observation_space = 28
    state_space = 0

    # 动作（ActionsCfg）：关节位置目标 = 默认位置 + action_scale × 动作
    action_scale = 0.5

    # 命令（CommandsCfg）：目标位置在根坐标系里均匀采样，姿态固定；每 4 s 重采样
    resampling_time_range = (4.0, 4.0)
    pos_x = (0.30, 0.60)
    pos_y = (-0.40, -0.15)
    pos_z = (1.15, 1.50)
    target_rpy = TARGET_RPY

    # 重置（EventCfg）：整机回默认姿态后，右臂关节位置加 ±0.2 rad 的均匀扰动
    reset_position_range = (-0.2, 0.2)

    # 奖励（RewardsCfg）：权重 × 函数值 × 控制周期
    rew_position = -0.2
    rew_position_fine = 0.1
    rew_position_fine_std = 0.1
    rew_orientation = -0.1
    rew_action_rate = -0.0001
    rew_joint_vel = -0.0001

    # 课程（CurriculumCfg）：全局控制步数超过 4500 后，在重置时把两项惩罚加大
    curriculum_steps = 4500
    rew_action_rate_final = -0.001
    rew_joint_vel_final = -0.001

    def __post_init__(self):
        self.viewer.eye = (3.5, 3.5, 3.5)
        # 任务级的执行器覆盖，同 Manager 版（6.5.1）：右臂刚度 / 阻尼 1600 / 80
        self.scene.robot.actuators["arms"].stiffness = 1600.0
        self.scene.robot.actuators["arms"].damping = 80.0
