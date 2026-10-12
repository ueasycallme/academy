# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
"""轮式 Galbot 的底盘速度跟踪（6.4.5）：给定底盘坐标系下的 (vx, vy, wz) 指令，策略输出 4 个主动轮的速度目标。

结构照 Isaac Lab 的速度跟踪任务（locomotion/velocity）写，只保留轮式底盘用得到的项。两臂与腿由执行器保持默认姿态，不受策略控制。
"""

import math

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.envs import mdp
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass

from galbot_academy.assets.galbot import GALBOT_ONE_GOLF_WHEELED_CFG
from galbot_academy.assets.omni_base import WHEEL_JOINTS

WHEELS = SceneEntityCfg("robot", joint_names=WHEEL_JOINTS, preserve_order=True)
MAX_WHEEL_SPEED = 6.0  # rad/s：动作 [-1, 1] 映射到 ±6 rad/s；0.6 m/s 直行约需 4.1 rad/s（omni_base.body_to_wheel）


@configclass
class BaseVelSceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(prim_path="/World/ground", spawn=sim_utils.GroundPlaneCfg())
    light = AssetBaseCfg(prim_path="/World/light", spawn=sim_utils.DomeLightCfg(intensity=2000.0))
    robot: ArticulationCfg = GALBOT_ONE_GOLF_WHEELED_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")


@configclass
class CommandsCfg:
    # 底盘坐标系下的速度指令，每 4 s 重采样；10% 的环境给零指令（原地停住也要会）
    base_velocity = mdp.UniformVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(4.0, 4.0),
        rel_standing_envs=0.1,
        heading_command=False,
        debug_vis=False,
        ranges=mdp.UniformVelocityCommandCfg.Ranges(lin_vel_x=(-0.6, 0.6), lin_vel_y=(-0.6, 0.6), ang_vel_z=(-0.6, 0.6)),
    )


@configclass
class ActionsCfg:
    # 4 个主动轮的速度目标 = MAX_WHEEL_SPEED × 动作，再限幅到 ±MAX_WHEEL_SPEED。
    # clip 作用在缩放之后（joint_actions.py L173–L178），单位是 rad/s；写成 (-1, 1) 会把轮速限在 ±1 rad/s（6.4.5 坑）
    wheel_action = mdp.JointVelocityActionCfg(
        asset_name="robot", joint_names=WHEEL_JOINTS, preserve_order=True, scale=MAX_WHEEL_SPEED,
        clip={".*": (-MAX_WHEEL_SPEED, MAX_WHEEL_SPEED)},
    )


@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        # 速度都在底盘（根）坐标系下，与指令同一个坐标系（坑三）
        base_lin_vel = ObsTerm(func=mdp.base_lin_vel)
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
        projected_gravity = ObsTerm(func=mdp.projected_gravity)
        velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
        wheel_vel = ObsTerm(func=mdp.joint_vel_rel, params={"asset_cfg": WHEELS})
        actions = ObsTerm(func=mdp.last_action)

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class EventCfg:
    # 整机回到默认姿态（含关节目标，6.4.1），再给底盘一个随机朝向
    reset_to_default = EventTerm(func=mdp.reset_scene_to_default, mode="reset", params={"reset_joint_targets": True})
    reset_base = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={"pose_range": {"yaw": (-math.pi, math.pi)}, "velocity_range": {}},
    )


@configclass
class RewardsCfg:
    # 权重照 Isaac Lab 速度跟踪任务（locomotion/velocity）；std 由 √0.25 收窄到 0.25（6.4.5 调参轮 std025b）
    track_lin_vel_xy = RewTerm(func=mdp.track_lin_vel_xy_exp, weight=1.0, params={"command_name": "base_velocity", "std": 0.25})
    track_ang_vel_z = RewTerm(func=mdp.track_ang_vel_z_exp, weight=0.5, params={"command_name": "base_velocity", "std": 0.25})
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.01)
    flat_orientation = RewTerm(func=mdp.flat_orientation_l2, weight=-2.0)  # 侧倾惩罚


@configclass
class TerminationsCfg:
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    tipped = DoneTerm(func=mdp.bad_orientation, params={"limit_angle": 0.5})  # 倾斜超过约 29° 算倾覆


@configclass
class GalbotBaseVelEnvCfg(ManagerBasedRLEnvCfg):
    scene: BaseVelSceneCfg = BaseVelSceneCfg(num_envs=1024, env_spacing=3.0)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()

    def __post_init__(self):
        self.sim.dt = 1 / 120
        self.decimation = 4  # 30 Hz，同主线。改成 1/240、8 的对照（std025b_dt240）没有降低训练中的倾覆，见 6.4.5
        self.sim.render_interval = self.decimation
        self.episode_length_s = 12.0  # 3 段指令
