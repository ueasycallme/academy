# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""用脚本化示教录 pick-place 示范（6.4.6）：录制管线与 scripts/tools/record_demos.py 相同，只是"手"换成了分段控制器。

环境配置的改法逐条照搬 record_demos.py 的 create_environment_config()（4.20）：1 个环境、取出 success 项在主循环里判断、
关掉超时、挂 ActionStateRecorderManagerCfg、只导出成功的回合；成功要连续 --num_success_steps 步（默认 10）。
与 record_demos.py 的不同：
- 动作来自 PickPlaceTeacher，而不是 teleop_interface.advance()；输出同样是 7 维 [Δ位置, Δ轴角, 夹爪]；
- 一次尝试超过 --max_steps 步还没成功、或方块掉下桌，就丢弃重来（record_demos.py 里这要人按 R）；
- 不限速：没有人在看，限速只会变慢，录下的数据与限速与否无关。

    python scripts/record_pick_place.py --headless --num_demos 10 --dataset_file ./datasets/galbot_pick_place.hdf5
"""

import argparse
import os
import statistics
import sys
import time

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="脚本化示教录 Galbot pick-place 示范")
parser.add_argument("--task", default="Galbot-PickPlace-IK-Rel-v0")
parser.add_argument("--num_demos", type=int, default=10, help="要录的成功示范条数")
parser.add_argument("--max_attempts", type=int, default=0, help="最多尝试多少次，0 表示 num_demos 的 3 倍")
parser.add_argument("--dataset_file", default="./datasets/galbot_pick_place.hdf5")
parser.add_argument("--num_success_steps", type=int, default=10, help="连续满足 success 多少步才算一条示范（同 record_demos.py）")
parser.add_argument("--max_steps", type=int, default=900, help="一次尝试的步数上限（30 Hz，900 步 = 30 s）")
parser.add_argument("--approach_deg", type=float, default=60.0, help="接近方向与竖直向下的夹角（°），见 6.4.6\"抓取姿态\"")
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--no_export", action="store_true", help="只统计成功率，不写文件（调控制器用）")
parser.add_argument("--robot_gravity", action="store_true", help="对照：打开机器人的重力（环境默认关掉，6.4.6 坑二）")
parser.add_argument("--stock_ik", action="store_true", help="对照：换回 Isaac Lab 原版 DifferentialInverseKinematicsAction（6.4.6 坑一）")
parser.add_argument("--trace", action="store_true", help="每 15 步打印段名、误差、方块相对 TCP 的位置、右臂关节离限位的最小余量")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch

import isaaclab.utils.math as math_utils
from isaaclab.envs.mdp.recorders.recorders_cfg import ActionStateRecorderManagerCfg
from isaaclab.managers import DatasetExportMode

import galbot_academy.tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg
from pick_place_teacher import PickPlaceTeacher  # 同目录；6.3.1 起与 sweep_physics.py 共用


def main() -> None:
    out_dir, out_name = os.path.split(os.path.abspath(args.dataset_file))
    os.makedirs(out_dir, exist_ok=True)
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=1)
    env_cfg.env_name = args.task
    env_cfg.seed = args.seed
    if args.stock_ik:
        from isaaclab.envs.mdp.actions.task_space_actions import DifferentialInverseKinematicsAction

        env_cfg.actions.arm_action.class_type = DifferentialInverseKinematicsAction
    if args.robot_gravity:
        env_cfg.scene.robot.spawn.rigid_props.disable_gravity = False
    # —— 以下照 record_demos.py 的 create_environment_config() ——
    success_term = env_cfg.terminations.success
    env_cfg.terminations.success = None
    env_cfg.terminations.time_out = None
    env_cfg.observations.policy.concatenate_terms = False
    env_cfg.recorders = ActionStateRecorderManagerCfg()
    env_cfg.recorders.dataset_export_dir_path = out_dir
    env_cfg.recorders.dataset_filename = os.path.splitext(out_name)[0]
    env_cfg.recorders.dataset_export_mode = (
        DatasetExportMode.EXPORT_NONE if args.no_export else DatasetExportMode.EXPORT_SUCCEEDED_ONLY
    )
    env = gym.make(args.task, cfg=env_cfg).unwrapped
    gripper_close_q = env.cfg.actions.gripper_action.close_command_expr[next(iter(env.cfg.actions.gripper_action.close_command_expr))]
    teacher = PickPlaceTeacher(env.device, args.approach_deg, gripper_close_q)

    def handle_reset():
        # 与 record_demos.py 的 handle_reset() 相同：丢弃当前录到的这一条
        env.sim.reset()
        env.recorder_manager.reset()
        obs, _ = env.reset()
        teacher.reset()
        return obs

    max_attempts = args.max_attempts or 3 * args.num_demos
    obs = handle_reset()
    obj0 = obs["policy"]["object_position"][0].clone()
    n_ok, n_try, lengths, fails = 0, 0, [], {}
    steps, ok_steps = 0, 0
    t0 = time.monotonic()
    with torch.inference_mode():
        while n_ok < args.num_demos and n_try < max_attempts:
            obs, *_ = env.step(teacher.act(obs))
            steps += 1
            if args.trace and steps % 15 == 0:
                o = obs["policy"]
                R = math_utils.matrix_from_quat(o["eef_quat"])[0]
                rel = R.T @ (o["object_position"][0] - o["eef_pos"][0])  # 方块中心在 TCP 坐标系里
                rob = env.scene["robot"]
                ids = rob.find_joints("right_arm_joint[1-7]")[0]
                lim, qq = rob.data.soft_joint_pos_limits[0, ids], rob.data.joint_pos[0, ids]
                m = torch.minimum(qq - lim[:, 0], lim[:, 1] - qq)
                print(f"[trace] {steps:4d} {teacher.phase:8s} err {teacher.last_err * 100:5.1f} cm  方块@TCP {[round(x * 100, 1) for x in rel.tolist()]} cm  "
                      f"夹爪 {o['gripper_pos'][0, 0].item():.2f}  余量最小 j{int(m.argmin()) + 1} {m.min().item():+.2f}  "
                      f"TCP {[round(x, 3) for x in o['eef_pos'][0].tolist()]}  |q̇| {rob.data.joint_vel[0, ids].abs().max().item():.3f}  "
                      f"q目标−q {(rob.data.joint_pos_target[0, ids] - qq).abs().max().item():.3f}", flush=True)
            # 与 record_demos.py 的 process_success_condition() 相同：连续 num_success_steps 步成功才导出
            if bool(success_term.func(env, **success_term.params)[0]):
                ok_steps += 1
            else:
                ok_steps = 0
            dropped = bool(env.termination_manager.get_term("object_dropping")[0])
            if ok_steps >= args.num_success_steps:
                env.recorder_manager.record_pre_reset([0], force_export_or_skip=False)
                env.recorder_manager.set_success_to_episodes([0], torch.tensor([[True]], dtype=torch.bool, device=env.device))
                env.recorder_manager.export_episodes([0])
                n_ok += 1
                n_try += 1
                lengths.append(steps)
                print(f"[rec] 第 {n_try} 次尝试：成功，{steps} 步（{steps / 30:.1f} s），已录 {n_ok} 条", flush=True)
            elif dropped or teacher.timed_out() or steps >= args.max_steps:
                n_try += 1
                why = "方块掉落" if dropped else f"{teacher.phase} 段超时"
                o = obs["policy"]
                print(f"[rec]   诊断：段内误差 {teacher.last_err * 100:.1f} cm，方块离初始位置 "
                      f"{torch.linalg.norm(o['object_position'][0] - obj0).item() * 100:.1f} cm，夹爪 {o['gripper_pos'][0, 0].item():.2f} rad", flush=True)
                fails[why] = fails.get(why, 0) + 1
                print(f"[rec] 第 {n_try} 次尝试：失败（{why}），{steps} 步", flush=True)
            else:
                continue
            obs = handle_reset()
            obj0 = obs["policy"]["object_position"][0].clone()
            steps, ok_steps = 0, 0
    wall = time.monotonic() - t0
    print(f"[rec] 成功 {n_ok} / 尝试 {n_try}（{100 * n_ok / max(n_try, 1):.0f}%），失败原因 {fails}；墙上 {wall:.0f} s", flush=True)
    if lengths:
        print(f"[rec] 成功示范长度（步）：最短 {min(lengths)}，中位 {statistics.median(lengths)}，最长 {max(lengths)}", flush=True)
    if not args.no_export:
        print(f"[rec] 导出到 {os.path.join(out_dir, out_name)}", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
