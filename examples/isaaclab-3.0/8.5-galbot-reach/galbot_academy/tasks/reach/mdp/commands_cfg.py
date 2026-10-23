# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0（commit e3f7d9ff1）+ Isaac Sim 6.2.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-23
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04

"""TcpPoseCommand 的配置类（3.0 版，8.5）。

3.0 的配置类用字符串指向实现类（官方写法如 "{DIR}.pose_command:UniformPoseCommand"，见 commands_cfg.py），
实现类在环境创建时才导入；这里照做，避免在 Kit 启动前加载 pxr。
"""

from dataclasses import MISSING

from isaaclab.envs.mdp.commands.commands_cfg import UniformPoseCommandCfg
from isaaclab.utils import configclass


@configclass
class TcpPoseCommandCfg(UniformPoseCommandCfg):
    """UniformPoseCommandCfg 加上 TCP 相对 body_name 的偏移。"""

    class_type: type | str = "galbot_academy.tasks.reach.mdp.commands:TcpPoseCommand"
    offset_pos: tuple[float, float, float] = MISSING
    offset_rot: tuple[float, float, float, float] = MISSING
