# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0（PhysX）/ Newton 1.5.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-12
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04
"""右臂单关节阶跃响应（8.10；方法与指标同 6.3.2 的 step_response.py）。

用 Galbot-Reach 的场景与执行器（任务配置里的 PD 增益），先保持默认姿态 --hold 秒，再把一个关节的位置目标加 --step rad，
逐个物理步记录关节位置 --seconds 秒。指标（与 6.3.2 相同）：上升时间（10% → 90%）、超调（相对末 0.25 s 均值）、
2% 调节时间、稳态误差（末 0.25 s 均值 − 目标）、末 0.25 s 的波动。同时打印每个物理步的曲线到 --csv。

    python scripts/step_response_30.py --joint right_arm_joint2 --step 0.05 --csv step_physx.csv physics=isaacsim_physx
    python scripts/step_response_30.py --joint right_arm_joint2 --step 0.05 --csv step_newton.csv physics=newton_mjwarp
"""

import argparse
import sys

from isaaclab.app import add_launcher_args, launch_simulation
from isaaclab.utils.string import list_intersection

from isaaclab_rl.entrypoints.common import add_frontend_args, create_isaaclab_env

from isaaclab_tasks.utils import setup_preset_cli
from isaaclab_tasks.utils.hydra import hydra_task_config

import galbot_academy

parser = argparse.ArgumentParser(description="单关节阶跃响应（3.0 EA，8.10）")
parser.add_argument("--task", default="Galbot-Reach")
parser.add_argument("--agent", default="rsl_rl_cfg_entry_point")
parser.add_argument("--joint", default="right_arm_joint2")
parser.add_argument("--step", type=float, default=0.05)
parser.add_argument("--hold", type=float, default=1.0)
parser.add_argument("--seconds", type=float, default=1.5)
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--csv", default=None)
add_launcher_args(parser)
add_frontend_args(parser)
args, remaining = setup_preset_cli(parser)
galbot_academy.register_tasks()
sys.argv = [sys.argv[0]] + list_intersection(remaining, None)


def metrics(t, q, q0: float, step: float, dt: float) -> dict:
    """与 6.3.2 的 metrics 相同：超调与调节时间相对最终值（末 0.25 s 均值），稳态误差相对目标。"""
    import torch

    tail = q[-max(1, round(0.25 / dt)) :]
    final = tail.mean().item()
    y = (q - q0) / (final - q0)

    def first(cond):
        idx = torch.nonzero(cond).flatten()
        return t[idx[0]].item() if len(idx) else float("nan")

    t10, t90 = first(y >= 0.1), first(y >= 0.9)
    outside = torch.nonzero((y - 1.0).abs() > 0.02).flatten()
    if len(outside) == 0:
        settle = 0.0
    elif outside[-1] + 1 < len(t):
        settle = t[outside[-1] + 1].item()
    else:
        settle = float("nan")
    return {"rise": t90 - t10, "overshoot": max(0.0, (y.max().item() - 1.0) * 100), "settle": settle,
            "ss_err": final - (q0 + step), "ripple": (tail.max() - tail.min()).item()}


@hydra_task_config(args.task, args.agent)
def main(env_cfg, agent_cfg) -> None:
    import torch

    with launch_simulation(env_cfg, args):
        env_cfg.scene.num_envs = args.num_envs
        env_cfg.commands.ee_pose.debug_vis = False
        env = create_isaaclab_env(args.task, env_cfg, args, convert_marl_to_single_agent=False).unwrapped
        env.reset()
        robot = env.scene["robot"]
        sim, dt = env.sim, env.physics_dt
        j = robot.find_joints(args.joint)[0][0]
        print(f"[8.10] physics {type(env_cfg.sim.physics).__name__}，物理步 {dt:.5f} s；关节 {args.joint}（公开序号 {j}）；"
              f"阶跃 {args.step} rad", flush=True)
        target = robot.data.default_joint_pos.torch.clone()

        def physics_step(tgt):
            robot.set_joint_position_target(tgt)
            env.scene.write_data_to_sim()
            sim.step(render=False)
            env.scene.update(dt)

        for _ in range(round(args.hold / dt)):
            physics_step(target)
        q0 = robot.data.joint_pos.torch[:, j].clone()
        target[:, j] += args.step
        ts, qs = [], []
        for k in range(round(args.seconds / dt)):
            physics_step(target)
            ts.append((k + 1) * dt)
            qs.append(robot.data.joint_pos.torch[:, j].clone())
        t = torch.tensor(ts)
        q = torch.stack(qs).cpu()  # (时间, 环境)
        m = metrics(t, q[:, 0], q0[0].item(), args.step, dt)
        spread = (q[-1] - q[-1, 0]).abs().max().item()
        print(f"[8.10] env_0：起点 {q0[0].item():+.4f} rad；上升 {m['rise']:.3f} s，超调 {m['overshoot']:.1f}%，"
              f"2% 调节 {m['settle']:.3f} s，稳态误差 {m['ss_err']:+.4f} rad，末 0.25 s 波动 {m['ripple']:.4f} rad；"
              f"各环境终值最大差 {spread:.2e} rad", flush=True)
        if args.csv:
            with open(args.csv, "w") as f:
                f.write("t,q\n")
                for ti, qi in zip(ts, q[:, 0].tolist()):
                    f.write(f"{ti:.5f},{qi - q0[0].item():.6f}\n")
            print(f"[8.10] 曲线（相对起点）已写到 {args.csv}", flush=True)
        env.close()


if __name__ == "__main__":
    main()
