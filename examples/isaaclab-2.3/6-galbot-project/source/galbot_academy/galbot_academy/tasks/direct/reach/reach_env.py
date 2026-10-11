# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""Galbot 单臂 reach 的 Direct 版（6.4.4）。

目标是与 Manager-based 版（Galbot-Reach-v0）语义等价：同一种子、同一动作序列下，观测与奖励逐步一致
（scripts/compare_direct_manager.py 比对）。为此连随机数的消耗顺序也照 Manager 版排：
重置时先采关节扰动（事件），再采命令的重采样时间与目标（命令）。每段对应的管理器写在注释里。
"""

from __future__ import annotations

from collections.abc import Sequence

import torch

from isaaclab.assets import Articulation
from isaaclab.envs import DirectRLEnv
from isaaclab.utils.math import (
    combine_frame_transforms,
    compute_pose_error,
    quat_error_magnitude,
    quat_from_euler_xyz,
    sample_uniform,
)

from galbot_academy.assets.galbot import REACH_ARM, REACH_EE_BODY, REACH_EE_OFFSET_POS, REACH_EE_OFFSET_ROT
from galbot_academy.tasks.manager_based.reach.mdp.tcp import tcp_pose_w

from .reach_env_cfg import GalbotReachDirectEnvCfg

REWARD_TERMS = (  # 与 Manager 版 RewardsCfg 的项名、顺序相同（求和顺序影响浮点结果）
    "end_effector_position_tracking",
    "end_effector_position_tracking_fine_grained",
    "end_effector_orientation_tracking",
    "action_rate",
    "joint_vel",
)


class GalbotReachDirectEnv(DirectRLEnv):
    cfg: GalbotReachDirectEnvCfg

    def __init__(self, cfg: GalbotReachDirectEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)
        self.robot: Articulation = self.scene["robot"]
        self.arm_ids, _ = self.robot.find_joints(f"{REACH_ARM}_arm_joint[1-7]")
        self.ee_id = self.robot.find_bodies(REACH_EE_BODY)[0][0]
        n, d = self.num_envs, self.device
        # 动作（ActionManager）：本步与上一步的原始动作、换算后的关节目标
        self.actions = torch.zeros(n, self.cfg.action_space, device=d)
        self.prev_actions = torch.zeros_like(self.actions)
        self.arm_offset = self.robot.data.default_joint_pos[:, self.arm_ids].clone()
        self.arm_targets = self.arm_offset.clone()
        # 命令（CommandManager）：根坐标系下的目标位姿 (x, y, z, qw, qx, qy, qz)、距下次重采样的时间、误差指标
        # 名字与 UniformPoseCommand 相同，eval_reach.py 两个版本都能读
        self.pose_command_b = torch.zeros(n, 7, device=d)
        self.pose_command_b[:, 3] = 1.0
        self.time_left = torch.zeros(n, device=d)
        self.metrics = {"position_error": torch.zeros(n, device=d), "orientation_error": torch.zeros(n, device=d)}
        self._command_step = 0  # 上一次更新命令时的全局步数，见 _get_observations
        # 奖励（RewardManager）：当前权重（课程会改）与每个回合的分项累计
        self.reward_weights = {
            "end_effector_position_tracking": self.cfg.rew_position,
            "end_effector_position_tracking_fine_grained": self.cfg.rew_position_fine,
            "end_effector_orientation_tracking": self.cfg.rew_orientation,
            "action_rate": self.cfg.rew_action_rate,
            "joint_vel": self.cfg.rew_joint_vel,
        }
        self.episode_sums = {k: torch.zeros(n, device=d) for k in REWARD_TERMS}

    # ---------------- 动作（ActionManager：process_action / apply_action） ----------------

    def _pre_physics_step(self, actions: torch.Tensor):
        self.prev_actions[:] = self.actions
        self.actions[:] = actions
        self.arm_targets = self.actions * self.cfg.action_scale + self.arm_offset

    def _apply_action(self):
        self.robot.set_joint_position_target(self.arm_targets, joint_ids=self.arm_ids)

    # ---------------- 观测（ObservationManager）；命令的定时更新也放在这里 ----------------

    def _get_observations(self) -> dict:
        # Manager 版在"重置之后、算观测之前"调用 command_manager.compute。Direct 的 step() 在这个位置没有单独的钩子，
        # 所以放在观测开头；reset() 也会调用本函数，但那时全局步数没变，不做更新（Manager 版的 reset() 也不调用它）
        if self.common_step_counter != self._command_step:
            self._command_step = self.common_step_counter
            self._update_command(self.step_dt)
        q = self.robot.data
        obs = torch.cat(
            (
                q.joint_pos[:, self.arm_ids] - q.default_joint_pos[:, self.arm_ids],
                q.joint_vel[:, self.arm_ids] - q.default_joint_vel[:, self.arm_ids],
                self.pose_command_b,
                self.actions,
            ),
            dim=-1,
        )
        return {"policy": obs}

    # ---------------- 奖励（RewardManager） ----------------

    def _get_rewards(self) -> torch.Tensor:
        tcp_pos, tcp_quat = self._tcp_pose_w()
        target_pos, target_quat = self._command_w()
        dist = torch.norm(tcp_pos - target_pos, dim=1)
        values = {
            "end_effector_position_tracking": dist,
            "end_effector_position_tracking_fine_grained": 1 - torch.tanh(dist / self.cfg.rew_position_fine_std),
            "end_effector_orientation_tracking": quat_error_magnitude(tcp_quat, target_quat),
            "action_rate": torch.sum(torch.square(self.actions - self.prev_actions), dim=1),
            "joint_vel": torch.sum(torch.square(self.robot.data.joint_vel[:, self.arm_ids]), dim=1),
        }
        reward = torch.zeros(self.num_envs, device=self.device)
        for name in REWARD_TERMS:
            weight = self.reward_weights[name]
            if weight == 0.0:
                continue
            value = values[name] * weight * self.step_dt  # 与 RewardManager 一样乘控制周期（4.14 坑二）
            reward += value
            self.episode_sums[name] += value
        return reward

    # ---------------- 终止（TerminationManager） ----------------

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        time_out = self.episode_length_buf >= self.max_episode_length  # 同 mdp.time_out；官方 Direct Cartpole 用的是 - 1
        return torch.zeros_like(time_out), time_out

    # ---------------- 重置（CurriculumManager → 场景 → EventManager → 各管理器 reset） ----------------

    def _reset_idx(self, env_ids: Sequence[int]):
        # 课程（CurriculumManager.compute）：在场景重置之前
        if self.common_step_counter > self.cfg.curriculum_steps:
            self.reward_weights["action_rate"] = self.cfg.rew_action_rate_final
            self.reward_weights["joint_vel"] = self.cfg.rew_joint_vel_final
        super()._reset_idx(env_ids)  # scene.reset、回合步数清零
        self._reset_robot(env_ids)
        # 日志（RewardManager.reset）：rsl_rl 从 extras["log"] 读
        self.extras["log"] = {}
        for name in REWARD_TERMS:
            self.extras["log"][f"Episode_Reward/{name}"] = torch.mean(self.episode_sums[name][env_ids]) / self.max_episode_length_s
            self.episode_sums[name][env_ids] = 0.0
        # 动作（ActionManager.reset）
        self.actions[env_ids] = 0.0
        self.prev_actions[env_ids] = 0.0
        # 命令（CommandManager.reset）
        for name, value in self.metrics.items():
            self.extras["log"][f"Metrics/ee_pose/{name}"] = torch.mean(value[env_ids]).item()
            value[env_ids] = 0.0
        self._resample_command(env_ids)

    def _reset_robot(self, env_ids: torch.Tensor):
        """事件 reset_scene_to_default(reset_joint_targets=True) + reset_joints_by_offset（只扰动右臂）。"""
        root = self.robot.data.default_root_state[env_ids].clone()
        root[:, 0:3] += self.scene.env_origins[env_ids]
        self.robot.write_root_pose_to_sim(root[:, :7], env_ids=env_ids)
        self.robot.write_root_velocity_to_sim(root[:, 7:], env_ids=env_ids)
        joint_pos = self.robot.data.default_joint_pos[env_ids].clone()
        joint_vel = self.robot.data.default_joint_vel[env_ids].clone()
        self.robot.write_joint_state_to_sim(joint_pos, joint_vel, env_ids=env_ids)
        self.robot.set_joint_position_target(joint_pos, env_ids=env_ids)
        self.robot.set_joint_velocity_target(joint_vel, env_ids=env_ids)
        # 右臂：默认位置加均匀扰动，速度扰动范围为 0（仍采样一次，保持随机数消耗与 Manager 版相同）
        ids = env_ids[:, None]
        arm_pos = self.robot.data.default_joint_pos[ids, self.arm_ids].clone()
        arm_vel = self.robot.data.default_joint_vel[ids, self.arm_ids].clone()
        arm_pos += sample_uniform(*self.cfg.reset_position_range, arm_pos.shape, arm_pos.device)
        arm_vel += sample_uniform(0.0, 0.0, arm_vel.shape, arm_vel.device)
        limits = self.robot.data.soft_joint_pos_limits[ids, self.arm_ids]
        arm_pos = arm_pos.clamp_(limits[..., 0], limits[..., 1])
        vel_limits = self.robot.data.soft_joint_vel_limits[ids, self.arm_ids]
        arm_vel = arm_vel.clamp_(-vel_limits, vel_limits)
        self.robot.write_joint_state_to_sim(arm_pos, arm_vel, joint_ids=self.arm_ids, env_ids=env_ids)

    # ---------------- 命令（CommandManager：UniformPoseCommand 的 compute / _resample） ----------------

    def _update_command(self, dt: float):
        tcp_pos, tcp_quat = self._tcp_pose_w()
        target_pos, target_quat = self._command_w()
        pos_err, rot_err = compute_pose_error(target_pos, target_quat, tcp_pos, tcp_quat)
        self.metrics["position_error"] = pos_err.norm(dim=-1)
        self.metrics["orientation_error"] = rot_err.norm(dim=-1)
        self.time_left -= dt
        env_ids = (self.time_left <= 0.0).nonzero().flatten()
        if len(env_ids) > 0:
            self._resample_command(env_ids)

    def _resample_command(self, env_ids: torch.Tensor):
        # 随机数的调用方式照抄 CommandTerm._resample 与 UniformPoseCommand._resample_command：
        # 先采重采样时间，再按 x、y、z、roll、pitch、yaw 的顺序各采一次（姿态范围上下限相同，也照样采）
        self.time_left[env_ids] = self.time_left[env_ids].uniform_(*self.cfg.resampling_time_range)
        r = torch.empty(len(env_ids), device=self.device)
        self.pose_command_b[env_ids, 0] = r.uniform_(*self.cfg.pos_x)
        self.pose_command_b[env_ids, 1] = r.uniform_(*self.cfg.pos_y)
        self.pose_command_b[env_ids, 2] = r.uniform_(*self.cfg.pos_z)
        euler = torch.zeros_like(self.pose_command_b[env_ids, :3])
        for i, a in enumerate(self.cfg.target_rpy):
            euler[:, i].uniform_(a, a)
        self.pose_command_b[env_ids, 3:] = quat_from_euler_xyz(euler[:, 0], euler[:, 1], euler[:, 2])

    # ---------------- 工具 ----------------

    def _tcp_pose_w(self) -> tuple[torch.Tensor, torch.Tensor]:
        return tcp_pose_w(self.robot, self.ee_id, REACH_EE_OFFSET_POS, REACH_EE_OFFSET_ROT)

    def _command_w(self) -> tuple[torch.Tensor, torch.Tensor]:
        d = self.robot.data
        return combine_frame_transforms(d.root_pos_w, d.root_quat_w, self.pose_command_b[:, :3], self.pose_command_b[:, 3:])
