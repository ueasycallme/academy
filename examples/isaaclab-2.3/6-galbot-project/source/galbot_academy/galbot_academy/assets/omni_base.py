# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.11（不依赖 Isaac Sim）；几何取自 Galbot 描述仓库 commit 2d496b0 的 galbot_one_golf.urdf
# 验证日期：2026-10-11
"""Galbot 全向底盘的几何与运动学（6.4.5）。

URDF 里 4 个主动轮装在 omni_chassis_base_link 的四角（x、y 各 ±0.1765 m），转轴是各自坐标系的 x 轴，
分别绕 z 转了 −135°、−45°、45°、135°，即 X 形布局。每个轮子外圈有 10 个被动滚子。

轮子 i 的"驱动方向" d_i 是转轴叉乘竖直向上（没有滚子方向的约束，轮子只管这一个方向的速度）。
底盘速度 (vx, vy, wz) 对应的轮速：ω_i = d_i ·(v + wz ẑ × r_i) / R。符号以 probe_rollers.py 的实测为准。
"""

import math

WHEEL_JOINTS = ["wheel1_joint", "wheel2_joint", "wheel3_joint", "wheel4_joint"]
HALF = 0.176493  # 轮心到底盘中心在 x、y 上的距离（m），URDF wheel*_joint 的 origin
WHEEL_YAW = [-0.75 * math.pi, -0.25 * math.pi, 0.25 * math.pi, 0.75 * math.pi]  # 各轮坐标系绕 z 的转角
WHEEL_POS = [(HALF, HALF), (-HALF, HALF), (-HALF, -HALF), (HALF, -HALF)]
# 轮子半径：轮心在根上方 0.0718 m，滚子碰撞球最低到 −0.032 m（6.1.2），差约 0.104 m（推断，未直接量网格）
WHEEL_RADIUS = 0.104


def drive_dirs() -> list[tuple[float, float]]:
    """各轮驱动方向（底盘坐标系）：转轴 a = (cos ψ, sin ψ, 0)，d = a × ẑ = (sin ψ, −cos ψ)。"""
    return [(math.sin(y), -math.cos(y)) for y in WHEEL_YAW]


def body_to_wheel(vx: float, vy: float, wz: float) -> list[float]:
    """底盘速度（底盘坐标系，m/s 与 rad/s）→ 4 个轮子的角速度（rad/s）。"""
    out = []
    for (dx, dy), (px, py) in zip(drive_dirs(), WHEEL_POS):
        ux, uy = vx - wz * py, vy + wz * px  # 轮心速度 = v + wz ẑ × r
        out.append((dx * ux + dy * uy) / WHEEL_RADIUS)
    return out
