# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-09
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""夹爪能不能夹住方块（6.4.3）：不训练，只检查抓取的物理。

在 Galbot-Lift-v0 里，右臂保持默认姿态（悬在空中），每个环境做同一件事：
1. 夹爪张开；把方块"钉"在 TCP 处（每个控制步都重写方块位姿、清零速度），姿态与 TCP 一致；
2. 下令闭合，方块仍钉住，用两个指尖的间距判断何时夹到方块，记下用时；
3. 松开方块，只靠夹持力，观察 3 s：方块相对 TCP 滑了多少、有没有掉。

可以改方块边长、夹爪刚度、机器人的求解器迭代次数，对照哪些设置能夹住。用法::

    python scripts/check_grasp.py --headless
    python scripts/check_grasp.py --headless --cube_size 0.04 --robot_pos_iters 32
"""

import argparse

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="检查夹爪能否夹住方块")
parser.add_argument("--num_envs", type=int, default=16)
parser.add_argument("--cube_size", type=float, default=None, help="方块边长（m），默认用 scenes/lift.py 的 CUBE_SIZE")
parser.add_argument("--cube_mass", type=float, default=None, help="方块质量（kg）")
parser.add_argument("--gripper_stiffness", type=float, default=None, help="夹爪主动关节的刚度，默认用 drives.py")
parser.add_argument("--robot_pos_iters", type=int, default=None, help="机器人的位置迭代次数，默认 16（galbot.py）")
parser.add_argument("--cube_pos_iters", type=int, default=None, help="方块的位置迭代次数，默认 16（scenes/lift.py）")
parser.add_argument("--hold_s", type=float, default=3.0, help="松开方块后观察的时长（s）")
parser.add_argument("--open_q", type=float, default=None, help="夹爪\"张开\"时的目标角（rad），默认用 lift_env_cfg.GRIPPER_OPEN")
parser.add_argument("--accel_sweep", action="store_true",
                    help="夹住后给方块逐级加外力 F = m·a，等效于手臂按加速度 a 运动，找出滑脱的加速度")
parser.add_argument("--keep_open", action="store_true", help="对照：始终不闭合夹爪，方块应当掉落")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch

import galbot_academy.tasks  # noqa: F401  注册任务
from isaaclab_tasks.utils import parse_env_cfg


def main() -> None:
    cfg = parse_env_cfg("Galbot-Lift-v0", device=args.device, num_envs=args.num_envs)
    cfg.events.reset_object_position = None  # 方块位置由本脚本写入
    cfg.terminations.object_dropping = None  # 方块本来就悬在空中
    cfg.rewards.object_dropping = None  # 掉落惩罚引用了上面那个终止项，一起去掉
    cfg.commands.object_pose.debug_vis = False
    cfg.episode_length_s = 60.0  # 整个检查在一个回合里做完，不让超时重置打断
    if args.cube_size is not None:
        cfg.scene.object.spawn.size = (args.cube_size,) * 3
    if args.cube_mass is not None:
        cfg.scene.object.spawn.mass_props.mass = args.cube_mass
    if args.gripper_stiffness is not None:
        cfg.scene.robot.actuators["grippers"].stiffness = args.gripper_stiffness
    if args.robot_pos_iters is not None:
        cfg.scene.robot.spawn.articulation_props.solver_position_iteration_count = args.robot_pos_iters
    if args.cube_pos_iters is not None:
        cfg.scene.object.spawn.rigid_props.solver_position_iteration_count = args.cube_pos_iters
    if args.open_q is not None:
        cfg.actions.gripper_action.open_command_expr = {"right_gripper_joint": args.open_q}
    size = cfg.scene.object.spawn.size[0]

    env = gym.make("Galbot-Lift-v0", cfg=cfg).unwrapped
    env.reset()
    robot, obj, ee = env.scene["robot"], env.scene["object"], env.scene["ee_frame"]
    g = robot.find_joints("right_gripper_joint")[0][0]
    dt = env.step_dt
    n = env.num_envs
    act = torch.zeros(n, env.action_manager.total_action_dim, device=env.device)  # 臂动作 0 = 保持默认姿态

    def pin_cube():
        pose = torch.cat([ee.data.target_pos_w[:, 0], ee.data.target_quat_w[:, 0]], dim=-1)
        obj.write_root_pose_to_sim(pose)
        obj.write_root_velocity_to_sim(torch.zeros(n, 6, device=env.device))

    # 1. 张开，钉住方块，等臂与夹爪稳定 2 s（夹爪从 0 走到张开目标需要时间）
    act[:, -1] = 1.0
    for _ in range(int(2.0 / dt)):
        pin_cube()
        env.step(act)
    fl, fr = (robot.find_bodies(f"right_gripper_{side}_finger_link")[0][0] for side in ("l", "r"))

    def finger_gap():
        """两个指尖刚体原点之间的距离 (N,)。"""
        return (robot.data.body_pos_w[:, fl] - robot.data.body_pos_w[:, fr]).norm(dim=-1)

    gap_open = finger_gap()
    # 2. 闭合，方块仍钉住（--keep_open 时保持张开，作为对照）。用指尖间距判断何时夹到方块：
    #    间距 0.2 s 内缩小不到 0.5 mm 即算停下。不用夹爪关节角判断：主动关节在指尖被挡住后仍会继续转
    #    （指尖由 mimic 约束带动，约束被拉伸），本脚本实测停在 1.68–1.70 rad，几乎就是完全闭合的 1.703。
    act[:, -1] = 1.0 if args.keep_open else -1.0
    gaps, q_hist, contact_t = [], [], torch.full((n,), float("nan"), device=env.device)
    win = max(1, int(0.2 / dt))
    for k in range(int(5.0 / dt)):
        pin_cube()
        env.step(act)
        gaps.append(finger_gap())
        q_hist.append(robot.data.joint_pos[:, g].clone())
        if k >= win:
            stalled = (gaps[-1 - win] - gaps[-1]) < 0.0005
            newly = torch.isnan(contact_t) & stalled & (gaps[-1] < gap_open - 0.005)
            contact_t[newly] = (k + 1 - win) * dt  # 记停下的起点
    q_stop = robot.data.joint_pos[:, g].clone()
    qv_max = torch.stack(q_hist).diff(dim=0).abs().max().item() / dt
    # 3. 松开方块，观察
    rel0 = obj.data.root_pos_w - ee.data.target_pos_w[:, 0]
    max_slip = torch.zeros(n, device=env.device)
    for _ in range(int(args.hold_s / dt)):
        env.step(act)
        slip = (obj.data.root_pos_w - ee.data.target_pos_w[:, 0] - rel0).norm(dim=-1)
        max_slip = torch.maximum(max_slip, slip)
    held = max_slip < 0.01

    if args.accel_sweep:
        # 4. 等效加速度扫描（达朗贝尔原理）：手臂以加速度 a 运动时，方块相对夹爪受到 -m·a 的惯性力。这里让手臂不动，
        #    直接给方块施加外力来模拟，忽略手臂自身动力学的影响（推断，只用来比较量级）。环境分四组，施力方向分别为
        #    世界 -z（等效于向上加速举起）、+x、+y、+z；每级持续 0.5 s，滑移超过 1 cm 即判定为滑脱
        mass = cfg.scene.object.spawn.mass_props.mass
        dirs = torch.tensor([[0, 0, -1], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=torch.float32, device=env.device)
        d = dirs[torch.arange(n, device=env.device) % 4]
        levels = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
        slip_at = torch.full((n,), float("nan"), device=env.device)
        rel0 = obj.data.root_pos_w - ee.data.target_pos_w[:, 0]
        for a in levels:
            obj.set_external_force_and_torque((mass * a * d).unsqueeze(1), torch.zeros(n, 1, 3, device=env.device))
            for _ in range(int(0.5 / dt)):
                env.step(act)
                slip = (obj.data.root_pos_w - ee.data.target_pos_w[:, 0] - rel0).norm(dim=-1)
                slip_at[torch.isnan(slip_at) & (slip > 0.01)] = a
        names = ["-z（向上加速）", "+x", "+y", "+z（向下加速）"]
        for i, name in enumerate(names):
            v = slip_at[i::4]
            ok = v[~torch.isnan(v)]
            print(f"[SWEEP] 方向 {name}：滑脱时的等效加速度 "
                  + (f"中位数 {ok.median().item():.1f} m/s²（{len(ok)}/{len(v)} 个环境在 {levels[-1]} m/s² 内滑脱）" if len(ok) else f"在 {levels[-1]} m/s² 内都没有滑脱"))
    print(f"[INFO] cube {size * 100:.1f} cm / {cfg.scene.object.spawn.mass_props.mass} kg, "
          f"gripper stiffness {cfg.scene.robot.actuators['grippers'].stiffness}, "
          f"robot pos iters {cfg.scene.robot.spawn.articulation_props.solver_position_iteration_count}, "
          f"cube pos iters {cfg.scene.object.spawn.rigid_props.solver_position_iteration_count}")
    print(f"[INFO] 夹爪最大角速度 {qv_max:.2f} rad/s；张开时指尖间距 {gap_open.mean() * 100:.1f} cm；"
          f"从下令闭合到夹到方块 {torch.nanmean(contact_t):.2f} s（未夹到 {int(torch.isnan(contact_t).sum())}/{n}）；"
          f"主动关节最终 {q_stop.mean():.3f} rad")
    print(f"[INFO] 松开后 {args.hold_s:.0f} s：最大滑移 {max_slip.mean() * 100:.2f} cm（最大 {max_slip.max() * 100:.2f} cm），"
          f"夹住（滑移 < 1 cm）{int(held.sum())}/{n}；指尖刚体间距 {finger_gap().mean() * 100:.1f} cm")
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
