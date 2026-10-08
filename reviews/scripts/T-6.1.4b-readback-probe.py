# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""复现并检查 6.1.4 中"右臂卡在 1.45 rad"的情形（6.1.4，T-6.1.4b 探针）。

与 check_contacts.py 第 [3] 段相同的设置与姿态序列（自碰撞关、USD 中的增益与限位、种子 0）：
右臂依次走过第 0–12 组随机目标，各 4 s；第 13 组保持 8 s，每 0.5 s 打印 joint1 与 joint3 的
位置、PhysX 报告的速度 v，以及由位置差分得到的速度 fd。卡住时 v 不为 0 而 fd 为 0。

在 t = 5 s（已卡住）时可以只改一个量，看能否解开：

    python scripts/probe_stuck_joint.py --headless                       # 基线：卡住
    python scripts/probe_stuck_joint.py --headless --no_sleep            # 关掉休眠与稳定化（从头生效）
    python scripts/probe_stuck_joint.py --headless --kick 0.05           # t=5 s 给 joint3 加 0.05 rad/s 的速度扰动
    python scripts/probe_stuck_joint.py --headless --vel_limit_at5 100   # t=5 s 把关节速度上限改为 100 rad/s
    python scripts/probe_stuck_joint.py --headless --effort_scale_at5 10 # t=5 s 把力矩上限放大 10 倍
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="复现右臂卡住")
parser.add_argument("--usd", default="generated/galbot_fixed_base/galbot.usd")
parser.add_argument("--no_sleep", action="store_true", help="sleep_threshold 与 stabilization_threshold 设为 0")
parser.add_argument("--kick", type=float, default=0.0, help="t=5 s 时给 joint3 加的速度（rad/s）")
parser.add_argument("--vel_limit_at5", type=float, default=None, help="t=5 s 时把所有关节速度上限改为该值（rad/s）")
parser.add_argument("--effort_scale_at5", type=float, default=None, help="t=5 s 时把力矩上限乘以该倍数")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import os

import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation, ArticulationCfg

STUCK_POSE = 13  # 种子 0 的序列中卡住的那一组（从 0 计）


def main() -> None:
    dt = 1 / 120
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=dt, device=args.device))
    no_sleep = {"sleep_threshold": 0.0, "stabilization_threshold": 0.0} if args.no_sleep else {}
    robot = Articulation(
        ArticulationCfg(
            prim_path="/World/Galbot",
            spawn=sim_utils.UsdFileCfg(
                usd_path=os.path.abspath(args.usd),
                articulation_props=sim_utils.ArticulationRootPropertiesCfg(enabled_self_collisions=False, **no_sleep),
            ),
            actuators={"all": ImplicitActuatorCfg(joint_names_expr=[".*"], stiffness=None, damping=None)},
        )
    )
    sim.reset()
    from pxr import Usd
    st = sim_utils.get_current_stage()
    for p in Usd.PrimRange(st.GetPrimAtPath("/World/Galbot")):
        for an in ("physxArticulation:sleepThreshold", "physxArticulation:stabilizationThreshold"):
            at = p.GetAttribute(an)
            if at and at.HasAuthoredValue():
                print("READBACK", p.GetPath(), an, at.Get())
    names = robot.joint_names
    arm = [i for i, n in enumerate(names) if n.startswith("right_arm_joint")]
    j1, j3 = names.index("right_arm_joint1"), names.index("right_arm_joint3")

    def step() -> None:
        robot.write_data_to_sim()
        sim.step(render=False)
        robot.update(dt)

    # 与 check_contacts.py 相同：先在零位 1 步 + 2 s，再按种子 0 采样右臂目标
    target = torch.zeros_like(robot.data.joint_pos)
    robot.set_joint_position_target(target)
    for _ in range(1 + round(2.0 / dt)):
        step()
    lo, hi = robot.data.soft_joint_pos_limits[0, arm, 0], robot.data.soft_joint_pos_limits[0, arm, 1]
    gen = torch.Generator(device=lo.device).manual_seed(0)
    for pose in range(STUCK_POSE + 1):
        target[0, arm] = lo + (hi - lo) * torch.rand(len(arm), generator=gen, device=lo.device)
        robot.set_joint_position_target(target)
        if pose < STUCK_POSE:
            for _ in range(round(4.0 / dt)):
                step()

    print(f"第 {STUCK_POSE} 组：joint3 目标 {target[0, j3].item():+.4f}，joint1 目标 {target[0, j1].item():+.4f}")
    for k in range(round(8.0 / dt)):
        if k == round(5.0 / dt):
            if args.kick:
                v = robot.data.joint_vel.clone()
                v[0, j3] += args.kick
                robot.write_joint_state_to_sim(robot.data.joint_pos, v)
            if args.vel_limit_at5 is not None:
                robot.write_joint_velocity_limit_to_sim(torch.full_like(robot.data.joint_vel_limits, args.vel_limit_at5))
            if args.effort_scale_at5 is not None:
                robot.write_joint_effort_limit_to_sim(robot.data.joint_effort_limits * args.effort_scale_at5)
        q_prev = robot.data.joint_pos[0].clone()
        step()
        if k % 60 == 0:
            fd = (robot.data.joint_pos[0] - q_prev) / dt
            print(f"t={k * dt:4.1f} s  joint1 v={robot.data.joint_vel[0, j1].item():+.3f} fd={fd[j1].item():+.3f}  "
                  f"joint3 q={robot.data.joint_pos[0, j3].item():+.4f} v={robot.data.joint_vel[0, j3].item():+.3f} "
                  f"fd={fd[j3].item():+.3f} 力矩={robot.data.applied_torque[0, j3].item():+.1f}")
    err = (robot.data.joint_pos[0, arm] - target[0, arm]).abs()
    tau_g = robot.root_physx_view.get_gravity_compensation_forces()[0, j3].item()
    print(f"8 s 后右臂最大误差 {err.max().item():.4f} rad（{names[arm[int(err.argmax())]]}）；"
          f"joint3 需要的重力补偿力矩 {tau_g:+.2f} N·m，力矩上限 {robot.data.joint_effort_limits[0, j3].item():.1f} N·m")

    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
