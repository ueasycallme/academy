# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""单关节阶跃响应（6.1.5）。

一次放若干台固定底座的 Galbot（相距 3 m，不放地面），每台给被测关节一组不同的 stiffness / damping，
从零位（先保持 3 s）出发，给被测关节一个阶跃目标，其余关节按参数表（galbot_academy.assets.drives）保持零位。
输出每组的上升时间（10%→90%）、超调与 2% 调节时间（都相对最终值）、稳态误差（相对目标）、末 0.25 s 的峰峰值波动、最大力矩，可选保存曲线 CSV。

用法（项目根目录）::

    python scripts/step_response.py --headless
    python scripts/step_response.py --headless --actuator ideal          # 显式 IdealPD
    python scripts/step_response.py --headless --effort 1000             # 力矩上限改用厂商 USD 的 1000
    python scripts/step_response.py --headless --vel_limit 100           # 放开速度上限
    python scripts/step_response.py --headless --csv generated/step/implicit.csv
"""

import argparse
import sys

from isaaclab.app import AppLauncher

ARM_JOINTS = [f"{s}_arm_joint{i}" for s in ("left", "right") for i in range(1, 8)]

parser = argparse.ArgumentParser(description="单关节阶跃响应")
parser.add_argument("--usd", default="generated/galbot_fixed_base/galbot.usd")
parser.add_argument("--joint", default="right_arm_joint2", choices=ARM_JOINTS, help="被测关节（臂关节）")
parser.add_argument("--step", type=float, default=0.5, help="阶跃幅度（rad）")
parser.add_argument("--gains", default="100:10,400:10,400:40,400:120,1600:80,4000:200",
                    help="逗号分隔的 stiffness:damping，每组一台机器人")
parser.add_argument("--actuator", choices=["implicit", "ideal"], default="implicit")
parser.add_argument("--effort", type=float, default=None, help="被测关节的力矩上限（N·m）；默认沿用 USD（= URDF effort）")
parser.add_argument("--vel_limit", type=float, default=None, help="被测关节的速度上限（rad/s）；默认沿用 USD（= URDF velocity）")
parser.add_argument("--dt", type=float, default=1 / 120)
parser.add_argument("--solver_iters", type=int, nargs=2, default=None, metavar=("POS", "VEL"),
                    help="覆盖求解器的位置 / 速度迭代次数（6.1.6b）；默认沿用资产中的值")
parser.add_argument("--seconds", type=float, default=2.0)
parser.add_argument("--csv", default=None, help="保存曲线：每行 t, 各组位置")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import os
from pathlib import Path

import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import IdealPDActuatorCfg, ImplicitActuatorCfg
from isaaclab.assets import Articulation, ArticulationCfg

from galbot_academy.assets.drives import GROUPS, make_actuators

SPACING = 3.0


def build_actuators(gains: list[tuple[float, float]]) -> dict:
    """参数表的各组，但被测关节单独成组（各组正则互不重叠）。"""
    actuators = make_actuators()
    arms = GROUPS["arms"]
    rest = [n for n in ARM_JOINTS if n != args.joint]
    actuators["arms"] = ImplicitActuatorCfg(joint_names_expr=rest, stiffness=arms["stiffness"], damping=arms["damping"])
    common = dict(joint_names_expr=[args.joint], stiffness=gains[0][0], damping=gains[0][1],
                  effort_limit_sim=args.effort, velocity_limit_sim=args.vel_limit)
    if args.actuator == "implicit":
        actuators["test"] = ImplicitActuatorCfg(**common)
    else:
        # 显式执行器在模型内按 effort_limit 截断（未设时取 USD 值），effort_limit_sim 只管 PhysX 层（4.7）
        actuators["test"] = IdealPDActuatorCfg(**common, effort_limit=args.effort)
    return actuators


def metrics(t: torch.Tensor, q: torch.Tensor, q0: float, step: float) -> dict:
    """q: (时间,) 的位置曲线。超调与调节时间相对最终值（末 0.25 s 均值），稳态误差相对目标。"""
    tail = q[-max(1, round(0.25 / args.dt)):]
    final = tail.mean().item()
    y = (q - q0) / (final - q0)  # 归一化到 0 → 1（以最终值为 1）

    def first(cond):
        idx = torch.nonzero(cond).flatten()
        return t[idx[0]].item() if len(idx) else float("nan")

    t10, t90 = first(y >= 0.1), first(y >= 0.9)
    outside = torch.nonzero((y - 1.0).abs() > 0.02).flatten()  # 2% 带之外的时刻
    if len(outside) == 0:
        settle = 0.0
    elif outside[-1] + 1 < len(t):
        settle = t[outside[-1] + 1].item()
    else:
        settle = float("nan")  # 到结束仍未进入 2% 带
    return {"rise": t90 - t10, "overshoot": max(0.0, (y.max().item() - 1.0) * 100), "settle": settle,
            "ss_err": final - (q0 + step), "ripple": (tail.max() - tail.min()).item()}


def main() -> None:
    gains = [tuple(float(x) for x in g.split(":")) for g in args.gains.split(",")]
    n = len(gains)
    dt = args.dt
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=dt, device=args.device))
    for i in range(n):
        sim_utils.create_prim(f"/World/envs/env_{i}", "Xform", translation=(SPACING * i, 0.0, 0.0))
    robot = Articulation(ArticulationCfg(
        prim_path="/World/envs/env_.*/Robot",
        spawn=sim_utils.UsdFileCfg(usd_path=os.path.abspath(args.usd), articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            **({} if args.solver_iters is None else {"solver_position_iteration_count": args.solver_iters[0], "solver_velocity_iteration_count": args.solver_iters[1]}))),
        actuators=build_actuators(gains),
    ))
    sim.reset()
    j = robot.joint_names.index(args.joint)
    act = robot.actuators["test"]
    kp = torch.tensor([g[0] for g in gains], device=robot.device).unsqueeze(1)
    kd = torch.tensor([g[1] for g in gains], device=robot.device).unsqueeze(1)
    act.stiffness[:] = kp  # 执行器模型里的增益（显式执行器用它算力矩；隐式执行器用它估算 applied_torque）
    act.damping[:] = kd
    if args.actuator == "implicit":  # 隐式：真正起作用的是写进 PhysX 的驱动增益
        robot.write_joint_stiffness_to_sim(kp, joint_ids=[j])
        robot.write_joint_damping_to_sim(kd, joint_ids=[j])

    target = torch.zeros_like(robot.data.joint_pos)
    robot.set_joint_position_target(target)

    def step() -> None:
        robot.write_data_to_sim()
        sim.step(render=False)
        robot.update(dt)

    for _ in range(round(3.0 / dt)):  # 先在零位稳定 3 s（重力下有静差；阻尼大的组收敛慢）
        step()
    q0 = robot.data.joint_pos[:, j].clone()
    target[:, j] = q0 + args.step
    robot.set_joint_position_target(target)
    ts, qs, taus = [], [], []
    for k in range(round(args.seconds / dt)):
        step()
        ts.append((k + 1) * dt)
        qs.append(robot.data.joint_pos[:, j].clone())
        taus.append(robot.data.applied_torque[:, j].abs().clone())
    t = torch.tensor(ts, device=robot.device)
    q = torch.stack(qs, dim=1)  # (组, 时间)
    tau = torch.stack(taus, dim=1)
    finite = bool(torch.isfinite(q).all())

    eff = robot.data.joint_effort_limits[0, j].item()
    vel = robot.data.joint_vel_limits[0, j].item()
    print(f"{args.joint}：{args.actuator}，阶跃 {args.step} rad，dt {dt:.4f} s，力矩上限 {eff:g} N·m，速度上限 {vel:g} rad/s，数值有限 {finite}")
    print(f"{'stiffness':>9s} {'damping':>8s} {'上升 s':>7s} {'超调 %':>7s} {'调节 s':>7s} {'稳态误差 rad':>12s} {'末段波动 rad':>12s} {'最大力矩':>8s}")
    for i, (k_, d_) in enumerate(gains):
        m = metrics(t, q[i], q0[i].item(), args.step)
        print(f"{k_:9g} {d_:8g} {m['rise']:7.3f} {m['overshoot']:7.1f} {m['settle']:7.3f} {m['ss_err']:+12.4f} {m['ripple']:12.4f} {tau[i].max().item():8.1f}")

    if args.csv:
        path = Path(args.csv)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write("t," + ",".join(f"{k_:g}:{d_:g}" for k_, d_ in gains) + "\n")
            for k in range(len(ts)):
                f.write(f"{ts[k]:.5f}," + ",".join(f"{(q[i, k] - q0[i]).item():.6f}" for i in range(n)) + "\n")
        print(f"曲线已保存 {path}（位置相对阶跃起点）")

    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
