# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""哪些抓取姿态右臂够得着（6.4.6 表 2）。姿态 = 接近方向（从竖直向下倾斜 θ、朝向 φ）+ 水平的闭合轴（TCP y）。
每个候选：重置 → 闭环移到预抓点（方块中心沿接近方向后退 10 cm，240 步）→ 再移到方块中心（150 步），
记位置 / 姿态误差、右臂关节离限位的最小余量，以及方块被推动了多远。约 11 分钟。

    python scripts/sweep_grasp_pose.py --headless
"""
import argparse, math
from isaaclab.app import AppLauncher
p = argparse.ArgumentParser(); AppLauncher.add_app_launcher_args(p); args = p.parse_args()
app = AppLauncher(args).app
import gymnasium as gym, torch
import isaaclab.utils.math as mu
import galbot_academy.tasks  # noqa
from isaaclab_tasks.utils import parse_env_cfg

cfg = parse_env_cfg("Galbot-PickPlace-IK-Rel-v0", device=args.device, num_envs=1)
cfg.events.reset_object_position = None  # 方块固定在桌面中心，各候选可比
env = gym.make("Galbot-PickPlace-IK-Rel-v0", cfg=cfg).unwrapped
rob = env.scene["robot"]; dev = env.device
ids = [rob.joint_names.index(f"right_arm_joint{i}") for i in range(1, 8)]


def rot_for(theta, phi, sign):
    a = torch.tensor([math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), -math.cos(theta)], device=dev)
    c = sign * torch.tensor([-math.sin(phi), math.cos(phi), 0.0], device=dev)
    return torch.stack([a, c, torch.linalg.cross(a, c)], dim=1)


def drive(obs, goal, Rd, steps):
    for _ in range(steps):
        pcur, q = obs["policy"]["eef_pos"][0], obs["policy"]["eef_quat"][0]
        R = mu.matrix_from_quat(q[None])[0]
        dp = (goal - pcur).clamp(-0.01, 0.01)
        dr = mu.axis_angle_from_quat(mu.quat_from_matrix((Rd @ R.T)[None]))[0]
        n = torch.linalg.norm(dr)
        if n > 0.05:
            dr = dr / n * 0.05
        obs, *_ = env.step(torch.cat([dp, dr, torch.ones(1, device=dev)])[None])
    pcur, q = obs["policy"]["eef_pos"][0], obs["policy"]["eef_quat"][0]
    R = mu.matrix_from_quat(q[None])[0]
    perr = torch.linalg.norm(goal - pcur).item() * 100
    rerr = torch.acos(((torch.trace(Rd @ R.T) - 1) / 2).clamp(-1, 1)).item()
    lim = rob.data.soft_joint_pos_limits[0, ids]; qq = rob.data.joint_pos[0, ids]
    margin = torch.minimum(qq - lim[:, 0], lim[:, 1] - qq).min().item()
    return obs, perr, rerr, margin


for th in (0, 15, 30, 45, 60, 75, 90):
    for ph in (-45, 0, 45):
        for sg in (1, -1):
            obs, _ = env.reset()
            obj = obs["policy"]["object_position"][0]
            Rd = rot_for(math.radians(th), math.radians(ph), sg)
            # 沿接近方向后退：上方点 = 方块中心 − 接近方向 × 0.10
            above = obj - Rd[:, 0] * 0.10
            obs, pe1, re1, m1 = drive(obs, above, Rd, 240)
            obs, pe2, re2, m2 = drive(obs, obj.clone(), Rd, 150)
            moved = torch.linalg.norm(obs["policy"]["object_position"][0] - obj).item() * 100
            print(f"[sweep] θ={th:2d} φ={ph:+3d} s={sg:+d} | 预抓点 {pe1:5.1f} cm {re1:.3f} rad 余量 {m1:+.2f} | 抓取点 {pe2:5.1f} cm {re2:.3f} rad 余量 {m2:+.2f} | 方块被推动 {moved:.1f} cm", flush=True)
env.close(); app.close()
