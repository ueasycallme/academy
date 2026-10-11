# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
"""pick-place 的 Mimic 接口（6.4.6 实现，6.4.7 使用）：ManagerBasedRLMimicEnv 要求的方法（4.19"任务侧需要什么"）。

所有位姿都在机器人根坐标系下：末端取观测里的 eef_pos / eef_quat（FrameTransformer，源是根），
物体也换算到根坐标系。官方 Galbot stack 的 Mimic 环境同样把物体位姿换到机器人底座坐标系
（isaaclab_mimic/envs/galbot_stack_rmp_rel_mimic_env.py），因为那台 One Charlie 的根不在环境原点。
本项目的根就在环境原点、不旋转，换不换结果相同；这里照样换，免得以后挪动机器人时末端与物体不在同一坐标系。
"""

from __future__ import annotations

from collections.abc import Sequence

import torch

import isaaclab.utils.math as math_utils
from isaaclab.envs import ManagerBasedRLMimicEnv


class GalbotPickPlaceMimicEnv(ManagerBasedRLMimicEnv):
    """Galbot-PickPlace-IK-Rel-Mimic-v0 的环境类。只有一个末端（右臂），名字取 subtask_configs 的唯一键。"""

    @property
    def _eef_name(self) -> str:
        return next(iter(self.cfg.subtask_configs))

    def get_robot_eef_pose(self, eef_name: str, env_ids: Sequence[int] | None = None) -> torch.Tensor:
        """TCP 位姿 (len(env_ids), 4, 4)，根坐标系；与 IK 动作项跟踪的是同一个点。"""
        ids = slice(None) if env_ids is None else env_ids
        pos = self.obs_buf["policy"]["eef_pos"][ids]
        quat = self.obs_buf["policy"]["eef_quat"][ids]
        return math_utils.make_pose(pos, math_utils.matrix_from_quat(quat))

    def target_eef_pose_to_action(
        self,
        target_eef_pose_dict: dict,
        gripper_action_dict: dict,
        action_noise_dict: dict | None = None,
        env_id: int = 0,
    ) -> torch.Tensor:
        """目标 TCP 位姿 → 7 维动作：[Δ位置 3, Δ轴角 3, 夹爪 1]。

        IK 动作项（相对模式）把 Δ位置加到当前位置上、把 Δ轴角对应的转动左乘到当前姿态上（4.20"方向在根坐标系里"），
        所以这里取 Δp = p_target − p_now，ΔR = R_target · R_nowᵀ。动作项的 scale 是 1.0，不用再除。
        """
        name = self._eef_name
        target = target_eef_pose_dict[name]
        now = self.get_robot_eef_pose(name, env_ids=[env_id])[0]
        p_t, r_t = math_utils.unmake_pose(target)
        p_n, r_n = math_utils.unmake_pose(now)
        d_rot = math_utils.axis_angle_from_quat(math_utils.quat_from_matrix(r_t @ r_n.transpose(-1, -2)))
        pose_action = torch.cat([p_t - p_n, d_rot], dim=0)
        if action_noise_dict is not None:
            pose_action = pose_action + action_noise_dict[name] * torch.randn_like(pose_action)
            pose_action = torch.clamp(pose_action, -1.0, 1.0)
        return torch.cat([pose_action, gripper_action_dict[name]], dim=0)

    def action_to_target_eef_pose(self, action: torch.Tensor) -> dict[str, torch.Tensor]:
        """7 维动作 → 这一步 IK 动作项要追的目标 TCP 位姿 (N, 4, 4)。是上一个方法的逆。"""
        name = self._eef_name
        p_n, r_n = math_utils.unmake_pose(self.get_robot_eef_pose(name))
        d_pos, d_rot = action[:, 0:3], action[:, 3:6]
        angle = torch.linalg.norm(d_rot, dim=-1)
        axis = torch.where(angle[:, None] > 1e-9, d_rot / angle.clamp_min(1e-9)[:, None], torch.zeros_like(d_rot))
        r_delta = math_utils.matrix_from_quat(math_utils.quat_from_angle_axis(angle, axis))
        return {name: math_utils.make_pose(p_n + d_pos, r_delta @ r_n)}

    def actions_to_gripper_actions(self, actions: torch.Tensor) -> dict[str, torch.Tensor]:
        """动作的最后一维是夹爪（< 0 闭合）。

        基类 docstring 写的形状是 (N, T, 7)，但生成器（datagen_info_pool.py L114）传进来的是一条示范的 (T, 7)，
        所以按最后一维取，两种形状都对（6.4.7 坑）。
        """
        return {self._eef_name: actions[..., -1:]}

    def get_object_poses(self, env_ids: Sequence[int] | None = None) -> dict[str, torch.Tensor]:
        """方块与放置点在机器人根坐标系下的位姿 (len(env_ids), 4, 4)。"""
        ids = slice(None) if env_ids is None else env_ids
        robot = self.scene["robot"].data
        poses = {}
        for name in ("object", "target"):
            obj = self.scene[name].data
            pos, quat = math_utils.subtract_frame_transforms(
                robot.root_pos_w[ids], robot.root_quat_w[ids], obj.root_pos_w[ids], obj.root_quat_w[ids]
            )
            poses[name] = math_utils.make_pose(pos, math_utils.matrix_from_quat(quat))
        return poses

    def get_subtask_term_signals(self, env_ids: Sequence[int] | None = None) -> dict[str, torch.Tensor]:
        """子任务完成信号：读观测组 subtask_terms（pick_place_env_cfg.py）。"""
        ids = slice(None) if env_ids is None else env_ids
        return {"grasp": self.obs_buf["subtask_terms"]["grasp"][ids]}
