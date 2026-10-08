# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""重力力矩与重力下的保持（6.1.5）。

一次放 N 台固定底座的 Galbot（彼此相距 3 m，不放地面），每台一组随机姿态：
1. 统计：用 PhysX 的 get_gravity_compensation_forces() 读出每个关节在该姿态下需要的重力补偿力矩，
   与力矩上限（URDF 的 effort，转换后写进 USD 的 maxForce）比较；
2. 保持：以该姿态为目标保持若干秒，报告各组关节的稳态误差，以及误差大的姿态里是不是重力力矩超过了上限。

驱动参数默认用 galbot_academy.assets.drives 的参数表；--usd_gains 改用 USD 里的值（转换时的占位增益）。

用法（项目根目录）::

    python scripts/gravity_torques.py --headless
    python scripts/gravity_torques.py --headless --usd_gains
    python scripts/gravity_torques.py --headless --effort_scale 10   # 对照：力矩上限放大 10 倍
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="重力力矩统计与保持测试")
parser.add_argument("--usd", default="generated/galbot_fixed_base/galbot.usd")
parser.add_argument("--num", type=int, default=64, help="机器人台数 = 随机姿态数（第 0 台为零位）")
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--solver_iters", type=int, nargs=2, default=None, metavar=("POS", "VEL"),
                    help="覆盖求解器的位置 / 速度迭代次数（6.1.6b）；默认沿用资产或配置中的值")
parser.add_argument("--seconds", type=float, default=4.0, help="保持时长")
parser.add_argument("--usd_gains", action="store_true", help="用 USD 里的增益（转换时的占位值），而不是参数表")
parser.add_argument("--effort_scale", type=float, default=1.0, help="把力矩上限乘以这个倍数（对照实验）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import os
import re

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation, ArticulationCfg

from galbot_academy.assets.drives import GROUPS, make_actuators

SPACING = 3.0


def main() -> None:
    dt = 1 / 120
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=dt, device=args.device))
    cols = int(args.num**0.5 + 0.999)
    for i in range(args.num):
        sim_utils.create_prim(f"/World/envs/env_{i}", "Xform", translation=(SPACING * (i % cols), SPACING * (i // cols), 0.0))
    robot = Articulation(
        ArticulationCfg(
            prim_path="/World/envs/env_.*/Robot",
            spawn=sim_utils.UsdFileCfg(usd_path=os.path.abspath(args.usd), articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                **({} if args.solver_iters is None else {"solver_position_iteration_count": args.solver_iters[0], "solver_velocity_iteration_count": args.solver_iters[1]}))),
            actuators=make_actuators(use_usd_gains=args.usd_gains),
        )
    )
    sim.reset()
    names = robot.joint_names
    effort = robot.data.joint_effort_limits.clone()  # 来自 USD（= URDF effort）
    if args.effort_scale != 1.0:
        effort *= args.effort_scale
        robot.write_joint_effort_limit_to_sim(effort)

    # 每台一组随机姿态：所有关节在软限位内均匀采样；第 0 台保持零位
    lo, hi = robot.data.soft_joint_pos_limits[..., 0], robot.data.soft_joint_pos_limits[..., 1]
    gen = torch.Generator(device=lo.device).manual_seed(args.seed)
    pose = lo + (hi - lo) * torch.rand(lo.shape, generator=gen, device=lo.device)
    pose[0] = 0.0
    pose = pose.clamp(lo, hi)
    robot.write_joint_state_to_sim(pose, torch.zeros_like(pose))
    robot.set_joint_position_target(pose)
    robot.write_data_to_sim()
    sim.step(render=False)
    robot.update(dt)
    # 重力补偿力矩：维持当前姿态需要的关节力矩（固定底座时形状为 (台数, 关节数)）
    tau_g = robot.root_physx_view.get_gravity_compensation_forces().abs()

    print(f"{args.num} 台，每台一组随机姿态（种子 {args.seed}，第 0 台为零位）；驱动参数：{'USD' if args.usd_gains else '参数表'}，"
          f"力矩上限 ×{args.effort_scale:g}")
    print(f"\n{'关节':22s} {'力矩上限':>8s} {'零位 |τg|':>9s} {'最大 |τg|':>9s} {'|τg|>上限 的姿态':>14s}")
    groups = {g: [i for i, n in enumerate(names) if any(re.fullmatch(e, n) for e in spec["joint_names_expr"])]
              for g, spec in GROUPS.items()}
    driven = sorted(i for ids in groups.values() for i in ids)
    for i in driven:
        if names[i].startswith("left_"):
            continue  # 与右侧对称，只列右侧
        over = int((tau_g[:, i] > effort[:, i]).sum())
        print(f"{names[i]:22s} {effort[0, i].item():8.1f} {tau_g[0, i].item():9.2f} {tau_g[:, i].max().item():9.2f} {over:14d}")

    # 保持
    for _ in range(round(args.seconds / dt)):
        robot.write_data_to_sim()
        sim.step(render=False)
        robot.update(dt)
    err = (robot.data.joint_pos - pose).abs()
    finite = bool(torch.isfinite(robot.data.joint_pos).all())
    print(f"\n保持 {args.seconds:g} s 后的稳态误差（rad），数值有限 {finite}：")
    print(f"{'组':10s} {'零位最大':>8s} {'中位数':>8s} {'95% 分位':>9s} {'最大':>8s}  最大误差的关节 / 该姿态下 |τg| 与上限")
    for g, ids in groups.items():
        e = err[:, ids]
        k = int(e.max(dim=0).values.argmax())
        env = int(e[:, k].argmax())
        j = ids[k]
        print(f"{g:10s} {e[0].max().item():8.4f} {e.flatten().median().item():8.4f} {e.flatten().quantile(0.95).item():9.4f} "
              f"{e.max().item():8.4f}  {names[j]}（第 {env} 台）：{tau_g[env, j].item():.1f} / {effort[env, j].item():.1f} N·m")

    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
