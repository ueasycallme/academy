# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""Galbot One Golf 的 Isaac Lab 配置（6.1.6；3.0 EA 版，8.5）。

- GALBOT_ONE_GOLF_CFG：固定底座版，reach 用它。2.3 项目里的轮式版本子集不带。

USD 由 scripts/convert_galbot.py 生成（6.1.2），路径经由 GALBOT_GENERATED_DIR 约定（6.1.1）。
本模块要在 Isaac Sim 启动后导入；galbot_academy.assets 不会自动导入它。
"""

import os

from isaaclab_physx.sim.schemas import PhysxArticulationRootPropertiesCfg

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg

from .drives import make_actuators
from .paths import generated_asset_dir

# reach 用的手臂（6.1.6 定，之后各页保持一致）
REACH_ARM = "right"

# 末端坐标系（6.2.1）：描述仓库标准化的 TCP（right_gripper_tcp_link）在转换时随固定关节并入 right_arm_link7，
# 这里给出它相对 right_arm_link7 的固定偏移（由 URDF 的固定关节链组合得到，与厂商 USD 中 tcp prim 的相对位姿一致）。
# 位置单位 m；四元数按 Isaac Lab 3.0 的约定为 (x, y, z, w)，即绕 y 轴转 180°（2.3 里写作 WXYZ 的 (0, 0, 1, 0)）。
REACH_EE_BODY = f"{REACH_ARM}_arm_link7"
REACH_EE_OFFSET_POS = (-0.25572, 0.0, 0.0)
REACH_EE_OFFSET_ROT = (0.0, 1.0, 0.0, 0.0)

# 默认关节位置：腿、头、双臂取自 Isaac Lab 官方 Galbot One Charlie 配置（isaaclab_assets/robots/galbot.py）的初始姿态，
# 在本机器人上重新验证过：全部在限位内且离开限位，重力下腿部各关节需要的力矩不超过上限的一半（6.1.6 验证脚本）。
# 零位不行：腿 1–3 的零位正是下限，上半身压在限位上（6.1.5）。
DEFAULT_JOINT_POS = {
    "leg_joint1": 0.8,
    "leg_joint2": 2.3,
    "leg_joint3": 1.55,
    "leg_joint4": 0.0,
    "leg_joint5": 0.0,
    "head_joint1": 0.0,
    "head_joint2": 0.36,
    "left_arm_joint1": -0.5480,
    "left_arm_joint2": -0.6551,
    "left_arm_joint3": 2.407,
    "left_arm_joint4": 1.3641,
    "left_arm_joint5": -0.4416,
    "left_arm_joint6": 0.1168,
    "left_arm_joint7": 1.2308,
    "right_arm_joint1": 0.1535,
    "right_arm_joint2": 1.0087,
    "right_arm_joint3": 0.0895,
    "right_arm_joint4": 1.5743,
    "right_arm_joint5": -0.2422,
    "right_arm_joint6": -0.0009,
    "right_arm_joint7": -0.9143,
    ".*_gripper_.*": 0.0,  # 夹爪张开；mimic 跟随关节同为 0
}

# Newton 后端用的资产（8.5）：5.1 转换的 USD 在 Newton 下用不了（悬空引用、碰撞 API 加在 Xform 上），
# 改用 3.0 自带的 URDF 转换器重新转换（scripts/convert_galbot_30.py）。PhysX 预设仍用 5.1 转换的原资产
# 环境变量 GALBOT_NEWTON_USD 可以换成别的资产（8.5 用它复现"5.1 资产在 Newton 下失败"）
GALBOT_NEWTON_USD = os.environ.get(
    "GALBOT_NEWTON_USD",
    str(generated_asset_dir() / "galbot_fixed_base_30" / "galbot_one_golf_fixed_base" / "galbot_one_golf_fixed_base.usda"),
)

GALBOT_ONE_GOLF_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(generated_asset_dir() / "galbot_fixed_base" / "galbot.usd"),
        # 自碰撞打开：依赖 convert_galbot.py 写进资产的 7 对过滤对（6.1.4）。
        # 求解器迭代次数：位置 16、速度 1（6.1.6b 对比 32/1、16/1、8/0 后选定；转换器写入的是 32/1）。
        # 3.0：求解器迭代次数是 PhysX 专有字段，用 PhysxArticulationRootPropertiesCfg（旧名 ArticulationRootPropertiesCfg 为弃用别名）
        articulation_props=PhysxArticulationRootPropertiesCfg(
            enabled_self_collisions=True, solver_position_iteration_count=16, solver_velocity_iteration_count=1
        ),
        # 不改刚体与碰撞属性：碰撞体在实例内部，spawn 阶段的 collision_props 改不到（6.1.4）。
        # 接触传感器到 6.2.2 才用，这里不开。
        activate_contact_sensors=False,
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.0),  # 根固定在世界中；底盘碰撞体已并入固定根，不会与地面相互作用（6.1.2）
        joint_pos=DEFAULT_JOINT_POS,
        joint_vel={".*": 0.0},
    ),
    actuators=make_actuators(),  # 参数表见 drives.py（6.1.5）
)
"""Galbot One Golf，固定底座。"""
