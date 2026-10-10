# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""Galbot 固定底座版的关节驱动参数表（6.1.5）。

这是仿真内自洽的参数，不代表真机（D-004）。各组的 joint_names_expr 互不重叠（Isaac Lab 要求）。
stiffness 单位 N·m/rad，damping 单位 N·m·s/rad；joint_effort_limit / joint_velocity_limit 为 None 时沿用 USD 中的值，
也就是 URDF 的 effort / velocity（转换器写入）。6.1.6 用 make_actuators() 组装 ArticulationCfg。
"""

GROUPS: dict[str, dict] = {
    # 躯干升降（腿）：承担上半身重量，按关节分别给刚度
    "legs": {
        "joint_names_expr": ["leg_joint[1-5]"],
        "stiffness": {"leg_joint[1-3]": 4000.0, "leg_joint[4-5]": 400.0},
        "damping": {"leg_joint[1-3]": 400.0, "leg_joint[4-5]": 40.0},
    },
    "head": {
        "joint_names_expr": ["head_joint[1-2]"],
        "stiffness": 400.0,
        "damping": 40.0,
    },
    "arms": {
        "joint_names_expr": ["(left|right)_arm_joint[1-7]"],
        "stiffness": 400.0,
        "damping": 40.0,
    },
    "grippers": {
        "joint_names_expr": ["(left|right)_gripper_joint"],
        "stiffness": 100.0,
        "damping": 10.0,
    },
}

# mimic 跟随关节：由 mimic 约束带动，没有驱动。单列一组、增益沿用 USD（为 0），只为让每个关节都归属某一组。
MIMIC_FOLLOWERS = ["(left|right)_gripper_(l|r)_(inner_knuckle|finger)_joint", "(left|right)_gripper_l_knuckle_joint"]


def make_actuators(use_usd_gains: bool = False) -> dict:
    """按参数表生成 {组名: ImplicitActuatorCfg}。use_usd_gains=True 时增益改用 USD 中的值（对照用）。"""
    from isaaclab.actuators import ImplicitActuatorCfg

    actuators = {}
    for name, spec in GROUPS.items():
        actuators[name] = ImplicitActuatorCfg(
            joint_names_expr=spec["joint_names_expr"],
            stiffness=None if use_usd_gains else spec["stiffness"],
            damping=None if use_usd_gains else spec["damping"],
            # 3.0：effort_limit_sim / velocity_limit_sim 改名为 joint_effort_limit / joint_velocity_limit（8.4 表 1）
            joint_effort_limit=spec.get("joint_effort_limit"),
            joint_velocity_limit=spec.get("joint_velocity_limit"),
        )
    actuators["mimic"] = ImplicitActuatorCfg(joint_names_expr=MIMIC_FOLLOWERS, stiffness=None, damping=None)
    return actuators
