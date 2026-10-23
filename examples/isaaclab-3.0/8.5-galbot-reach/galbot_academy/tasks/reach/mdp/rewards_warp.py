# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0（commit e3f7d9ff1），warp-lang 1.17.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-23
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04
"""`tcp_position_error` 的 Warp 内核版（8.9）。与 rewards.py 的 torch 版算的是同一个量：

    目标（世界系）= 根位置 + 根姿态 ⊗ 指令位置
    TCP（世界系） = 刚体位置 + 刚体姿态 ⊗ TCP 偏移
    误差 = ‖TCP − 目标‖

torch 版要先 `.torch` 取张量，再经 combine_frame_transforms 做几次批量运算；这里一个内核、每个环境一个线程算完。
资产数据直接以 ProxyArray 传给 wp.launch（经 __cuda_array_interface__，零拷贝），指令是 torch 张量，用 wp.from_torch 包一层（也零拷贝）。
Warp 的四元数是 (x, y, z, w)，与 3.0 的数据约定一致，不用换顺序（8.4）。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
import warp as wp

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv
    from isaaclab.managers import SceneEntityCfg

__all__ = ["tcp_position_error_warp"]


@wp.kernel
def _tcp_position_error_kernel(
    root_pos: wp.array(dtype=wp.vec3f),  # (N,)
    root_quat: wp.array(dtype=wp.quatf),  # (N,) x, y, z, w
    body_pos: wp.array2d(dtype=wp.vec3f),  # (N, 刚体数)
    body_quat: wp.array2d(dtype=wp.quatf),  # (N, 刚体数)
    command: wp.array2d(dtype=wp.float32),  # (N, 7)：根系下的目标位置与姿态
    body_idx: int,
    offset_pos: wp.vec3f,
    out: wp.array(dtype=wp.float32),  # (N,)
):
    i = wp.tid()
    cmd_pos = wp.vec3f(command[i, 0], command[i, 1], command[i, 2])
    target = root_pos[i] + wp.quat_rotate(root_quat[i], cmd_pos)
    tcp = body_pos[i, body_idx] + wp.quat_rotate(body_quat[i, body_idx], offset_pos)
    out[i] = wp.length(tcp - target)


_OUT: dict[int, wp.array] = {}  # 每个环境一个输出缓冲，避免每步重新分配


def tcp_position_error_warp(
    env: ManagerBasedRLEnv, command_name: str, asset_cfg: SceneEntityCfg, offset_pos, offset_rot
) -> torch.Tensor:
    """TCP 与目标位置的距离（m）。签名与 rewards.tcp_position_error 相同（offset_rot 不影响位置，保留以便直接替换）。"""
    robot = env.scene[asset_cfg.name]
    n = robot.num_instances
    out = _OUT.get(id(env))
    if out is None or out.shape[0] != n:
        out = _OUT[id(env)] = wp.zeros(n, dtype=wp.float32, device=str(env.device))
    cmd = env.command_manager.get_command(command_name)
    wp.launch(
        _tcp_position_error_kernel,
        dim=n,
        inputs=[
            robot.data.root_pos_w,  # ProxyArray 直接传，不经 .torch
            robot.data.root_quat_w,
            robot.data.body_pos_w,
            robot.data.body_quat_w,
            wp.from_torch(cmd),
            int(asset_cfg.body_ids[0]),
            wp.vec3f(*offset_pos),
        ],
        outputs=[out],
        device=str(env.device),
    )
    return wp.to_torch(out)  # 零拷贝；奖励管理器要 torch 张量
