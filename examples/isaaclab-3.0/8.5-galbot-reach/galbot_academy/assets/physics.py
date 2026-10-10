# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""Galbot 的碰撞相关设置（6.1.4）。只依赖 pxr，转换脚本与实验脚本共用。"""

from pxr import Usd, UsdPhysics

# 开启自碰撞时要排除的刚体对（6.1.4 实测）。PhysX 只自动排除由关节直接相连的两个刚体，下面几对都不是：
# - 躯干与头：隔着一个没有碰撞体的连杆 head_link1，零位时就已相互穿透，不排除会把头顶开；
# - 小臂与腕部（link5 与 link7）：隔着很短的 link6，凸包把凹处填平后，在部分腕部角度下相互重叠；
# - 夹爪的外、内指节：同装在夹爪底座上、由 mimic 联动的平行四杆，凸包彼此重叠。
# 实验只动了右臂与右夹爪；左侧的 3 对按对称补上，未单独实测。
SELF_COLLISION_FILTERED_PAIRS: list[tuple[str, str]] = [("leg_link5", "head_link2")] + [
    pair
    for side in ("left", "right")
    for pair in [
        (f"{side}_arm_link5", f"{side}_arm_link7"),
        (f"{side}_gripper_l_knuckle_link", f"{side}_gripper_l_inner_knuckle_link"),
        (f"{side}_gripper_r_knuckle_link", f"{side}_gripper_r_inner_knuckle_link"),
    ]
]


def add_filtered_pairs(stage: Usd.Stage, root_path: str, pairs=SELF_COLLISION_FILTERED_PAIRS) -> int:
    """为每一对刚体写入 UsdPhysics.FilteredPairsAPI，使它们互不碰撞；返回写入的对数。

    写在资产里（转换阶段）时，关系目标随引用一起重映射，机器人放到任何路径、克隆多少份都有效。
    """
    # 3.0 版（8.5）：按刚体名查找，不再假定刚体直接挂在根下。5.1 的转换器生成扁平结构（/galbot_one_golf/leg_link5），
    # 3.0 的转换器生成嵌套结构（/galbot_one_golf/Geometry/base_link/.../leg_link5）
    bodies = {
        p.GetName(): p.GetPath()
        for p in Usd.PrimRange(stage.GetPrimAtPath(root_path))
        if p.HasAPI(UsdPhysics.RigidBodyAPI)
    }
    for a, b in pairs:
        if a not in bodies or b not in bodies:
            raise ValueError(f"在 {root_path} 下找不到刚体 {a} 或 {b}")
        UsdPhysics.FilteredPairsAPI.Apply(stage.GetPrimAtPath(bodies[a])).CreateFilteredPairsRel().AddTarget(bodies[b])
    return len(pairs)


def remove_filtered_pairs(stage: Usd.Stage, root_path: str) -> int:
    """去掉 root_path 下所有刚体上的过滤对（对照实验用）；返回处理的刚体数。"""
    n = 0
    for prim in stage.GetPrimAtPath(root_path).GetChildren():
        if prim.HasAPI(UsdPhysics.FilteredPairsAPI):
            # 要写一个显式的空列表：ClearTargets 只清掉当前编辑层的意见，资产里引用进来的目标仍然有效
            UsdPhysics.FilteredPairsAPI(prim).GetFilteredPairsRel().SetTargets([])
            n += 1
    return n
