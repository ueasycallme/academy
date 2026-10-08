# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-08
"""TCP 位姿：刚体位姿加上固定偏移（6.2.1 定义的 REACH_EE_OFFSET_*）。"""

import torch

from isaaclab.assets import Articulation
from isaaclab.utils.math import combine_frame_transforms


def tcp_pose_w(robot: Articulation, body_idx: int, offset_pos, offset_rot) -> tuple[torch.Tensor, torch.Tensor]:
    """返回世界系下 TCP 的位置 (N, 3) 与四元数 (N, 4，w, x, y, z)。"""
    n = robot.num_instances
    p = torch.tensor(offset_pos, device=robot.device).expand(n, 3)
    q = torch.tensor(offset_rot, device=robot.device).expand(n, 4)
    return combine_frame_transforms(robot.data.body_pos_w[:, body_idx], robot.data.body_quat_w[:, body_idx], p, q)
