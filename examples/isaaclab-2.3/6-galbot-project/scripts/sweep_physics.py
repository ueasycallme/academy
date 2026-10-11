# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""物理参数的稳定性探针（6.3.1）：每次只改一项物理参数，用 6.4.6 的示教控制器做固定的 N 次抓取，记稳定性与代价。

两种模式：
- probe（默认）：1 个环境，示教控制器做 --attempts 次 pick-place（种子固定，所以每组的方块与放置垫位置序列相同）。
  每次记：是否成功；举起到放下之间方块相对 TCP 的最大滑移（6.4.6 trace 的口径：方块中心在 TCP 坐标系里的位置）；
  方块是否弹飞（速度 > 2 m/s）、穿透（中心低于桌面静止高度 1 cm 以上而没有掉下桌）、出现 NaN；每个控制步的墙上时间。
- buffers：--num_envs 个环境、零动作跑 --steps 步，看 PhysX 的 GPU 缓冲会不会溢出（溢出时 PhysX 打印错误，进程日志里 grep）。

    python scripts/sweep_physics.py --headless --dt 1/120 --decimation 4           # 主线默认
    python scripts/sweep_physics.py --headless --pos_iters 4                         # 求解器迭代
    python scripts/sweep_physics.py --headless --contact_offset 0.002 --rest_offset 0
    python scripts/sweep_physics.py --headless --mode buffers --num_envs 1024 --gpu_max_rigid_patch_count 4096
"""

import argparse
import math
import sys
import time
from fractions import Fraction

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="物理参数稳定性探针")
parser.add_argument("--task", default="Galbot-PickPlace-IK-Rel-v0")
parser.add_argument("--mode", choices=["probe", "buffers"], default="probe")
parser.add_argument("--attempts", type=int, default=20)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--dt", default=None, help="物理步长，如 1/240；不给则用任务默认（1/120）")
parser.add_argument("--decimation", type=int, default=None, help="与 --dt 一起改，保持控制频率 30 Hz（1/dt ÷ decimation）")
parser.add_argument("--pos_iters", type=int, default=None, help="机器人与方块的位置迭代次数（默认 16）")
parser.add_argument("--vel_iters", type=int, default=None, help="机器人与方块的速度迭代次数（默认 1）")
parser.add_argument("--contact_offset", type=float, default=None, help="机器人与方块全部碰撞形状的接触偏移（m），运行时设置")
parser.add_argument("--rest_offset", type=float, default=None, help="机器人与方块全部碰撞形状的静止偏移（m），运行时设置")
parser.add_argument("--num_envs", type=int, default=1, help="buffers 模式的环境数")
parser.add_argument("--steps", type=int, default=150, help="buffers 模式的控制步数")
parser.add_argument("--gpu_max_rigid_patch_count", type=int, default=None)
parser.add_argument("--gpu_max_rigid_contact_count", type=int, default=None)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch

import isaaclab.utils.math as math_utils

import galbot_academy.tasks  # noqa: F401
from galbot_academy.scenes.lift import CUBE_REST_Z
from isaaclab_tasks.utils import parse_env_cfg
from pick_place_teacher import PickPlaceTeacher  # 同目录，6.4.6 的示教控制器


def make_env():
    cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs if args.mode == "buffers" else 1)
    cfg.seed = args.seed
    if args.dt:
        cfg.sim.dt = float(Fraction(args.dt))
    if args.decimation:
        cfg.decimation = args.decimation
        cfg.sim.render_interval = args.decimation  # __post_init__ 里由 decimation 派生，命令行改了要同步（4.3）
    robot, cube = cfg.scene.robot.spawn, cfg.scene.object.spawn
    for it, field in ((args.pos_iters, "solver_position_iteration_count"), (args.vel_iters, "solver_velocity_iteration_count")):
        if it is not None:
            setattr(robot.articulation_props, field, it)
            setattr(cube.rigid_props, field, it)
    for value, field in ((args.gpu_max_rigid_patch_count, "gpu_max_rigid_patch_count"),
                         (args.gpu_max_rigid_contact_count, "gpu_max_rigid_contact_count")):
        if value is not None:
            setattr(cfg.sim.physx, field, value)
    success_term = cfg.terminations.success
    cfg.terminations.success = None
    cfg.terminations.time_out = None
    cfg.observations.policy.concatenate_terms = False
    env = gym.make(args.task, cfg=cfg).unwrapped
    print(f"[sweep] dt {env.physics_dt:.6f} s，decimation {env.cfg.decimation}，控制 {1 / env.step_dt:.1f} Hz；"
          f"迭代 位置 {robot.articulation_props.solver_position_iteration_count} / 速度 {robot.articulation_props.solver_velocity_iteration_count}；"
          f"偏移 接触 {args.contact_offset} / 静止 {args.rest_offset}（None = 不改）；环境 {env.num_envs}", flush=True)
    return env, success_term


def apply_offsets(env, when: str) -> None:
    """偏移在运行时经 PhysX 视图改：spawn 阶段的 collision_props 对机器人不生效（碰撞体在实例里，6.1.4 坑一），
    写法同事件项 randomize_rigid_body_collider_offsets。先改接触偏移、再改静止偏移（要求静止 < 接触）。
    放在 env.sim.reset() 之后调用，结束时再读一次核对没有被冲掉；when 只用于打印。"""
    for name in ("robot", "object"):
        view = env.scene[name].root_physx_view
        ids = torch.arange(env.num_envs)
        if when == "开始" and args.contact_offset is not None:
            view.set_contact_offsets(torch.full_like(view.get_contact_offsets(), args.contact_offset), ids)
        if when == "开始" and args.rest_offset is not None:
            view.set_rest_offsets(torch.full_like(view.get_rest_offsets(), args.rest_offset), ids)
        co, ro = view.get_contact_offsets(), view.get_rest_offsets()
        print(f"[sweep] {when}时 {name} 的生效偏移：接触 {co.min().item() * 1000:.2f}–{co.max().item() * 1000:.2f} mm，"
              f"静止 {ro.min().item() * 1000:.2f}–{ro.max().item() * 1000:.2f} mm（{co.numel()} 个形状）", flush=True)


def probe(env, success_term) -> None:
    gripper_close_q = env.cfg.actions.gripper_action.close_command_expr[next(iter(env.cfg.actions.gripper_action.close_command_expr))]
    teacher = PickPlaceTeacher(env.device, 60.0, gripper_close_q)
    cube = env.scene["object"]
    results = []
    with torch.inference_mode():
        for attempt in range(args.attempts):
            if attempt == 0:
                env.sim.reset()
                apply_offsets(env, "开始")
            obs, _ = env.reset()
            teacher.reset()
            ok_steps, slip, rel0, flags, dt_sum, steps, close_steps = 0, 0.0, None, set(), 0.0, 0, 0
            while True:
                close_steps += teacher.phase == "close"
                action = teacher.act(obs)
                t0 = time.perf_counter()
                obs, *_ = env.step(action)
                torch.cuda.synchronize()
                dt_sum += time.perf_counter() - t0
                steps += 1
                o = obs["policy"]
                if not all(torch.isfinite(v).all() for v in o.values()):
                    flags.add("NaN")
                    ok = False
                    break
                if teacher.phase in ("lift", "carry", "lower"):
                    R = math_utils.matrix_from_quat(o["eef_quat"])[0]
                    rel = R.T @ (o["object_position"][0] - o["eef_pos"][0])  # 方块中心在 TCP 坐标系里
                    rel0 = rel if rel0 is None else rel0
                    slip = max(slip, torch.linalg.norm(rel - rel0).item())
                if torch.linalg.norm(cube.data.root_lin_vel_w[0]).item() > 2.0:
                    flags.add("弹飞")
                z = o["object_position"][0, 2].item()
                dropped = bool(env.termination_manager.get_term("object_dropping")[0])
                if not dropped and z < CUBE_REST_Z - 0.01:
                    flags.add("穿透")
                ok_steps = ok_steps + 1 if bool(success_term.func(env, **success_term.params)[0]) else 0
                if ok_steps >= 10:
                    ok = True
                    break
                if dropped or teacher.timed_out() or steps >= 900:
                    ok = False
                    flags.add("掉落" if dropped else f"{teacher.phase} 超时")
                    break
            results.append((ok, slip, flags, dt_sum / steps * 1000, steps))
            print(f"[sweep] 第 {attempt + 1} 次：{'成功' if ok else '失败'}，{steps} 步，滑移 {slip * 100:.2f} cm，"
                  f"每控制步 {dt_sum / steps * 1000:.2f} ms，合拢段 {close_steps} 步，{','.join(sorted(flags)) or '—'}"
                  + ("" if ok else f"；结束时夹爪 {teacher._last_grip:.3f} rad"), flush=True)
    apply_offsets(env, "结束")
    n_ok = sum(r[0] for r in results)
    slips = sorted(r[1] for r in results if r[0])
    per_step = sorted(r[3] for r in results)
    flags = {}
    for r in results:
        for f in r[2]:
            flags[f] = flags.get(f, 0) + 1
    med = lambda xs: xs[len(xs) // 2] if len(xs) % 2 else (xs[len(xs) // 2 - 1] + xs[len(xs) // 2]) / 2  # noqa: E731
    print(f"[sweep] 汇总：成功 {n_ok} / {len(results)}；成功回合的滑移 中位 {med(slips) * 100:.2f} cm、最大 {slips[-1] * 100:.2f} cm"
          if slips else f"[sweep] 汇总：成功 {n_ok} / {len(results)}", flush=True)
    print(f"[sweep] 汇总：每控制步墙上时间 中位 {med(per_step):.2f} ms；标记 {flags or '无'}", flush=True)


def buffers(env) -> None:
    zero = torch.zeros(env.num_envs, env.action_manager.total_action_dim, device=env.device)
    zero[:, -1] = 1.0  # 夹爪张开
    t0 = time.perf_counter()
    with torch.inference_mode():
        env.reset()
        apply_offsets(env, "开始")
        for _ in range(args.steps):
            env.step(zero)
    torch.cuda.synchronize()
    print(f"[sweep] buffers：{env.num_envs} 个环境 × {args.steps} 步，墙上 {time.perf_counter() - t0:.1f} s；"
          f"gpu_max_rigid_patch_count {env.cfg.sim.physx.gpu_max_rigid_patch_count}，"
          f"gpu_max_rigid_contact_count {env.cfg.sim.physx.gpu_max_rigid_contact_count}", flush=True)
    obj = env.scene["object"].data.root_pos_w
    print(f"[sweep] buffers：方块中心高度 最低 {obj[:, 2].min().item():.4f} m（静止应为 {CUBE_REST_Z:.4f} + 环境原点 z）；"
          f"NaN {int((~torch.isfinite(obj)).any(dim=1).sum())} 个环境", flush=True)


def main() -> None:
    env, success_term = make_env()
    probe(env, success_term) if args.mode == "probe" else buffers(env)
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
