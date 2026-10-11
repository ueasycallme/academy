# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
"""pick-place 的 Mimic 配置（6.4.6 定义，6.4.7 调参）：两段子任务。

- 第 1 段"抓"：以方块为参考，到子任务信号 grasp 为止；
- 第 2 段"放"：以放置点为参考，到示范结束。
生成参数照官方 Franka / Galbot stack 的取值（4.19 表 2），只有 action_noise 按本项目的动作尺度改小（6.4.7）。
"""

from isaaclab.envs.mimic_env_cfg import MimicEnvCfg, SubTaskConfig
from isaaclab.utils import configclass

from .pick_place_env_cfg import GalbotPickPlaceEnvCfg

EEF_NAME = "galbot_right"


@configclass
class GalbotPickPlaceMimicEnvCfg(GalbotPickPlaceEnvCfg, MimicEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        dg = self.datagen_config
        dg.name = "galbot_pick_place"
        dg.generation_guarantee = True
        dg.generation_keep_failed = True
        dg.generation_num_trials = 10
        dg.generation_select_src_per_subtask = True
        dg.generation_transform_first_robot_pose = False
        dg.generation_interpolate_from_last_target_pose = True
        dg.max_num_failures = 25
        dg.seed = 1
        common = dict(
            selection_strategy="nearest_neighbor_object",
            selection_strategy_kwargs={"nn_k": 3},
            # 动作噪声（每轴标准差）。官方 Franka 取 0.03，但本项目示教每步只走 1 cm，0.03 让噪声（每步约 5 cm）
            # 盖过动作本身，生成 490 次尝试 0 次成功（6.4.7 坑）。取示教步长的一半
            action_noise=0.005,
            num_interpolation_steps=5,
            num_fixed_steps=0,
            apply_noise_during_interpolation=False,
        )
        self.subtask_configs[EEF_NAME] = [
            SubTaskConfig(
                object_ref="object",
                subtask_term_signal="grasp",
                subtask_term_offset_range=(10, 20),
                description="抓起方块",
                next_subtask_description="把方块放到绿色方垫上",
                **common,
            ),
            SubTaskConfig(object_ref="target", subtask_term_signal=None, subtask_term_offset_range=(0, 0), **common),
        ]
