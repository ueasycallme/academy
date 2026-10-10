# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""TCP 位姿：刚体位姿加上固定偏移（6.2.1 定义的 REACH_EE_OFFSET_*；3.0 EA 版，8.5）。"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.utils.math import combine_frame_transforms

if TYPE_CHECKING:  # 3.0：运行时导入 Articulation 会在 Kit 启动前加载 pxr
    from isaaclab.assets import Articulation


def tcp_pose_w(robot: Articulation, body_idx: int, offset_pos, offset_rot) -> tuple[torch.Tensor, torch.Tensor]:
    """返回世界系下 TCP 的位置 (N, 3) 与四元数 (N, 4，3.0 为 x, y, z, w)。"""
    n = robot.num_instances
    p = torch.tensor(offset_pos, device=robot.device).expand(n, 3)
    q = torch.tensor(offset_rot, device=robot.device).expand(n, 4)
    # 3.0：data.* 是 ProxyArray，索引前先取 .torch
    return combine_frame_transforms(robot.data.body_pos_w.torch[:, body_idx], robot.data.body_quat_w.torch[:, body_idx], p, q)
