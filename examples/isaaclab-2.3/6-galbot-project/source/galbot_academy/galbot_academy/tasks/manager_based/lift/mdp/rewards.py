# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-09
"""lift 的奖励（6.4.3）。三个函数照搬 Isaac Lab lift 任务（manipulation/lift/mdp/rewards.py），只改一处：

"举起"的判据。官方写的是 object.root_pos_w[:, 2] > minimal_height，即世界坐标的绝对高度。官方桌面
（SeattleLabTable）碰撞体的上表面在 z ≈ -0.003，方块（DexCube × 0.8）边长 4.8 cm，静止时中心约在 z = 0.021，
所以 minimal_height = 0.04 实际是"中心比静止时高约 2 cm"。本项目桌面在 z = 0.95，照抄会让方块静止在桌上时就已"举起"。
这里改成相对桌面的高度：方块中心高于"静止高度 rest_z"多少（6.4.3 用 4 cm，比官方的约 2 cm 严）。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.math import combine_frame_transforms

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv

__all__ = ["object_lift_height", "object_is_lifted", "object_ee_distance", "object_goal_distance", "gripper_closed", "grasp_closure_near_object"]


def object_lift_height(env: ManagerBasedRLEnv, rest_z: float, object_cfg: SceneEntityCfg = SceneEntityCfg("object")) -> torch.Tensor:
    """方块中心比静止在桌面上时高出多少（m），(N,)。rest_z 为环境局部坐标中的静止高度，加上各环境原点的 z。"""
    obj = env.scene[object_cfg.name]
    return obj.data.root_pos_w[:, 2] - (env.scene.env_origins[:, 2] + rest_z)


def gripper_closed(env: ManagerBasedRLEnv, gripper_cfg: SceneEntityCfg | None, min_q: float | None) -> torch.Tensor:
    """夹爪门控：测得的夹爪主动关节位置 ≥ min_q 时为 1，否则为 0。gripper_cfg 为 None 时恒为 1（不门控）。

    用测得的关节位置而不是夹爪指令：下令闭合但还没合拢（或没夹住）时不应计分（6.4.3）。
    """
    if gripper_cfg is None or min_q is None:
        return torch.ones(env.num_envs, device=env.device)
    q = env.scene[gripper_cfg.name].data.joint_pos[:, gripper_cfg.joint_ids]
    return (q.min(dim=-1).values >= min_q).float()


def object_is_lifted(
    env: ManagerBasedRLEnv,
    minimal_height: float,
    rest_z: float,
    object_cfg: SceneEntityCfg = SceneEntityCfg("object"),
    gripper_cfg: SceneEntityCfg | None = None,
    gripper_min_q: float | None = None,
) -> torch.Tensor:
    """方块离开桌面超过 minimal_height（且夹爪已合拢，若给了门控参数）时为 1，否则为 0。"""
    lifted = (object_lift_height(env, rest_z, object_cfg) > minimal_height).float()
    return lifted * gripper_closed(env, gripper_cfg, gripper_min_q)


def object_ee_distance(
    env: ManagerBasedRLEnv,
    std: float,
    object_cfg: SceneEntityCfg = SceneEntityCfg("object"),
    ee_frame_cfg: SceneEntityCfg = SceneEntityCfg("ee_frame"),
) -> torch.Tensor:
    """接近：1 - tanh(|方块 - TCP| / std)。TCP 由 FrameTransformer 给出（scenes/lift.py）。"""
    obj = env.scene[object_cfg.name]
    ee_w = env.scene[ee_frame_cfg.name].data.target_pos_w[..., 0, :]
    return 1 - torch.tanh(torch.norm(obj.data.root_pos_w - ee_w, dim=1) / std)


def object_goal_distance(
    env: ManagerBasedRLEnv,
    std: float,
    minimal_height: float,
    rest_z: float,
    command_name: str,
    robot_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    object_cfg: SceneEntityCfg = SceneEntityCfg("object"),
    gripper_cfg: SceneEntityCfg | None = None,
    gripper_min_q: float | None = None,
) -> torch.Tensor:
    """跟踪目标：方块已举起（且夹爪已合拢，若给了门控参数）时为 1 - tanh(|方块 - 目标| / std)，否则为 0。目标在机器人根坐标系中给出。"""
    robot = env.scene[robot_cfg.name]
    obj = env.scene[object_cfg.name]
    des_pos_w, _ = combine_frame_transforms(robot.data.root_pos_w, robot.data.root_quat_w, env.command_manager.get_command(command_name)[:, :3])
    distance = torch.norm(des_pos_w - obj.data.root_pos_w, dim=1)
    return object_is_lifted(env, minimal_height, rest_z, object_cfg, gripper_cfg, gripper_min_q) * (1 - torch.tanh(distance / std))


def grasp_closure_near_object(
    env: ManagerBasedRLEnv,
    std: float,
    open_q: float,
    closed_q: float,
    gripper_cfg: SceneEntityCfg,
    object_cfg: SceneEntityCfg = SceneEntityCfg("object"),
    ee_frame_cfg: SceneEntityCfg = SceneEntityCfg("ee_frame"),
) -> torch.Tensor:
    """抓取塑形（6.4.3 第 6 组）：夹爪合拢程度 × 靠近方块的核函数。

    合拢程度 = (q - open_q) / (closed_q - open_q)，截到 [0, 1]，q 是测得的夹爪主动关节位置；
    靠近 = 1 - tanh(|方块 - TCP| / std)。只有"在方块旁边合拢"才得分，离得远时合拢几乎没有奖励。
    这是中间奖励：举起与跟踪目标仍要过夹爪门控（gripper_closed）。
    """
    q = env.scene[gripper_cfg.name].data.joint_pos[:, gripper_cfg.joint_ids].min(dim=-1).values
    closure = ((q - open_q) / (closed_q - open_q)).clamp(0.0, 1.0)
    return closure * object_ee_distance(env, std, object_cfg, ee_frame_cfg)
