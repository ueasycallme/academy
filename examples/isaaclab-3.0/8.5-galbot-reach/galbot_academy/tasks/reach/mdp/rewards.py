# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""以 TCP 为末端的奖励（6.4.1；3.0 EA 版，8.5）。写法照搬 Isaac Lab reach 任务的三个函数，只把刚体原点换成"刚体 + 偏移"。"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.math import combine_frame_transforms, quat_error_magnitude

from .tcp import tcp_pose_w

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv

__all__ = ["tcp_position_error", "tcp_position_error_tanh", "tcp_orientation_error"]


def _command_w(env: ManagerBasedRLEnv, command_name: str, asset_cfg: SceneEntityCfg):
    robot = env.scene[asset_cfg.name]
    cmd = env.command_manager.get_command(command_name)  # 根坐标系下 (x, y, z, qx, qy, qz, qw)：3.0 改为 XYZW
    return combine_frame_transforms(robot.data.root_pos_w.torch, robot.data.root_quat_w.torch, cmd[:, :3], cmd[:, 3:7])


def _tcp(env: ManagerBasedRLEnv, asset_cfg: SceneEntityCfg, offset_pos, offset_rot):
    robot = env.scene[asset_cfg.name]
    return tcp_pose_w(robot, asset_cfg.body_ids[0], offset_pos, offset_rot)


def tcp_position_error(env, command_name: str, asset_cfg: SceneEntityCfg, offset_pos, offset_rot) -> torch.Tensor:
    """TCP 与目标位置的距离（m），作为惩罚用（权重取负）。"""
    target, _ = _command_w(env, command_name, asset_cfg)
    pos, _ = _tcp(env, asset_cfg, offset_pos, offset_rot)
    return torch.norm(pos - target, dim=1)


def tcp_position_error_tanh(env, std: float, command_name: str, asset_cfg: SceneEntityCfg, offset_pos, offset_rot) -> torch.Tensor:
    """1 − tanh(距离 / std)：距离为 0 时为 1，越远越接近 0（权重取正）。"""
    return 1 - torch.tanh(tcp_position_error(env, command_name, asset_cfg, offset_pos, offset_rot) / std)


def tcp_orientation_error(env, command_name: str, asset_cfg: SceneEntityCfg, offset_pos, offset_rot) -> torch.Tensor:
    """TCP 与目标姿态之间的旋转角（rad），作为惩罚用（权重取负）。"""
    _, target_q = _command_w(env, command_name, asset_cfg)
    _, q = _tcp(env, asset_cfg, offset_pos, offset_rot)
    return quat_error_magnitude(q, target_q)
