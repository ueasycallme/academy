# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
"""pick-place 的观测、子任务信号与成功判定（6.4.6）。

坐标约定：机器人根固定在各环境原点、不旋转（assets/galbot.py），所以"根坐标系"与"环境局部坐标"只差环境原点的平移。
末端（TCP）的位姿一律取 FrameTransformer `ee_frame`（源是机器人根），与 IK 动作项跟踪的是同一个点（pick_place_env_cfg.py）。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.managers import SceneEntityCfg

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv

__all__ = ["ee_pos", "ee_quat", "gripper_q", "target_position_in_robot_root_frame", "object_grasped", "object_placed"]


def ee_pos(env: ManagerBasedRLEnv, ee_frame_cfg: SceneEntityCfg = SceneEntityCfg("ee_frame")) -> torch.Tensor:
    """TCP 在机器人根坐标系下的位置 (N, 3)。"""
    return env.scene[ee_frame_cfg.name].data.target_pos_source[:, 0, :]


def ee_quat(env: ManagerBasedRLEnv, ee_frame_cfg: SceneEntityCfg = SceneEntityCfg("ee_frame")) -> torch.Tensor:
    """TCP 在机器人根坐标系下的姿态 (N, 4)，wxyz。"""
    return env.scene[ee_frame_cfg.name].data.target_quat_source[:, 0, :]


def gripper_q(env: ManagerBasedRLEnv, gripper_cfg: SceneEntityCfg) -> torch.Tensor:
    """夹爪主动关节的测量位置 (N, 1)，rad：0.6 为本任务的"张开"，夹住 5 cm 方块时约 1.69（6.4.3）。"""
    return env.scene[gripper_cfg.name].data.joint_pos[:, gripper_cfg.joint_ids]


def target_position_in_robot_root_frame(
    env: ManagerBasedRLEnv, target_cfg: SceneEntityCfg = SceneEntityCfg("target")
) -> torch.Tensor:
    """放置点（桌面上的绿色方垫）中心在机器人根坐标系下的位置 (N, 3)。"""
    return env.scene[target_cfg.name].data.root_pos_w - env.scene.env_origins


def _object_to_tcp(env: ManagerBasedRLEnv, object_cfg: SceneEntityCfg, ee_frame_cfg: SceneEntityCfg) -> torch.Tensor:
    obj = env.scene[object_cfg.name].data.root_pos_w - env.scene.env_origins
    return torch.linalg.norm(obj - ee_pos(env, ee_frame_cfg), dim=-1)


def object_grasped(
    env: ManagerBasedRLEnv,
    gripper_cfg: SceneEntityCfg,
    min_q: float,
    max_dist: float,
    object_cfg: SceneEntityCfg = SceneEntityCfg("object"),
    ee_frame_cfg: SceneEntityCfg = SceneEntityCfg("ee_frame"),
) -> torch.Tensor:
    """子任务信号"抓住了"(N,)：夹爪测量位置 ≥ min_q，且方块中心离 TCP 不超过 max_dist。

    只看夹爪会把"空手握拳"也算进去；只看距离会把"张着手从方块旁经过"算进去，两者都要。
    """
    closed = gripper_q(env, gripper_cfg)[:, 0] >= min_q
    return closed & (_object_to_tcp(env, object_cfg, ee_frame_cfg) <= max_dist)


def object_placed(
    env: ManagerBasedRLEnv,
    gripper_cfg: SceneEntityCfg,
    max_open_q: float,
    xy_tol: float,
    rest_z: float,
    z_tol: float,
    min_release_dist: float,
    object_cfg: SceneEntityCfg = SceneEntityCfg("object"),
    target_cfg: SceneEntityCfg = SceneEntityCfg("target"),
    ee_frame_cfg: SceneEntityCfg = SceneEntityCfg("ee_frame"),
) -> torch.Tensor:
    """成功判定 (N,)：方块落在放置点上、夹爪已张开、手已离开方块。

    - 方块中心与放置点中心的水平距离 ≤ xy_tol；
    - 方块中心高度与静止在桌面上时相差 ≤ z_tol（放在桌上，而不是悬在放置点上方）；
    - 夹爪测量位置 ≤ max_open_q（真的松开了）；
    - TCP 离方块中心 ≥ min_release_dist（手已移开，不是"夹着方块停在放置点上、指尖刚好松一点"）。
    """
    obj = env.scene[object_cfg.name].data.root_pos_w - env.scene.env_origins
    tgt = target_position_in_robot_root_frame(env, target_cfg)
    on_target = torch.linalg.norm(obj[:, :2] - tgt[:, :2], dim=-1) <= xy_tol
    on_table = (obj[:, 2] - rest_z).abs() <= z_tol
    released = gripper_q(env, gripper_cfg)[:, 0] <= max_open_q
    away = _object_to_tcp(env, object_cfg, ee_frame_cfg) >= min_release_dist
    return on_target & on_table & released & away
