# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-09
"""lift 场景加传感器（6.2.2）：右腕相机、TCP→方块的坐标系变换、两个指尖的接触传感器。

用法：make_sensor_scene_cfg(...) 在 GalbotLiftSceneCfg 上按开关加传感器，返回场景配置；
scripts/check_sensors.py 用它验证数据与测代价。主线的 reach / lift 训练不用本模块。

- 相机：URDF 的 right_wrist_camera_link 转换时随固定关节并入 right_arm_link7 刚体，但在 USD 里仍留有同名 Xform
  （right_arm_link7/right_arm_wrist_camera_stand/right_wrist_camera_link），相机直接挂在它下面，偏移为零。
  该 link 的 +Z 指向夹爪前方，按 ROS 光学坐标系（+Z 前、-Y 上）解释，所以 convention="ros"（推断，依据见 6.2.2）。
  FrameTransformer 不能这样用：它只接受刚体，所以 TCP 用"link7 + 固定偏移"（6.2.1）。
- 接触传感器：带过滤（只看与方块的接触）时，一个传感器在每个环境只能匹配一个刚体（匹配两个时 force_matrix_w
  全为零且不报错，6.2.2 实测），所以左右指尖各一个传感器。需要机器人 spawn 时 activate_contact_sensors=True（galbot.py 默认 False）。
"""

import math

import isaaclab.sim as sim_utils
from isaaclab.sensors import ContactSensorCfg, FrameTransformerCfg, TiledCameraCfg
from isaaclab.sensors.frame_transformer import OffsetCfg

from galbot_academy.assets.galbot import REACH_ARM, REACH_EE_BODY, REACH_EE_OFFSET_POS, REACH_EE_OFFSET_ROT

from .lift import GalbotLiftSceneCfg

# 相机挂载点：转换后留在 link7 下的 URDF 相机 link（Xform）
WRIST_CAMERA_LINK_PATH = f"{REACH_EE_BODY}/{REACH_ARM}_arm_wrist_camera_stand/{REACH_ARM}_wrist_camera_link"
# 该 link 相对 right_arm_link7 的位姿，只用于核对（check_sensors.py）：URDF right_arm_camera_stand_joint（无 origin，即单位变换）
# 与 right_arm_camera_joint（xyz="-0.0822 0 -0.06842" rpy="0 1.4808 3.1416"）的组合。四元数 (w, x, y, z)
WRIST_CAMERA_POS = (-0.0822, 0.0, -0.06842)
WRIST_CAMERA_ROT = (0.0, -0.6746, 0.0, 0.7382)
# 视场角：URDF 没有给内参；取 RealSense D405 产品页（realsenseai.com）的深度视场 87° × 58°（水平 × 垂直）中的水平值。
# 这里用正方形小图，垂直视场随之也是 87°，与真机不同
WRIST_CAMERA_HFOV_DEG = 87.0
_FOCAL_LENGTH = 24.0  # 与 Isaac Lab 默认相同；视场只由 focal_length 与 horizontal_aperture 的比值决定
_H_APERTURE = 2 * _FOCAL_LENGTH * math.tan(math.radians(WRIST_CAMERA_HFOV_DEG / 2))

FINGER_BODIES = {side: f"{REACH_ARM}_gripper_{side}_finger_link" for side in ("l", "r")}


def wrist_camera_cfg(resolution: int = 64, data_types: tuple[str, ...] = ("rgb", "depth")) -> TiledCameraCfg:
    """右腕相机：TiledCamera，正方形分辨率 resolution × resolution。"""
    return TiledCameraCfg(
        prim_path=f"{{ENV_REGEX_NS}}/Robot/{WRIST_CAMERA_LINK_PATH}/wrist_cam",
        offset=TiledCameraCfg.OffsetCfg(convention="ros"),  # 位置、姿态都与相机 link 重合
        data_types=list(data_types),
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=_FOCAL_LENGTH,
            horizontal_aperture=_H_APERTURE,
            clipping_range=(0.01, 5.0),  # D405 最近可测距离约 7 cm；远处只有桌子和地面，5 m 足够
        ),
        width=resolution,
        height=resolution,
        update_period=0.0,  # 0 = 每次场景更新都刷新（实际刷新频率受渲染间隔限制）
    )


def tcp_to_cube_cfg() -> FrameTransformerCfg:
    """源是 TCP（link7 + 固定偏移，与 lift 的 ee_frame 相同），目标是方块：直接给出方块在 TCP 坐标系里的位姿。"""
    return FrameTransformerCfg(
        prim_path=f"{{ENV_REGEX_NS}}/Robot/{REACH_EE_BODY}",
        source_frame_offset=OffsetCfg(pos=REACH_EE_OFFSET_POS, rot=REACH_EE_OFFSET_ROT),
        target_frames=[FrameTransformerCfg.FrameCfg(prim_path="{ENV_REGEX_NS}/Object", name="cube")],
        debug_vis=False,
    )


def finger_contact_cfg(side: str) -> ContactSensorCfg:
    """一个指尖的接触传感器，只报告与方块的接触（force_matrix_w）；net_forces_w 是与所有物体的合力。"""
    return ContactSensorCfg(
        prim_path=f"{{ENV_REGEX_NS}}/Robot/{FINGER_BODIES[side]}",
        filter_prim_paths_expr=["{ENV_REGEX_NS}/Object"],
        history_length=0,
        update_period=0.0,
    )


def make_sensor_scene_cfg(
    num_envs: int,
    camera: int | None = None,
    tcp_to_cube: bool = False,
    contact: bool = False,
    env_spacing: float = 2.5,
) -> GalbotLiftSceneCfg:
    """在 lift 场景上按开关加传感器。camera 为分辨率（None 表示不加）。

    lift 场景本身已有一个 FrameTransformer（ee_frame，机器人根 → TCP）；要对照"没有任何传感器"，调用方自行把它设为 None。
    """
    cfg = GalbotLiftSceneCfg(num_envs=num_envs, env_spacing=env_spacing)
    if camera is not None:
        cfg.wrist_cam = wrist_camera_cfg(camera)
    if tcp_to_cube:
        cfg.tcp_to_cube = tcp_to_cube_cfg()
    if contact:
        cfg.robot = cfg.robot.replace(spawn=cfg.robot.spawn.replace(activate_contact_sensors=True))
        cfg.contact_l = finger_contact_cfg("l")
        cfg.contact_r = finger_contact_cfg("r")
    return cfg


__all__ = [
    "WRIST_CAMERA_LINK_PATH",
    "WRIST_CAMERA_POS",
    "WRIST_CAMERA_ROT",
    "WRIST_CAMERA_HFOV_DEG",
    "FINGER_BODIES",
    "wrist_camera_cfg",
    "tcp_to_cube_cfg",
    "finger_contact_cfg",
    "make_sensor_scene_cfg",
]
