# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""验证 GALBOT_ONE_GOLF_CFG（6.1.6）。

正常模式：放 N 台机器人（相距 3 m，有地面），写入默认关节状态，保持若干秒，打印
`data` 关键字段的形状、各关节误差、末段关节速度、重力力矩占上限的比例；再给 reach 手臂一组关节目标并跟踪。
演示模式（各自只做一件事，用来看报错长什么样）：

    python scripts/verify_galbot_cfg.py --headless
    python scripts/verify_galbot_cfg.py --headless --variant wheeled
    python scripts/verify_galbot_cfg.py --headless --demo overlap_across   # 两组的正则都匹配到同一关节
    python scripts/verify_galbot_cfg.py --headless --demo overlap_within   # 同一组的两个正则匹配到同一关节
    python scripts/verify_galbot_cfg.py --headless --demo bad_default      # 默认关节位置越限
    python scripts/verify_galbot_cfg.py --headless --demo missing_usd      # USD 路径不存在
    python scripts/verify_galbot_cfg.py --headless --demo unfix_root       # 用 fix_root_link=False 关掉固定根版的根关节
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="验证 Galbot 的 ArticulationCfg")
parser.add_argument("--num", type=int, default=4, help="机器人台数")
parser.add_argument("--variant", choices=["fixed", "wheeled"], default="fixed")
parser.add_argument("--seconds", type=float, default=3.0, help="每段保持时长")
parser.add_argument("--demo", choices=["overlap_across", "overlap_within", "bad_default", "missing_usd", "unfix_root"], default=None)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation

from galbot_academy.assets.galbot import GALBOT_ONE_GOLF_CFG, GALBOT_ONE_GOLF_WHEELED_CFG, REACH_ARM

SPACING = 3.0


def make_cfg():
    cfg = GALBOT_ONE_GOLF_WHEELED_CFG if args.variant == "wheeled" else GALBOT_ONE_GOLF_CFG
    cfg = cfg.replace(prim_path="/World/envs/env_.*/Robot")
    if args.demo == "overlap_across":
        cfg.actuators = {**cfg.actuators, "extra": ImplicitActuatorCfg(joint_names_expr=["right_arm_joint1"], stiffness=1.0, damping=1.0)}
    elif args.demo == "overlap_within":
        cfg.actuators = {**cfg.actuators, "arms": ImplicitActuatorCfg(
            joint_names_expr=["(left|right)_arm_joint[1-7]", "right_arm_joint1"], stiffness=400.0, damping=40.0)}
    elif args.demo == "bad_default":
        cfg.init_state = cfg.init_state.replace(joint_pos={**cfg.init_state.joint_pos, "leg_joint1": 1.2})  # 上限 0.937
    elif args.demo == "unfix_root":
        from galbot_academy.assets.paths import generated_asset_dir

        cfg.spawn = cfg.spawn.replace(
            usd_path=str(generated_asset_dir() / "galbot_wheeled" / "galbot.usd"),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(enabled_self_collisions=True, fix_root_link=False))
    elif args.demo == "missing_usd":
        cfg.spawn = cfg.spawn.replace(usd_path="/nonexistent/galbot.usd")
    return cfg


def main() -> None:
    dt = 1 / 120
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=dt, device=args.device))
    sim_utils.GroundPlaneCfg().func("/World/ground", sim_utils.GroundPlaneCfg())
    for i in range(args.num):
        sim_utils.create_prim(f"/World/envs/env_{i}", "Xform", translation=(SPACING * i, 0.0, 0.0))
    try:
        robot = Articulation(make_cfg())
        sim.reset()
    except Exception as e:  # 演示模式下把报错打印出来
        print(f"异常 {type(e).__name__}: {str(e)[:300]}")
        return
    if args.demo:
        a = robot.actuators.get("extra") or robot.actuators["arms"]
        j = robot.joint_names.index("right_arm_joint1")
        print(f"没有报错。right_arm_joint1 在 PhysX 中的 stiffness = {robot.root_physx_view.get_dof_stiffnesses()[0, j].item():.1f}"
              f"（{a.cfg.class_type.__name__} 组 {list(robot.actuators)}）")
        return

    d = robot.data
    names = robot.joint_names
    print(f"{args.variant}：{robot.num_instances} 台，关节 {robot.num_joints}，刚体 {robot.num_bodies}，根固定 {robot.is_fixed_base}")
    print(f"执行器组：{ {k: len(v.joint_names) for k, v in robot.actuators.items()} }")
    for field in ["joint_pos", "joint_vel", "default_joint_pos", "soft_joint_pos_limits", "joint_effort_limits",
                  "root_pos_w", "root_quat_w", "body_pos_w", "body_quat_w"]:
        print(f"  data.{field:22s} {tuple(getattr(d, field).shape)}")

    robot.write_joint_state_to_sim(d.default_joint_pos, d.default_joint_vel)
    target = d.default_joint_pos.clone()
    robot.set_joint_position_target(target)
    z0 = d.root_pos_w[:, 2].clone()

    def hold(seconds: float) -> torch.Tensor:
        """保持 seconds 秒，返回末 0.5 s 每台各关节的最大 |速度|。"""
        vmax = torch.zeros_like(d.joint_vel)
        n = round(seconds / dt)
        for k in range(n):
            robot.write_data_to_sim()
            sim.step(render=False)
            robot.update(dt)
            if k >= n - round(0.5 / dt):
                vmax = torch.maximum(vmax, d.joint_vel.abs())
        return vmax

    vmax = hold(args.seconds)
    err = (d.joint_pos - target).abs()
    finite = bool(torch.isfinite(d.joint_pos).all())
    print(f"\n保持默认姿态 {args.seconds:g} s：数值有限 {finite}，根高度变化 {(d.root_pos_w[:, 2] - z0).abs().max().item():.4f} m")
    worst = err.max(dim=0).values.topk(5)
    print("  误差最大的 5 个关节：" + "，".join(f"{names[i]} {v:.4f}" for v, i in zip(worst.values.tolist(), worst.indices.tolist())))
    vw = vmax.max(dim=0).values.topk(3)
    print("  末 0.5 s |关节速度| 最大的 3 个：" + "，".join(f"{names[i]} {v:.3f}" for v, i in zip(vw.values.tolist(), vw.indices.tolist())))
    if robot.is_fixed_base:  # 浮动根时该数组还多出根的 6 个分量，这里只看固定底座
        tau_g = robot.root_physx_view.get_gravity_compensation_forces().abs()
        ratio = torch.where(d.joint_effort_limits > 0, tau_g / d.joint_effort_limits, torch.zeros_like(tau_g))
        rw = ratio.max(dim=0).values.topk(3)
        print("  重力力矩 / 力矩上限 最大的 3 个：" + "，".join(f"{names[i]} {v:.2f}" for v, i in zip(rw.values.tolist(), rw.indices.tolist())))
    bn = robot.body_names
    tcp = d.body_pos_w[0, bn.index(f"{REACH_ARM}_arm_link7")] - d.root_pos_w[0]
    print(f"  {REACH_ARM}_arm_link7 相对根的位置 {[round(x, 3) for x in tcp.tolist()]} m")

    # reach 手臂的关节目标：每台在默认姿态上加一组 ±0.3 rad 的偏移（第 i 台的符号模式不同），并夹到软限位内
    arm = [i for i, n in enumerate(names) if n.startswith(f"{REACH_ARM}_arm_joint")]
    signs = torch.tensor([[1 if (k >> (i % 3)) & 1 else -1 for i in range(len(arm))] for k in range(robot.num_instances)],
                         dtype=torch.float32, device=robot.device)
    lim = d.soft_joint_pos_limits[:, arm]
    target[:, arm] = (target[:, arm] + 0.3 * signs).clamp(lim[..., 0], lim[..., 1])
    robot.set_joint_position_target(target)
    hold(args.seconds)
    aerr = (d.joint_pos[:, arm] - target[:, arm]).abs()
    print(f"\n{REACH_ARM} 臂关节目标（默认 ± 0.3 rad）{args.seconds:g} s 后：最大误差 {aerr.max().item():.4f} rad，"
          f"平均 {aerr.mean().item():.4f} rad，数值有限 {bool(torch.isfinite(d.joint_pos).all())}")


if __name__ == "__main__":
    main()
    sim_utils.SimulationContext.instance().clear_all_callbacks() if sim_utils.SimulationContext.instance() else None
    sim_utils.SimulationContext.clear_instance()  # 退出三步：释放 SimulationContext → flush → close
    sys.stdout.flush()
    simulation_app.close()
