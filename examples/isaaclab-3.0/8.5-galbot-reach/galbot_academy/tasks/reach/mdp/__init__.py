# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""reach 的 MDP 函数（6.4.1）：Isaac Lab 自带的全部函数，加上以 TCP 为末端的命令与奖励。"""

import isaaclab.envs.mdp as _isaaclab_mdp

from .commands_cfg import TcpPoseCommandCfg  # noqa: F401
from .rewards import tcp_orientation_error, tcp_position_error, tcp_position_error_tanh  # noqa: F401


def __getattr__(name: str):
    """其余名字转给 isaaclab.envs.mdp（3.0 的 mdp 是惰性导出）。

    2.3 版这里写的是 from isaaclab.envs.mdp import *：在 3.0 里它会把全部实现模块（连同 pip 版的 pxr）
    在 Kit 启动前导入，Kit 随后起不来（8.5 实测）。改成按需取用。
    """
    return getattr(_isaaclab_mdp, name)
