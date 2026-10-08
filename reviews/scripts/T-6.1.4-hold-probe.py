# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""碰撞相关的验证实验（6.1.4）：自碰撞开 / 关时，零位、随机臂姿、夹爪闭合下的接触与稳定性。

四个阶段：
1. 第 1 步：哪些刚体已经有接触力（开自碰撞时即"初始穿透"）；
2. 保持零位 2 s：最大偏离、末 0.5 s 关节速度（抖动）；
3. 右臂随机姿态：在关节软限位内均匀采样 N 组，各保持 4 s（臂关节限速 1.5 rad/s，最远要走约 6 rad），统计出现接触的刚体对；
4. 右夹爪闭合到上限，保持 4.5 s（夹爪限速 0.5 rad/s）：手指接触、末段抖动。

另外读出 PhysX 中实际生效的接触偏移（contact offset）与静止偏移（rest offset）。不放地面：根固定，地面与本实验无关。

用法（项目根目录）::

    python scripts/check_contacts.py --headless
    python scripts/check_contacts.py --headless --self_collision               # 资产里已写入过滤对（convert_galbot.py）
    python scripts/check_contacts.py --headless --self_collision --no_filter   # 对照：去掉过滤对
    python scripts/check_contacts.py --headless --contact_offset 0.02 --poses 0   # 验证 spawn 阶段的 collision_props 是否生效
"""

import argparse
import os
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="碰撞验证实验")
parser.add_argument("--usd", default="generated/galbot_fixed_base/galbot.usd")
parser.add_argument("--self_collision", action="store_true", help="开启 Articulation 自碰撞")
parser.add_argument("--contact_offset", type=float, default=None, help="通过 spawn 的 collision_props 设置接触偏移")
parser.add_argument("--no_filter", action="store_true", help="去掉资产里写好的自碰撞过滤对（对照实验）")
parser.add_argument("--poses", type=int, default=20, help="右臂随机姿态数")
parser.add_argument("--seed", type=int, default=0)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import os
from collections import Counter

import torch
from pxr import UsdPhysics

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation, ArticulationCfg
from isaaclab.sensors import ContactSensor, ContactSensorCfg

FORCE_EPS = 0.01
HOLD = float(os.environ.get("HOLD", "4.0"))  # 校验方探针：每组姿态保持时间  # N；净接触力超过它才算"有接触"


def main() -> None:
    dt = 1 / 120
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=dt, device=args.device))
    spawn = sim_utils.UsdFileCfg(
        usd_path=os.path.abspath(args.usd),
        activate_contact_sensors=True,
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(enabled_self_collisions=args.self_collision),
        collision_props=None if args.contact_offset is None else sim_utils.CollisionPropertiesCfg(contact_offset=args.contact_offset),
    )
    robot = Articulation(
        ArticulationCfg(
            prim_path="/World/Galbot",
            spawn=spawn,
            actuators={"all": ImplicitActuatorCfg(joint_names_expr=[".*"], stiffness=None, damping=None)},
        )
    )
    # filter_prim_paths_expr 让传感器额外给出"刚体 × 刚体"的接触力矩阵，用来找出是哪一对在接触。
    # 要逐个列出刚体：写 "/World/Galbot/.*" 会同时匹配 joints、Looks、root_joint，数目对不上，矩阵全为 0（只报一条 Error）。
    stage = sim_utils.get_current_stage()
    body_paths = [p.GetPath().pathString for p in stage.GetPrimAtPath("/World/Galbot").GetChildren() if p.HasAPI(UsdPhysics.RigidBodyAPI)]
    contact = ContactSensor(ContactSensorCfg(prim_path="/World/Galbot/.*", filter_prim_paths_expr=body_paths))
    if args.no_filter:
        from galbot_academy.assets.physics import remove_filtered_pairs

        remove_filtered_pairs(stage, "/World/Galbot")
    sim.reset()
    names, bodies = robot.joint_names, contact.body_names
    filter_names = [p.rsplit("/", 1)[-1] for p in body_paths]  # 矩阵第二维按 filter 的顺序
    print(f"自碰撞 {args.self_collision}；接触传感器覆盖 {len(bodies)} 个刚体")

    view = robot.root_physx_view
    co, ro = view.get_contact_offsets().flatten(), view.get_rest_offsets().flatten()
    print(f"生效的接触偏移 {co.min().item():.4f}–{co.max().item():.4f} m，静止偏移 {ro.min().item():.4f}–{ro.max().item():.4f} m"
          f"（{view.max_shapes} 个形状）")

    def step(n: int, record=None) -> None:
        for _ in range(n):
            robot.write_data_to_sim()
            sim.step(render=False)
            robot.update(dt)
            contact.update(dt)
            if record is not None:
                record.append(robot.data.joint_vel[0].clone())

    def touching() -> list[str]:
        """有接触的刚体对（按名字排序去重）。"""
        f = contact.data.force_matrix_w[0].norm(dim=-1)  # (刚体, 过滤刚体)
        pairs = {tuple(sorted((bodies[i], filter_names[j]))) for i, j in torch.nonzero(f > FORCE_EPS).tolist()}
        return [f"{a}–{b}" for a, b in sorted(pairs)]

    target = torch.zeros_like(robot.data.joint_pos)
    robot.set_joint_position_target(target)
    step(1)
    print(f"[1] 第 1 步有接触的刚体对：{touching() or '无'}")

    vel = []
    step(round(2.0 / dt), vel)
    tail = torch.stack(vel[-round(0.5 / dt):])
    err = (robot.data.joint_pos[0] - target[0]).abs()
    print(f"[2] 零位 2 s：最大偏离 {err.max().item():.4f} rad（{names[err.argmax().item()]}），"
          f"末 0.5 s 最大 |关节速度| {tail.abs().max().item():.4f} rad/s，接触 {touching() or '无'}")

    arm = [i for i, n in enumerate(names) if n.startswith("right_arm_joint")]
    lo, hi = robot.data.soft_joint_pos_limits[0, arm, 0], robot.data.soft_joint_pos_limits[0, arm, 1]
    gen = torch.Generator(device=lo.device).manual_seed(args.seed)
    hits, with_contact, errs_free, errs_contact, max_vel = Counter(), 0, [], [], 0.0
    for _ in range(args.poses):
        prev = robot.data.joint_pos[0, arm].clone()
        target[0, arm] = lo + (hi - lo) * torch.rand(len(arm), generator=gen, device=lo.device)
        robot.set_joint_position_target(target)
        vel = []
        step(round(HOLD / dt), vel)
        ev = (robot.data.joint_pos[0, arm] - target[0, arm]).abs()
        e = ev.max().item(); k = ev.argmax().item()
        print(f"    POSE hold={HOLD} worst=right_arm_joint{k+1} err={e:.4f} dist={(target[0, arm][k]-prev[k]).abs().item():.3f} maxdist={(target[0, arm]-prev).abs().max().item():.3f}")
        t = touching()
        max_vel = max(max_vel, torch.stack(vel[-round(0.5 / dt):]).abs().max().item())
        if t:
            with_contact += 1
            hits.update(t)
            errs_contact.append(e)
        else:
            errs_free.append(e)
    finite = bool(torch.isfinite(robot.data.joint_pos).all())
    print(f"[3] 右臂随机姿态 {args.poses} 组：有接触 {with_contact} 组；数值有限 {finite}；"
          f"末 0.5 s 最大 |关节速度| {max_vel:.3f} rad/s")
    print(f"    臂关节最大跟踪误差：无接触的姿态 {max(errs_free, default=float('nan')):.4f} rad，"
          f"有接触的姿态 {max(errs_contact, default=float('nan')):.4f} rad")
    print(f"    出现接触的刚体对（姿态数）：{dict(hits.most_common()) or '无'}")

    target.zero_()
    g = names.index("right_gripper_joint")
    target[0, g] = robot.data.soft_joint_pos_limits[0, g, 1]
    robot.set_joint_position_target(target)
    vel = []
    step(round(4.5 / dt), vel)  # 回到零位并合上夹爪
    vel = vel[-round(0.5 / dt):]
    mimic = [i for i, n in enumerate(names) if n.startswith("right_gripper_") and n != "right_gripper_joint"]
    q = robot.data.joint_pos[0]
    print(f"[4] 右夹爪目标 {target[0, g].item():.3f}（上限）→ 实际 {q[g].item():.4f}；"
          f"夹爪各关节末 0.5 s 最大 |速度| {torch.stack(vel)[:, mimic + [g]].abs().max().item():.4f} rad/s；"
          f"接触 {touching() or '无'}")

    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
