# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-11
"""带固定偏移的微分 IK 动作项：按偏移的实际方向修正雅可比（6.4.6）。

Isaac Lab 2.3.2 的 DifferentialInverseKinematicsAction._compute_frame_jacobian（task_space_actions.py L245–L265）
在 body_offset 不为空时这样改父刚体的雅可比（雅可比已换到机器人根坐标系）：
- 平移部分加上 −[r]× · J_ω，其中 r 直接用 offset.pos（它是在**刚体**坐标系里写的）；
- 转动部分左乘 R(offset.rot)。
对一个刚性固连的点，正确的做法是：r 要先转到根坐标系，r_b = R_link · offset.pos；转动部分不变（同一刚体上各点的角速度相同）。
Franka 的偏移是沿手的 z 轴 0.107 m、不旋转，手大致朝下时误差不大；本项目的 TCP 偏移 0.256 m 且绕 y 转 180°
（6.2.1），按原写法转动部分的 x、z 两行被取反，姿态控制发散（6.4.6 实测）。
"""

from __future__ import annotations

import torch

import isaaclab.utils.math as math_utils
from isaaclab.envs.mdp.actions.actions_cfg import DifferentialInverseKinematicsActionCfg
from isaaclab.envs.mdp.actions.task_space_actions import DifferentialInverseKinematicsAction
from isaaclab.utils import configclass

__all__ = ["OffsetCorrectedDiffIKAction", "OffsetCorrectedDiffIKActionCfg"]


class OffsetCorrectedDiffIKAction(DifferentialInverseKinematicsAction):
    def _compute_frame_jacobian(self) -> torch.Tensor:
        jacobian = self.jacobian_b  # 父刚体的雅可比，已在根坐标系
        if self.cfg.body_offset is not None:
            data = self._asset.data
            # 父刚体在根坐标系下的姿态，用它把偏移向量转到根坐标系
            _, link_quat_b = math_utils.subtract_frame_transforms(
                data.root_pos_w, data.root_quat_w, data.body_pos_w[:, self._body_idx], data.body_quat_w[:, self._body_idx]
            )
            r_b = math_utils.quat_apply(link_quat_b, self._offset_pos)
            # v_tcp = v_link + ω × r_b = (J_v − [r_b]× J_ω) q̇；ω 对刚体上每一点都相同，转动部分不改
            jacobian[:, 0:3, :] += torch.bmm(-math_utils.skew_symmetric_matrix(r_b), jacobian[:, 3:, :])
        return jacobian


@configclass
class OffsetCorrectedDiffIKActionCfg(DifferentialInverseKinematicsActionCfg):
    class_type: type = OffsetCorrectedDiffIKAction
