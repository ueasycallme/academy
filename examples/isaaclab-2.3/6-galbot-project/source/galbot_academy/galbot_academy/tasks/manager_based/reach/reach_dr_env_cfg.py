# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
"""Galbot reach + 域随机化（6.4.2）。在 GalbotReachEnvCfg（6.4.1）上加事件与观测噪声，其余不变。

没有真机数据（D-004）：所有范围都是以标称值为中心的保守比例，属于经验性取值。
"""

from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils import configclass
from isaaclab.utils.noise import AdditiveUniformNoiseCfg as Unoise

from . import mdp
from .reach_env_cfg import ARM, EventCfg, GalbotReachEnvCfg

ARM_LINKS = SceneEntityCfg("robot", body_names=["right_arm_link[1-7]"])


@configclass
class DREventCfg(EventCfg):
    # ---- startup：只在环境创建时执行一次。这几项写的是物理参数，函数本身建议只在初始化时用（CPU 张量） ----
    # 右臂连杆质量 ×[0.9, 1.1]，按均匀密度重算惯量
    arm_mass = EventTerm(
        func=mdp.randomize_rigid_body_mass,
        mode="startup",
        params={"asset_cfg": ARM_LINKS, "mass_distribution_params": (0.9, 1.1), "operation": "scale", "recompute_inertia": True},
    )
    # 右臂驱动刚度、阻尼 ×[0.8, 1.2]（标称 400 / 40，6.1.5）
    arm_gains = EventTerm(
        func=mdp.randomize_actuator_gains,
        mode="startup",
        params={"asset_cfg": ARM, "stiffness_distribution_params": (0.8, 1.2), "damping_distribution_params": (0.8, 1.2),
                "operation": "scale"},
    )
    # 右臂关节 armature 加 [0, 0.005] kg·m²：标称为 0，按比例缩放无效，所以用加法
    arm_armature = EventTerm(
        func=mdp.randomize_joint_parameters,
        mode="startup",
        params={"asset_cfg": ARM, "armature_distribution_params": (0.0, 0.005), "operation": "add"},
    )

    def __post_init__(self):
        # 初始关节：位置偏移沿用 6.4.1 的 ±0.2 rad，再加 ±0.1 rad/s 的初速度
        self.reset_robot_joints.params["velocity_range"] = (-0.1, 0.1)


@configclass
class GalbotReachDREnvCfg(GalbotReachEnvCfg):
    events: DREventCfg = DREventCfg()

    def __post_init__(self):
        super().__post_init__()
        # 观测噪声：与 Franka reach 相同，右臂关节位置与速度各加 ±0.01 的均匀噪声
        self.observations.policy.enable_corruption = True
        self.observations.policy.joint_pos.noise = Unoise(n_min=-0.01, n_max=0.01)
        self.observations.policy.joint_vel.noise = Unoise(n_min=-0.01, n_max=0.01)


@configclass
class GalbotReachDREnvCfg_PLAY(GalbotReachDREnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 16
        # 回放：关掉观测噪声与物理参数的随机化，看策略在标称模型上的表现；初始姿态的扰动保留
        self.observations.policy.enable_corruption = False
        self.events.arm_mass = None
        self.events.arm_gains = None
        self.events.arm_armature = None
