# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-09
"""lift 的场景（6.4.3）：reach 的桌面场景 + 一个可抓取的方块 + 末端坐标系传感器。

对照 Isaac Lab 的 ObjectTableSceneCfg（manipulation/lift/lift_env_cfg.py）与 Franka 版的
FrankaCubeLiftEnvCfg（config/franka/joint_pos_env_cfg.py）：
- 桌子：官方用 Nucleus 上的 SeattleLabTable，桌面在 z = 0；这里沿用 6.2.1 的长方体桌面，桌面在 z = TABLE_TOP_Z。
- 方块：官方用 Nucleus 上的 DexCube（缩放 0.8）；这里用程序生成的长方体，尺寸、质量、摩擦都写在本文件。
- 末端坐标系：官方从 panda_hand 偏移 0.1034 m；这里从 right_arm_link7 偏移到描述仓库标准化的 TCP（6.2.1）。
"""

import isaaclab.sim as sim_utils
from isaaclab.assets import RigidObjectCfg
from isaaclab.markers.config import FRAME_MARKER_CFG
from isaaclab.sensors import FrameTransformerCfg
from isaaclab.sensors.frame_transformer import OffsetCfg
from isaaclab.utils import configclass

from galbot_academy.assets.galbot import REACH_EE_BODY, REACH_EE_OFFSET_POS, REACH_EE_OFFSET_ROT

from .reach import TABLE_CENTER_XY, TABLE_TOP_Z, GalbotReachTableSceneCfg

CUBE_SIZE = 0.05  # 方块边长，m
CUBE_MASS = 0.1  # kg
# 方块初始位置（相对机器人根），m：放在桌面中心，离各桌边 ≥ 25 cm（随机偏移后仍是）。最初放在 (0.50, -0.25)，
# 离靠近机器人的桌边只有约 12 cm，训练中策略学会了把方块推下桌来提前结束回合（6.4.3"失败模式"）
CUBE_SPAWN_XY = TABLE_CENTER_XY
CUBE_REST_Z = TABLE_TOP_Z + CUBE_SIZE / 2  # 方块静止在桌面上时中心的高度


@configclass
class GalbotLiftSceneCfg(GalbotReachTableSceneCfg):
    """地面、灯光、机器人、桌面（继承自 reach），加方块与末端坐标系。"""

    object = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Object",
        init_state=RigidObjectCfg.InitialStateCfg(pos=(*CUBE_SPAWN_XY, CUBE_REST_Z), rot=(1.0, 0.0, 0.0, 0.0)),
        spawn=sim_utils.CuboidCfg(
            size=(CUBE_SIZE, CUBE_SIZE, CUBE_SIZE),
            # 刚体参数照搬官方 Franka 版的方块（位置迭代 16、速度迭代 1，去穿透速度上限 5 m/s）
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                solver_position_iteration_count=16,
                solver_velocity_iteration_count=1,
                max_angular_velocity=1000.0,
                max_linear_velocity=1000.0,
                max_depenetration_velocity=5.0,
                disable_gravity=False,
            ),
            mass_props=sim_utils.MassPropertiesCfg(mass=CUBE_MASS),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            # 摩擦系数取 1.0；夹爪指节沿用资产里的材质，接触时两者按 RigidBodyMaterialCfg 默认的 average 方式合成
            physics_material=sim_utils.RigidBodyMaterialCfg(static_friction=1.0, dynamic_friction=1.0),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.8, 0.2, 0.2)),
        ),
    )

    # 末端坐标系：源是机器人根，目标是 TCP（right_arm_link7 + 固定偏移，见 assets/galbot.py 与 6.2.1）
    ee_frame = FrameTransformerCfg(
        prim_path="{ENV_REGEX_NS}/Robot/base_link",
        debug_vis=False,
        visualizer_cfg=FRAME_MARKER_CFG.replace(prim_path="/Visuals/FrameTransformer"),
        target_frames=[
            FrameTransformerCfg.FrameCfg(
                prim_path=f"{{ENV_REGEX_NS}}/Robot/{REACH_EE_BODY}",
                name="end_effector",
                offset=OffsetCfg(pos=REACH_EE_OFFSET_POS, rot=REACH_EE_OFFSET_ROT),
            ),
        ],
    )


__all__ = ["GalbotLiftSceneCfg", "CUBE_SIZE", "CUBE_MASS", "CUBE_SPAWN_XY", "CUBE_REST_Z", "TABLE_TOP_Z", "TABLE_CENTER_XY"]
