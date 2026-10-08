# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
"""Galbot 单臂 reach（6.4.1）：右臂 TCP 到达随机采样的目标位置，并保持一个固定的姿态。

结构照 Isaac Lab 的 Isaac-Reach-Franka-v0（manipulation/reach/reach_env_cfg.py）写，改动处都有注释。
"""

from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.utils import configclass

from galbot_academy.assets.galbot import REACH_ARM, REACH_EE_BODY, REACH_EE_OFFSET_POS, REACH_EE_OFFSET_ROT
from galbot_academy.scenes.reach import GalbotReachSceneCfg

from . import mdp

ARM_JOINTS = f"{REACH_ARM}_arm_joint[1-7]"
ARM = SceneEntityCfg("robot", joint_names=[ARM_JOINTS])  # 观测、惩罚、重置都只针对右臂（6.1.5：夹爪指节的静止速度读数大）
EE = SceneEntityCfg("robot", body_names=[REACH_EE_BODY])
TCP = {"offset_pos": REACH_EE_OFFSET_POS, "offset_rot": REACH_EE_OFFSET_ROT}

# 目标姿态：默认姿态下 TCP 的姿态（相对机器人根的 roll / pitch / yaw，rad），由 URDF 正运动学算得（6.4.1）
TARGET_RPY = (-1.3754, 0.0617, 0.7876)


@configclass
class CommandsCfg:
    # 位置范围（相对根）：在 6.2.1 的可达范围建议内收窄。6.2.1 只看位置；加上固定姿态后，原范围只有约 60% 的目标
    # 能用逆运动学达到，收窄后为 99%（scripts/check_reach_targets.py，6.4.1）。姿态固定为 TARGET_RPY
    ee_pose = mdp.TcpPoseCommandCfg(
        asset_name="robot",
        body_name=REACH_EE_BODY,
        **TCP,
        resampling_time_range=(4.0, 4.0),
        debug_vis=True,
        ranges=mdp.TcpPoseCommandCfg.Ranges(
            pos_x=(0.30, 0.60),
            pos_y=(-0.40, -0.15),
            pos_z=(1.15, 1.50),
            roll=(TARGET_RPY[0], TARGET_RPY[0]),
            pitch=(TARGET_RPY[1], TARGET_RPY[1]),
            yaw=(TARGET_RPY[2], TARGET_RPY[2]),
        ),
    )


@configclass
class ActionsCfg:
    # 右臂 7 个关节的位置目标 = 默认位置 + 0.5 × 动作（同 Franka）；其余关节不受策略控制，保持默认目标
    arm_action = mdp.JointPositionActionCfg(asset_name="robot", joint_names=[ARM_JOINTS], scale=0.5, use_default_offset=True)


@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        # 与 Franka 相同的四项，但关节量只取右臂，且先不加噪声
        joint_pos = ObsTerm(func=mdp.joint_pos_rel, params={"asset_cfg": ARM})
        joint_vel = ObsTerm(func=mdp.joint_vel_rel, params={"asset_cfg": ARM})
        pose_command = ObsTerm(func=mdp.generated_commands, params={"command_name": "ee_pose"})
        actions = ObsTerm(func=mdp.last_action)

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class EventCfg:
    # 先把整台机器人（关节状态与关节目标）恢复到默认姿态：下面的扰动只写右臂，其余关节若不复位，
    # 会停在 USD 的零位，而零位不是默认姿态（6.4.1 实测：腿偏离 2.3 rad）。同一 mode 的事件按声明顺序执行。
    reset_to_default = EventTerm(func=mdp.reset_scene_to_default, mode="reset", params={"reset_joint_targets": True})
    # 只扰动右臂：默认位置 ± 0.2 rad（Franka 用的是按比例缩放全部关节；Galbot 的腿若被缩放会撑不住，6.1.6）
    reset_robot_joints = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={"position_range": (-0.2, 0.2), "velocity_range": (0.0, 0.0), "asset_cfg": ARM},
    )


@configclass
class RewardsCfg:
    # 权重照搬 Franka：两者的控制周期都是 1/30 s，奖励按 权重 × 函数值 × 控制周期 累加，量级可比
    end_effector_position_tracking = RewTerm(
        func=mdp.tcp_position_error, weight=-0.2, params={"asset_cfg": EE, "command_name": "ee_pose", **TCP}
    )
    end_effector_position_tracking_fine_grained = RewTerm(
        func=mdp.tcp_position_error_tanh, weight=0.1, params={"asset_cfg": EE, "std": 0.1, "command_name": "ee_pose", **TCP}
    )
    end_effector_orientation_tracking = RewTerm(
        func=mdp.tcp_orientation_error, weight=-0.1, params={"asset_cfg": EE, "command_name": "ee_pose", **TCP}
    )
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.0001)
    joint_vel = RewTerm(func=mdp.joint_vel_l2, weight=-0.0001, params={"asset_cfg": ARM})  # 只罚右臂（6.1.5）


@configclass
class TerminationsCfg:
    # reach 没有失败条件，只有超时
    time_out = DoneTerm(func=mdp.time_out, time_out=True)


@configclass
class CurriculumCfg:
    # 4500 个控制步后加大动作变化率与关节速度的惩罚。动作变化率只升到 -0.001（Franka 是 -0.005）：
    # 6.5.1 的对照中，-0.005 时训练后段越来越多的回合"停在离目标几厘米处"，去掉又会让部分种子停不稳
    action_rate = CurrTerm(func=mdp.modify_reward_weight, params={"term_name": "action_rate", "weight": -0.001, "num_steps": 4500})
    joint_vel = CurrTerm(func=mdp.modify_reward_weight, params={"term_name": "joint_vel", "weight": -0.001, "num_steps": 4500})


@configclass
class GalbotReachEnvCfg(ManagerBasedRLEnvCfg):
    scene: GalbotReachSceneCfg = GalbotReachSceneCfg(num_envs=1024, env_spacing=2.5)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self):
        # 时间：物理步 1/120 s，每 4 个物理步一次控制（30 Hz，与 Franka 的 1/60 × 2 相同）；dt 取小是为了压低静止速度偏置（6.1.5）
        self.sim.dt = 1 / 120
        self.decimation = 4
        self.sim.render_interval = self.decimation
        self.episode_length_s = 12.0  # 360 个控制步，期间目标每 4 s 重采样一次
        self.viewer.eye = (3.5, 3.5, 3.5)
        # 任务级的执行器覆盖（6.5.1）：右臂刚度 / 阻尼由资产参数表的 400 / 40 提到 1600 / 80，
        # 重力下垂缩小到约 1/4（6.1.5 表 3），否则策略常停在离目标约 5 cm 处。资产参数表本身不改（drives.py）。
        self.scene.robot.actuators["arms"].stiffness = 1600.0
        self.scene.robot.actuators["arms"].damping = 80.0


@configclass
class GalbotReachEnvCfg_PLAY(GalbotReachEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 16
