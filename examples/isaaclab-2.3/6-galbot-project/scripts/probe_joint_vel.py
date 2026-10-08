# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""静止保持时，读回的关节速度是否为 0（6.1.5，T-6.1.5b 探针）。

机器人保持默认姿态，在若干时刻比较三个量（各关节取绝对值后的最大值）：
- v：`robot.data.joint_vel`（Isaac Lab 的缓冲）；
- raw：`root_physx_view.get_dof_velocities()`（直接从 PhysX 读，排除缓冲更新时机）；
- fd：一步内位置的差分 / dt（关节实际有没有在动）。
另外报告 6 s 内位置的总漂移，并与"一步内重力造成的关节加速度 × dt"（|M⁻¹ τg|·dt）对比。

    python scripts/probe_joint_vel.py --headless                         # Galbot，隐式执行器
    python scripts/probe_joint_vel.py --headless --actuator ideal        # Galbot，显式 IdealPD（增益相同）
    python scripts/probe_joint_vel.py --headless --robot franka          # 官方 Franka（隐式）
    python scripts/probe_joint_vel.py --headless --dt 0.0166667 --device cpu
    python scripts/probe_joint_vel.py --headless --no_gravity            # 关掉重力
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="静止时关节速度读数")
parser.add_argument("--robot", choices=["galbot", "franka"], default="galbot")
parser.add_argument("--actuator", choices=["implicit", "ideal"], default="implicit")
parser.add_argument("--dt", type=float, default=1 / 120)
parser.add_argument("--seconds", type=float, default=6.0)
parser.add_argument("--no_gravity", action="store_true")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import IdealPDActuatorCfg, ImplicitActuatorCfg
from isaaclab.assets import Articulation


def to_ideal(actuators: dict) -> dict:
    """把各组隐式执行器换成增益相同的 IdealPD（增益为 None 的组保持隐式）。"""
    out = {}
    for name, a in actuators.items():
        if isinstance(a, ImplicitActuatorCfg) and a.stiffness is not None:
            out[name] = IdealPDActuatorCfg(joint_names_expr=a.joint_names_expr, stiffness=a.stiffness, damping=a.damping,
                                           effort_limit=a.effort_limit_sim, velocity_limit=a.velocity_limit_sim)
        else:
            out[name] = a
    return out


def main() -> None:
    dt = args.dt
    gravity = (0.0, 0.0, 0.0) if args.no_gravity else (0.0, 0.0, -9.81)
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=dt, device=args.device, gravity=gravity))
    if args.robot == "galbot":
        from galbot_academy.assets.galbot import GALBOT_ONE_GOLF_CFG as cfg
    else:
        from isaaclab_assets.robots.franka import FRANKA_PANDA_CFG as cfg
    cfg = cfg.replace(prim_path="/World/Robot")
    if args.actuator == "ideal":
        cfg.actuators = to_ideal(cfg.actuators)
    robot = Articulation(cfg)
    sim.reset()
    d = robot.data
    robot.write_joint_state_to_sim(d.default_joint_pos, d.default_joint_vel)
    robot.set_joint_position_target(d.default_joint_pos)
    names = robot.joint_names
    print(f"{args.robot}，{args.actuator}，dt {dt:.5f}，{args.device}，重力 {gravity[2]}，关节 {robot.num_joints}")

    marks = {round(t / dt) for t in (0.5, 1.0, 2.0, 4.0, args.seconds)}
    q_start = None
    for k in range(1, round(args.seconds / dt) + 1):
        q_prev = d.joint_pos.clone()
        robot.write_data_to_sim()
        sim.step(render=False)
        robot.update(dt)
        if k == round(1.0 / dt):
            q_start = d.joint_pos.clone()
        if k in marks:
            v = d.joint_vel[0].abs()
            raw = robot.root_physx_view.get_dof_velocities()[0].abs()
            fd = ((d.joint_pos - q_prev) / dt)[0].abs()
            top = v.topk(3)
            print(f"t={k * dt:4.1f} s  max|v| {v.max().item():.4f}  max|raw| {raw.max().item():.4f}  max|fd| {fd.max().item():.4f}  "
                  f"v 最大的关节：" + "，".join(f"{names[i]} {x:.4f}" for x, i in zip(top.values.tolist(), top.indices.tolist())))
    drift = (d.joint_pos - q_start)[0].abs()
    print(f"1 s 之后到 {args.seconds:g} s 的位置漂移：最大 {drift.max().item():.5f} rad（{names[int(drift.argmax())]}）")
    v = d.joint_vel[0].abs()
    nz = [n for n, x in zip(names, v.tolist()) if x > 0.01]
    print(f"末时刻 |v| > 0.01 rad/s 的关节 {len(nz)} / {robot.num_joints} 个：{nz}")
    # 推断的检验：若读数 ≈ 一步内重力造成的关节加速度 × dt，则 v ≈ |M⁻¹ τg| · dt（M 为关节空间质量矩阵，τg 为重力补偿力矩）
    M = robot.root_physx_view.get_generalized_mass_matrices()[0]
    tau_g = robot.root_physx_view.get_gravity_compensation_forces()[0]
    pred = (torch.linalg.solve(M, tau_g.unsqueeze(-1)).squeeze(-1) * dt).abs()
    show = [i for i in v.topk(min(5, robot.num_joints)).indices.tolist()]
    print("读数 v 与预测 |M⁻¹τg|·dt（读数最大的 5 个关节）：" + "，".join(f"{names[i]} {v[i].item():.4f} / {pred[i].item():.4f}" for i in show))
    if args.robot == "galbot":
        arm = [i for i, n in enumerate(names) if n.startswith("right_arm_joint")]
        print("末时刻 right_arm 各关节 |v|：" + "，".join(f"{names[i][-6:]} {v[i].item():.4f}" for i in arm))

    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
