# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
"""Galbot 单臂 pick-place（6.4.6）：右手把桌上的方块拿起来，放到桌面上的绿色方垫上。

在 lift（6.4.3）的场景上加一个放置点；动作换成遥操作用的 IK 相对动作 + 二值夹爪（4.20）；
观测不拼接，按名字给出末端位姿等量，供录制与 Mimic（4.19）使用。没有奖励：这个环境用来录示范、生成数据，不做 RL。
"""

import isaaclab.sim as sim_utils
from isaaclab.assets import RigidObjectCfg
from isaaclab.controllers.differential_ik_cfg import DifferentialIKControllerCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.utils import configclass

from galbot_academy.assets.galbot import REACH_ARM, REACH_EE_BODY, REACH_EE_OFFSET_POS, REACH_EE_OFFSET_ROT
from galbot_academy.scenes.lift import CUBE_REST_Z, CUBE_SIZE, TABLE_TOP_Z, GalbotLiftSceneCfg

from ..lift.lift_env_cfg import GRIPPER_CLOSED, GRIPPER_OPEN
from . import mdp

ARM_JOINTS = f"{REACH_ARM}_arm_joint[1-7]"
GRIPPER_JOINT = f"{REACH_ARM}_gripper_joint"
GRIPPER = SceneEntityCfg("robot", joint_names=[GRIPPER_JOINT])
ARM_GRIPPER = SceneEntityCfg("robot", joint_names=[ARM_JOINTS, GRIPPER_JOINT], preserve_order=True)

# 放置点：桌面上 8 cm × 8 cm 的绿色薄垫，中心在根坐标系 (0.62, -0.45)，每次重置在 x ±0.03、y ±0.04 内随机。
# 方块在 (0.65, -0.25) 附近（6.4.3），两者中心相距约 0.2 m，取放之间要移动、但都在右臂的范围内（6.2.1 表 1）
TARGET_XY = (0.62, -0.45)
TARGET_SIZE = 0.08
# 成功判定的容差：方块中心落在放置垫中心 3 cm 内（垫子半宽 4 cm，方块半宽 2.5 cm）、高度与静止时相差 1 cm 内
PLACE_XY_TOL = 0.03
PLACE_Z_TOL = 0.01
# "抓住了"：夹爪测量位置 ≥ 1.0 rad（与 6.4.3 的门控阈值相同）且方块中心离 TCP ≤ 3 cm
GRASP_MIN_Q = 1.0
GRASP_MAX_DIST = 0.03
# "松开了"：夹爪测量位置 ≤ 0.8 rad（张开目标 0.6），TCP 离方块中心 ≥ 6 cm
RELEASE_MAX_Q = 0.8
RELEASE_MIN_DIST = 0.06


@configclass
class GalbotPickPlaceSceneCfg(GalbotLiftSceneCfg):
    """lift 的场景（地面、灯光、机器人、桌面、方块、末端坐标系）加一个放置点。"""

    # 放置点做成运动学刚体、关闭碰撞：不参与物理，只用来显示，并让 Mimic 能用 get_object_poses 读到它的位姿（4.19）
    target = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Target",
        init_state=RigidObjectCfg.InitialStateCfg(pos=(*TARGET_XY, TABLE_TOP_Z + 0.001)),
        spawn=sim_utils.CuboidCfg(
            size=(TARGET_SIZE, TARGET_SIZE, 0.002),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(kinematic_enabled=True, disable_gravity=True),
            collision_props=sim_utils.CollisionPropertiesCfg(collision_enabled=False),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.2, 0.7, 0.2)),
        ),
    )


@configclass
class ActionsCfg:
    # 右臂：微分 IK，相对模式（每步给 TCP 的位置增量 + 轴角增量，根坐标系，4.20"从设备到动作"）。
    # 跟踪的点就是 ee_frame 的 TCP（right_arm_link7 + 固定偏移，6.2.1）。scale 取 1.0 而不是官方 Franka 的 0.5：
    # Mimic 的 target_eef_pose_to_action / action_to_target_eef_pose 把动作当作"目标 − 当前"本身（mimic_env.py），
    # 缩放不为 1 时两者与动作项实际执行的增量差一个倍数。
    # 动作项类用 mdp/actions.py 的修正版：Isaac Lab 2.3.2 原版在偏移带旋转时把雅可比的转动部分改错，姿态控制发散（6.4.6 坑一）
    arm_action = mdp.OffsetCorrectedDiffIKActionCfg(
        asset_name="robot",
        joint_names=[ARM_JOINTS],
        body_name=REACH_EE_BODY,
        controller=DifferentialIKControllerCfg(command_type="pose", use_relative_mode=True, ik_method="dls"),
        scale=1.0,
        body_offset=mdp.OffsetCorrectedDiffIKActionCfg.OffsetCfg(pos=REACH_EE_OFFSET_POS, rot=REACH_EE_OFFSET_ROT),
    )
    # 夹爪：与 lift 相同的二值动作（< 0 闭合，否则张开）
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
        actions = ObsTerm(func=mdp.last_action)
        joint_pos = ObsTerm(func=mdp.joint_pos_rel, params={"asset_cfg": ARM_GRIPPER})
        joint_vel = ObsTerm(func=mdp.joint_vel_rel, params={"asset_cfg": ARM_GRIPPER})
        object_position = ObsTerm(func=mdp.object_position_in_robot_root_frame)
        target_position = ObsTerm(func=mdp.target_position_in_robot_root_frame)
        eef_pos = ObsTerm(func=mdp.ee_pos)
        eef_quat = ObsTerm(func=mdp.ee_quat)
        gripper_pos = ObsTerm(func=mdp.gripper_q, params={"gripper_cfg": GRIPPER})

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = False  # 按名字取：Mimic 的 get_robot_eef_pose 读 eef_pos / eef_quat

    @configclass
    class SubtaskCfg(ObsGroup):
        """Mimic 的子任务完成信号（4.19）：只有"抓住了"一个；第二段"放下"到示范结束为止。"""

        grasp = ObsTerm(
            func=mdp.object_grasped,
            params={"gripper_cfg": GRIPPER, "min_q": GRASP_MIN_Q, "max_dist": GRASP_MAX_DIST},
        )

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = False

    policy: PolicyCfg = PolicyCfg()
    subtask_terms: SubtaskCfg = SubtaskCfg()


@configclass
class EventCfg:
    reset_all = EventTerm(func=mdp.reset_scene_to_default, mode="reset", params={"reset_joint_targets": True})
    # 方块：与 lift 相同，桌面中心附近 x ±0.05、y ±0.08
    reset_object_position = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-0.05, 0.05), "y": (-0.08, 0.08), "z": (0.0, 0.0)},
            "velocity_range": {},
            "asset_cfg": SceneEntityCfg("object"),
        },
    )
    reset_target_position = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-0.03, 0.03), "y": (-0.04, 0.04), "z": (0.0, 0.0)},
            "velocity_range": {},
            "asset_cfg": SceneEntityCfg("target"),
        },
    )


@configclass
class TerminationsCfg:
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    object_dropping = DoneTerm(func=mdp.object_dropped, params={"drop_height": 0.05, "rest_z": CUBE_REST_Z})
    # record_demos.py 与 Mimic 都按名字找 success 项（4.20 坑三）
    success = DoneTerm(
        func=mdp.object_placed,
        params={
            "gripper_cfg": GRIPPER,
            "max_open_q": RELEASE_MAX_Q,
            "xy_tol": PLACE_XY_TOL,
            "rest_z": CUBE_REST_Z,
            "z_tol": PLACE_Z_TOL,
            "min_release_dist": RELEASE_MIN_DIST,
        },
    )


@configclass
class GalbotPickPlaceEnvCfg(ManagerBasedRLEnvCfg):
    scene: GalbotPickPlaceSceneCfg = GalbotPickPlaceSceneCfg(num_envs=1, env_spacing=2.5)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()
    rewards = None
    commands = None

    def __post_init__(self):
        # 时间与 lift 相同：1/120 s × 4（30 Hz 控制）；一条示范通常十几秒，回合上限给足 30 s
        self.sim.dt = 1 / 120
        self.decimation = 4
        self.sim.render_interval = self.decimation
        self.episode_length_s = 30.0
        self.viewer.eye = (2.0, -1.5, 2.0)
        self.viewer.lookat = (0.6, -0.3, 1.0)
        self.sim.physx.bounce_threshold_velocity = 0.01
        self.sim.physx.friction_correlation_distance = 0.00625
        # 右臂执行器：与 reach / lift 相同的任务级覆盖（6.5.1）；IK 跟踪靠关节位置驱动，刚度低了跟不上
        self.scene.robot.actuators["arms"].stiffness = 1600.0
        self.scene.robot.actuators["arms"].damping = 80.0
        # 机器人关掉重力，与官方 IK 任务的 FRANKA_PANDA_HIGH_PD_CFG 一样（spawn.rigid_props.disable_gravity = True）。
        # IK 相对动作每步只把目标放在当前位置前方约 1 cm，关节 PD 在重力下的下垂把这 1 cm 吃掉，手臂向上走不动（6.4.6 坑二）。
        # 只关机器人的重力，方块不受影响
        # GALBOT_ONE_GOLF_CFG 没有设 rigid_props（为 None），这里新建一份，只写 disable_gravity
        self.scene.robot.spawn.rigid_props = sim_utils.RigidBodyPropertiesCfg(disable_gravity=True)


__all__ = [
    "GalbotPickPlaceEnvCfg",
    "GalbotPickPlaceSceneCfg",
    "CUBE_SIZE",
    "GRIPPER_OPEN",
    "GRIPPER_CLOSED",
    "GRASP_MIN_Q",
    "RELEASE_MAX_Q",
]
