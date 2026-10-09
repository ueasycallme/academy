# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-09
"""Galbot 单臂 lift（6.4.3）：右手抓起桌上的方块，举到随机采样的目标位置。

结构照 Isaac Lab 的 Isaac-Lift-Cube-Franka-v0 写（manipulation/lift/lift_env_cfg.py 的 LiftEnvCfg +
config/franka/joint_pos_env_cfg.py 的 FrankaCubeLiftEnvCfg），改动处都有注释。
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

from galbot_academy.assets.galbot import REACH_ARM, REACH_EE_BODY
from galbot_academy.scenes.lift import CUBE_REST_Z, GalbotLiftSceneCfg

from . import mdp

ARM_JOINTS = f"{REACH_ARM}_arm_joint[1-7]"
GRIPPER_JOINT = f"{REACH_ARM}_gripper_joint"  # 夹爪唯一的主动关节，其余 5 个指节由 mimic 约束跟随（6.1.2、6.1.6）
ARM = SceneEntityCfg("robot", joint_names=[ARM_JOINTS])
# 观测里的关节：右臂 7 个 + 夹爪主动关节。不取 mimic 指节：它们的速度读数在静止时也有噪声本底（6.1.5、6.4.1 坑）
ARM_GRIPPER = SceneEntityCfg("robot", joint_names=[ARM_JOINTS, GRIPPER_JOINT], preserve_order=True)

# 夹爪的两个目标角。URDF 里这个关节的速度上限只有 0.5 rad/s，从完全张开（0）合到夹住 5 cm 方块要 2.8 s，
# 5 s 的回合里太慢；"张开"只张到 0.6 rad（两指尖相距 10.6 cm，方块两侧各留约 2.8 cm），夹到方块缩短为 1.6 s
# （scripts/check_grasp.py 实测，6.4.3）。
GRIPPER_OPEN = 0.6  # rad
GRIPPER_CLOSED = 1.703  # rad，URDF 上限，完全闭合；夹住方块时指尖停在方块两侧，由驱动的刚度产生夹持力

LIFT_HEIGHT = 0.04  # "举起"的判据：方块中心高出静止高度 4 cm。官方 minimal_height = 0.04 是世界坐标，折合约高出静止高度 2 cm（mdp/rewards.py）
REST = {"rest_z": CUBE_REST_Z}
# 夹爪门控（6.4.3 第 5 组）：举起与跟踪目标两项奖励只在夹爪"真的合上了"时计分。前 4 组的策略在举起期间
# 77–85% 的时间夹爪是张开的，靠张开的手指把方块挑起来拿分，随后方块被带离桌面掉落。
# 阈值：主动关节位置 ≥ 1.0 rad。由 check_grasp 的指尖几何测得 q = 1.0 时两指尖刚体相距约 7.3 cm（指垫间约 6.5 cm），
# 只比 5 cm 的方块宽 1.5 cm；夹住方块时实测停在约 1.69 rad，张开时为 0.6 rad。用测得的位置而不是指令（rewards.py）
GRASP_GATE = {"gripper_cfg": SceneEntityCfg("robot", joint_names=[GRIPPER_JOINT]), "gripper_min_q": 1.0}


@configclass
class CommandsCfg:
    # 方块的目标位置（相对机器人根）。官方：x 0.4–0.6、y ±0.25、z 0.25–0.5（桌面在 0）；
    # 这里放在右臂工作空间里、桌面上方 0.10–0.30 m（6.2.1 的可达范围）。姿态不要求（与官方相同，奖励只看位置）
    object_pose = mdp.UniformPoseCommandCfg(
        asset_name="robot",
        body_name=REACH_EE_BODY,
        resampling_time_range=(5.0, 5.0),
        debug_vis=True,
        ranges=mdp.UniformPoseCommandCfg.Ranges(
            pos_x=(0.45, 0.60),
            pos_y=(-0.35, -0.15),
            pos_z=(CUBE_REST_Z + 0.10, CUBE_REST_Z + 0.30),
            roll=(0.0, 0.0),
            pitch=(0.0, 0.0),
            yaw=(0.0, 0.0),
        ),
    )


@configclass
class ActionsCfg:
    # 右臂：与 reach 相同；夹爪：二值动作（动作 < 0 闭合，否则张开），官方 Franka 也是这样
    arm_action = mdp.JointPositionActionCfg(asset_name="robot", joint_names=[ARM_JOINTS], scale=0.5, use_default_offset=True)
    gripper_action = mdp.BinaryJointPositionActionCfg(
        asset_name="robot",
        joint_names=[GRIPPER_JOINT],
        open_command_expr={GRIPPER_JOINT: GRIPPER_OPEN},
        close_command_expr={GRIPPER_JOINT: GRIPPER_CLOSED},
    )


@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        # 与官方相同的五项；关节量只取右臂 + 夹爪主动关节（官方取全部 9 个关节），先不加噪声
        joint_pos = ObsTerm(func=mdp.joint_pos_rel, params={"asset_cfg": ARM_GRIPPER})
        joint_vel = ObsTerm(func=mdp.joint_vel_rel, params={"asset_cfg": ARM_GRIPPER})
        object_position = ObsTerm(func=mdp.object_position_in_robot_root_frame)
        target_object_position = ObsTerm(func=mdp.generated_commands, params={"command_name": "object_pose"})
        actions = ObsTerm(func=mdp.last_action)

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class EventCfg:
    # 整台机器人恢复默认姿态（6.4.1 坑：只写右臂时其余关节会停在 USD 零位），夹爪随之张开
    reset_all = EventTerm(func=mdp.reset_scene_to_default, mode="reset", params={"reset_joint_targets": True})
    # 方块在初始位置（桌面中心）附近随机放置（官方 x ±0.1、y ±0.25；这里桌面更小、只用右臂，收窄为 x ±0.05、y ±0.08）
    reset_object_position = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-0.05, 0.05), "y": (-0.08, 0.08), "z": (0.0, 0.0)},
            "velocity_range": {},
            "asset_cfg": SceneEntityCfg("object"),
        },
    )


@configclass
class RewardsCfg:
    # 四项分阶段奖励与权重照搬官方；"举起"改为相对桌面（mdp/rewards.py），举起与跟踪目标加夹爪门控（GRASP_GATE）
    reaching_object = RewTerm(func=mdp.object_ee_distance, params={"std": 0.1}, weight=1.0)
    lifting_object = RewTerm(func=mdp.object_is_lifted, params={"minimal_height": LIFT_HEIGHT, **REST, **GRASP_GATE}, weight=15.0)
    object_goal_tracking = RewTerm(
        func=mdp.object_goal_distance,
        params={"std": 0.3, "minimal_height": LIFT_HEIGHT, "command_name": "object_pose", **REST, **GRASP_GATE},
        weight=16.0,
    )
    object_goal_tracking_fine_grained = RewTerm(
        func=mdp.object_goal_distance,
        params={"std": 0.05, "minimal_height": LIFT_HEIGHT, "command_name": "object_pose", **REST, **GRASP_GATE},
        weight=5.0,
    )
    # 抓取塑形（6.4.3 第 6 组）：只加门控时（第 5 组），合拢之前没有任何中间奖励，策略始终没发现"在方块旁合拢、
    # 等约 1.6 s 再抬"这一串动作，举起奖励为 0。这一项给"在方块旁边合拢"稠密的奖励，权重与 reaching 同量级；
    # std 取 0.05（reaching 用 0.1），离方块较远时合拢几乎不得分，免得学成"一路握拳伸过去"
    grasp_shaping = RewTerm(
        func=mdp.grasp_closure_near_object,
        params={"std": 0.05, "open_q": GRIPPER_OPEN, "closed_q": GRIPPER_CLOSED, "gripper_cfg": GRASP_GATE["gripper_cfg"]},
        weight=1.0,
    )
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-1e-4)
    joint_vel = RewTerm(func=mdp.joint_vel_l2, weight=-1e-4, params={"asset_cfg": ARM})  # 只罚右臂（官方罚全部关节）
    # 掉落惩罚（官方没有）：方块掉下桌面会终止回合。若终止本身不扣分，课程把惩罚加大以后，"把方块推下桌、
    # 提前结束回合"反而比继续挨罚划算——6.4.3 的基线训练就学成了这样。终止也是奖励设计的一部分
    object_dropping = RewTerm(func=mdp.is_terminated_term, weight=-10.0, params={"term_keys": "object_dropping"})


@configclass
class TerminationsCfg:
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    # 方块掉下桌面（低于静止高度 5 cm）。官方 minimum_height=-0.05 是世界坐标，见 mdp/terminations.py
    object_dropping = DoneTerm(func=mdp.object_dropped, params={"drop_height": 0.05, **REST})


@configclass
class CurriculumCfg:
    # 10000 个控制步后加大两项惩罚。官方加到 -0.1；6.4.3 的训练中，这么大的惩罚让"提前结束回合"（方块掉下桌）
    # 比继续举着更划算，掉落率随之升到八九成。这里与 reach（6.4.1）一样只加到 -0.001，时间点保持官方的 10000 步
    action_rate = CurrTerm(func=mdp.modify_reward_weight, params={"term_name": "action_rate", "weight": -1e-3, "num_steps": 10000})
    joint_vel = CurrTerm(func=mdp.modify_reward_weight, params={"term_name": "joint_vel", "weight": -1e-3, "num_steps": 10000})


@configclass
class GalbotLiftEnvCfg(ManagerBasedRLEnvCfg):
    scene: GalbotLiftSceneCfg = GalbotLiftSceneCfg(num_envs=1024, env_spacing=2.5)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self):
        # 时间：沿用 reach 的 1/120 s × 4（30 Hz 控制）；官方是 1/100 s × 2（50 Hz）
        self.sim.dt = 1 / 120
        self.decimation = 4
        self.sim.render_interval = self.decimation
        self.episode_length_s = 5.0  # 同官方
        self.viewer.eye = (3.5, 3.5, 3.5)
        # PhysX 设置照搬官方 lift
        self.sim.physx.bounce_threshold_velocity = 0.01
        self.sim.physx.gpu_found_lost_aggregate_pairs_capacity = 1024 * 1024 * 4
        self.sim.physx.gpu_total_aggregate_pairs_capacity = 16 * 1024
        self.sim.physx.friction_correlation_distance = 0.00625
        # 右臂执行器：与 reach 相同的任务级覆盖（6.5.1）
        self.scene.robot.actuators["arms"].stiffness = 1600.0
        self.scene.robot.actuators["arms"].damping = 80.0


@configclass
class GalbotLiftEnvCfg_PLAY(GalbotLiftEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 16
