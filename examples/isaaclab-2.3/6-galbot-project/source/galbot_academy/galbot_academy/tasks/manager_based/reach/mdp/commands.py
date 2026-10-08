# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-08
"""以 TCP 为末端的位姿命令（6.4.1）。

Isaac Lab 的 UniformPoseCommand 用一个刚体的原点算误差与画"当前位姿"标记。Galbot 的 TCP 在转换时并进了
right_arm_link7，离它的原点 0.256 m（6.2.1），所以这里只改两处：误差指标与当前位姿标记都换成"刚体 + 偏移"。
目标的采样方式不变。
"""

from dataclasses import MISSING

from isaaclab.envs.mdp.commands import UniformPoseCommand, UniformPoseCommandCfg
from isaaclab.utils import configclass
from isaaclab.utils.math import combine_frame_transforms, compute_pose_error

from .tcp import tcp_pose_w


class TcpPoseCommand(UniformPoseCommand):
    """与 UniformPoseCommand 相同，只是"当前末端"取 TCP。"""

    cfg: "TcpPoseCommandCfg"

    def _tcp(self):
        return tcp_pose_w(self.robot, self.body_idx, self.cfg.offset_pos, self.cfg.offset_rot)

    def _update_metrics(self):
        self.pose_command_w[:, :3], self.pose_command_w[:, 3:] = combine_frame_transforms(
            self.robot.data.root_pos_w, self.robot.data.root_quat_w, self.pose_command_b[:, :3], self.pose_command_b[:, 3:]
        )
        pos, quat = self._tcp()
        pos_error, rot_error = compute_pose_error(self.pose_command_w[:, :3], self.pose_command_w[:, 3:], pos, quat)
        self.metrics["position_error"] = pos_error.norm(dim=-1)
        self.metrics["orientation_error"] = rot_error.norm(dim=-1)

    def _debug_vis_callback(self, event):
        if not self.robot.is_initialized:
            return
        self.goal_pose_visualizer.visualize(self.pose_command_w[:, :3], self.pose_command_w[:, 3:])
        pos, quat = self._tcp()
        self.current_pose_visualizer.visualize(pos, quat)


@configclass
class TcpPoseCommandCfg(UniformPoseCommandCfg):
    """UniformPoseCommandCfg 加上 TCP 相对 body_name 的偏移。"""

    class_type: type = TcpPoseCommand
    offset_pos: tuple[float, float, float] = MISSING
    offset_rot: tuple[float, float, float, float] = MISSING
