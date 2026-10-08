# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
"""Galbot One Golf 的 Isaac Lab 配置（6.1.6）。

- GALBOT_ONE_GOLF_CFG：固定底座版，第 6 部分的 reach 等任务都用它；
- GALBOT_ONE_GOLF_WHEELED_CFG：轮式版（浮动根），由 .replace() 派生，留给 6.4.5，本部分不用。

USD 由 scripts/convert_galbot.py 生成（6.1.2），路径经由 GALBOT_GENERATED_DIR 约定（6.1.1）。
本模块要在 Isaac Sim 启动后导入；galbot_academy.assets 不会自动导入它。
"""

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg

from .drives import make_actuators
from .paths import generated_asset_dir

# reach 用的手臂（6.1.6 定，之后各页保持一致）
REACH_ARM = "right"

# 末端坐标系（6.2.1）：描述仓库标准化的 TCP（right_gripper_tcp_link）在转换时随固定关节并入 right_arm_link7，
# 这里给出它相对 right_arm_link7 的固定偏移（由 URDF 的固定关节链组合得到，与厂商 USD 中 tcp prim 的相对位姿一致）。
# 位置单位 m；四元数按 Isaac Lab 约定为 (w, x, y, z)，即绕 y 轴转 180°。
REACH_EE_BODY = f"{REACH_ARM}_arm_link7"
REACH_EE_OFFSET_POS = (-0.25572, 0.0, 0.0)
REACH_EE_OFFSET_ROT = (0.0, 0.0, 1.0, 0.0)

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

GALBOT_ONE_GOLF_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(generated_asset_dir() / "galbot_fixed_base" / "galbot.usd"),
        # 自碰撞打开：依赖 convert_galbot.py 写进资产的 7 对过滤对（6.1.4）。
        # 求解器迭代次数不在此设置，沿用转换器写入的值（位置 32、速度 1）。
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(enabled_self_collisions=True),
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


# 轮式版：浮动根 + 4 个主动轮。只派生出来供 6.4.5 起步，本部分没有用它训练，轮子的阻尼是占位值（未验证）。
# 资产要用 convert_galbot.py --variant wheeled --floating_base 单独转换：固定根版的 Articulation 根就在那个固定关节上，
# 不能靠 fix_root_link=False 把它关掉（实测创建 Articulation 失败，6.1.6）。
GALBOT_ONE_GOLF_WHEELED_CFG = GALBOT_ONE_GOLF_CFG.replace(
    spawn=GALBOT_ONE_GOLF_CFG.spawn.replace(
        usd_path=str(generated_asset_dir() / "galbot_wheeled_floating" / "galbot.usd"),
    ),
    # 轮子的碰撞球在根高度为 0 时最低到 z = -0.032 m（6.1.2），初始抬高一点，让它落到地面上
    init_state=GALBOT_ONE_GOLF_CFG.init_state.replace(pos=(0.0, 0.0, 0.04)),
    actuators={
        **make_actuators(),
        # 主动轮：速度控制，stiffness 为 0，只用 damping 跟踪目标速度（Isaac Lab 的 Ridgeback 底盘同样如此）
        "wheels": ImplicitActuatorCfg(joint_names_expr=["wheel[1-4]_joint"], stiffness=0.0, damping=10.0),
        # 被动滚子：沿用 USD（刚度 0、小阻尼，6.1.2）
        "rollers": ImplicitActuatorCfg(joint_names_expr=["wheel_[1-4]_passive_.*"], stiffness=None, damping=None),
    },
)
"""Galbot One Golf，轮式底盘（浮动根）。未用于训练。"""
