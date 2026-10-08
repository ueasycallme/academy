# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""把任意一份 Galbot USD 载入 Isaac Lab，所有驱动关节以 0 为目标保持若干秒，再驱动右夹爪，报告稳定性（6.1.3）。

驱动增益、力矩上限一律用 USD 中的值（ImplicitActuatorCfg 的各项设为 None），以便比较两份资产本身。

用法（项目根目录）::

    python scripts/hold_pose.py --headless --usd generated/galbot_fixed_base/galbot.usd
    python scripts/hold_pose.py --headless --usd third_party/galbot_one_golf_description/usd/galbot_one_golf.usda --fix_root
    python scripts/hold_pose.py --headless --usd generated/galbot_wheeled/galbot.usd --z 0.05   # 轮式版：固定根要离地（6.1.2）

轮式版的根是固定的，放在 z=0 且有地面时，轮子一开始就压进地面，仿真会发散出 NaN（D-026）。
所以固定根的轮式版要用 --z 抬离地面，或用 --no_ground 不放地面。
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="载入 USD 并保持零位")
parser.add_argument("--usd", required=True, help="机器人 USD")
parser.add_argument("--fix_root", action="store_true", help="用 fix_root_link 把根连杆固定到世界")
parser.add_argument("--seconds", type=float, default=5.0, help="保持零位的时长")
parser.add_argument("--z", type=float, default=0.0, help="根的初始高度（m）；固定根的轮式版要离地，如 0.05")
parser.add_argument("--no_ground", action="store_true", help="不放地面")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import os

import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation, ArticulationCfg

# 右夹爪 5 个 mimic 跟随关节 → 相对 right_gripper_joint 的倍数（URDF 的 <mimic multiplier>）
MIMIC = {
    "right_gripper_r_inner_knuckle_joint": -1.0,
    "right_gripper_r_finger_joint": 1.0,
    "right_gripper_l_knuckle_joint": 1.0,
    "right_gripper_l_inner_knuckle_joint": 1.0,
    "right_gripper_l_finger_joint": -1.0,
}
FOLLOWERS = set(MIMIC) | {n.replace("right_", "left_", 1) for n in MIMIC}


def main() -> None:
    dt = 1 / 120
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=dt, device=args.device))
    if not args.no_ground:
        sim_utils.GroundPlaneCfg().func("/World/ground", sim_utils.GroundPlaneCfg())
    spawn = sim_utils.UsdFileCfg(
        usd_path=os.path.abspath(args.usd),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(fix_root_link=True) if args.fix_root else None,
    )
    robot = Articulation(
        ArticulationCfg(
            prim_path="/World/Galbot",
            spawn=spawn,
            init_state=ArticulationCfg.InitialStateCfg(pos=(0.0, 0.0, args.z)),
            actuators={"all": ImplicitActuatorCfg(joint_names_expr=[".*"], stiffness=None, damping=None)},
        )
    )
    sim.reset()
    names = robot.joint_names
    driven = [i for i, n in enumerate(names) if n not in FOLLOWERS and "_passive_" not in n and not n.startswith("wheel")]
    print(f"{os.path.basename(args.usd)}：关节 {robot.num_joints}，刚体 {robot.num_bodies}，根固定 {robot.is_fixed_base}，"
          f"根高度 {args.z} m，地面 {not args.no_ground}")
    j = names.index("left_arm_joint1")
    print(f"left_arm_joint1 生效的 stiffness {robot.data.joint_stiffness[0, j].item():.1f} N·m/rad，"
          f"damping {robot.data.joint_damping[0, j].item():.1f}，力矩上限 {robot.data.joint_effort_limits[0, j].item():.1f} N·m")

    def run(seconds: float) -> None:
        for _ in range(round(seconds / dt)):
            robot.write_data_to_sim()
            sim.step(render=False)
            robot.update(dt)

    z0 = robot.data.root_pos_w[0, 2].item()
    target = torch.zeros_like(robot.data.joint_pos)
    robot.set_joint_position_target(target)
    run(args.seconds)
    q = robot.data.joint_pos[0]
    dev = q[driven].abs()
    worst = driven[dev.argmax().item()]
    finite = bool(torch.isfinite(robot.data.joint_pos).all())
    print(f"保持零位 {args.seconds:.0f} s：驱动关节最大偏离 {dev.max().item():.4f} rad（{names[worst]}），"
          f"根高度变化 {robot.data.root_pos_w[0, 2].item() - z0:+.4f} m，数值有限 {finite}")

    g = names.index("right_gripper_joint")
    target[0, g] = 0.8
    robot.set_joint_position_target(target)
    run(2.0)
    q = robot.data.joint_pos[0]
    err = max(abs(q[names.index(n)].item() - k * q[g].item()) for n, k in MIMIC.items())
    print(f"right_gripper_joint 目标 0.8 → 实际 {q[g].item():+.4f}，mimic 最大跟随误差 {err:.4f} rad")

    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
