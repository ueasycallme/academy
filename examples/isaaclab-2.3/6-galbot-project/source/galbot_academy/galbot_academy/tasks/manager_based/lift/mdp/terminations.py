# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-09
"""lift 的终止条件（6.4.3）。"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.managers import SceneEntityCfg

from .rewards import object_lift_height

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv

__all__ = ["object_dropped"]


def object_dropped(
    env: ManagerBasedRLEnv, drop_height: float, rest_z: float, object_cfg: SceneEntityCfg = SceneEntityCfg("object")
) -> torch.Tensor:
    """方块掉到桌面以下 drop_height（m）时终止，即掉下了桌子。

    官方用 root_height_below_minimum(minimum_height=-0.05)，同样是世界坐标的绝对高度：官方桌面上表面在 z ≈ 0，
    -0.05 就是"桌面以下约 5 cm"。本项目桌面在 0.95 m，照抄这条永远不会触发。
    """
    return object_lift_height(env, rest_z, object_cfg) < -drop_height
