# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""以 TCP 为末端的位姿命令（6.4.1；3.0 EA 版，8.5）。

Isaac Lab 的 UniformPoseCommand 用一个刚体的原点算误差与画"当前位姿"标记。Galbot 的 TCP 在转换时并进了
right_arm_link7，离它的原点 0.256 m（6.2.1），所以这里只改两处：误差指标与当前位姿标记都换成"刚体 + 偏移"。
目标的采样方式不变。

3.0：这个实现类不能在 Kit 启动前导入（会提前加载 pip 版的 pxr，Kit 随后起不来），
所以配置类单独放在 commands_cfg.py，用字符串指向这里，由 Isaac Lab 在环境创建时再导入。
"""

from isaaclab.envs.mdp.commands.pose_command import UniformPoseCommand
from isaaclab.utils.math import combine_frame_transforms, compute_pose_error

from .tcp import tcp_pose_w


class TcpPoseCommand(UniformPoseCommand):
    """与 UniformPoseCommand 相同，只是"当前末端"取 TCP。"""

    cfg: "TcpPoseCommandCfg"  # noqa: F821  配置类在 commands_cfg.py

    def _tcp(self):
        return tcp_pose_w(self.robot, self.body_idx, self.cfg.offset_pos, self.cfg.offset_rot)

    # 3.0：父类把误差计算拆到 _compute_error（_update_metrics 调用它，并做成功统计），这里只改它
    def _compute_error(self):
        self.pose_command_w[:, :3], self.pose_command_w[:, 3:] = combine_frame_transforms(
            self.robot.data.root_pos_w.torch,  # 3.0：data.* 是 ProxyArray，用 .torch 取张量
            self.robot.data.root_quat_w.torch,
            self.pose_command_b[:, :3],
            self.pose_command_b[:, 3:],
        )
        pos, quat = self._tcp()
        pos_error, rot_error = compute_pose_error(self.pose_command_w[:, :3], self.pose_command_w[:, 3:], pos, quat)
        return pos_error.norm(dim=-1), rot_error.norm(dim=-1)

    def _debug_vis_callback(self, event):
        if not self.robot.is_initialized:
            return
        env_ids = self._env.scene._ALL_INDICES  # 3.0：visualize 需要 environment_ids
        self.goal_pose_visualizer.visualize(self.pose_command_w[:, :3], self.pose_command_w[:, 3:], environment_ids=env_ids)
        pos, quat = self._tcp()
        self.current_pose_visualizer.visualize(pos, quat, environment_ids=env_ids)
