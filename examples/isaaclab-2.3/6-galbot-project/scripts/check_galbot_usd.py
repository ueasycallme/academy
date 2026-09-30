# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""在仿真里检查 convert_galbot.py 的产物（6.1.2）：

1. 所有驱动关节以 0 为目标保持 2 秒，看重力下偏离多少（能否"站住"）；
2. 把右夹爪主动关节 right_gripper_joint 的目标设为 0.8 rad，看 5 个 mimic 跟随关节是否按 ±1 联动。

驱动增益直接用 USD 中的值（ImplicitActuatorCfg 的 stiffness / damping 设为 None）。

用法（项目根目录）::

    python scripts/check_galbot_usd.py --headless
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="检查转换得到的 Galbot USD")
parser.add_argument("--variant", choices=["fixed_base", "wheeled"], default="fixed_base")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation, ArticulationCfg

from galbot_academy.assets import generated_asset_dir

MIMIC = {  # 跟随关节 → 相对 right_gripper_joint 的倍数（取自 URDF 的 <mimic multiplier>）
    "right_gripper_r_inner_knuckle_joint": -1.0,
    "right_gripper_r_finger_joint": 1.0,
    "right_gripper_l_knuckle_joint": 1.0,
    "right_gripper_l_inner_knuckle_joint": 1.0,
    "right_gripper_l_finger_joint": -1.0,
}


def main() -> None:
    usd_path = generated_asset_dir() / f"galbot_{args.variant}" / "galbot.usd"
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=1 / 120, device=args.device))
    sim_utils.GroundPlaneCfg().func("/World/ground", sim_utils.GroundPlaneCfg())
    robot = Articulation(
        ArticulationCfg(
            prim_path="/World/Galbot",
            spawn=sim_utils.UsdFileCfg(usd_path=str(usd_path)),
            actuators={"all": ImplicitActuatorCfg(joint_names_expr=[".*"], stiffness=None, damping=None)},
        )
    )
    sim.reset()
    names = robot.joint_names
    print(f"{usd_path.name}（{args.variant}）：关节 {robot.num_joints}，刚体 {robot.num_bodies}，根固定 {robot.is_fixed_base}")

    def run(seconds: float) -> None:
        for _ in range(round(seconds * 120)):
            robot.write_data_to_sim()
            sim.step(render=False)
            robot.update(1 / 120)

    # 1. 保持零位
    target = torch.zeros_like(robot.data.joint_pos)
    robot.set_joint_position_target(target)
    run(2.0)
    # 驱动关节 = 去掉两侧夹爪的 mimic 跟随关节（右侧的名字见 MIMIC，左侧同名把 right 换成 left）与被动滚子
    followers = set(MIMIC) | {n.replace("right_", "left_", 1) for n in MIMIC}
    driven = [i for i, n in enumerate(names) if n not in followers and "_passive_" not in n]
    dev = robot.data.joint_pos[0, driven].abs()
    worst = dev.argmax().item()
    print(f"保持零位 2 s：驱动关节最大偏离 {dev.max().item():.4f} rad（{names[driven[worst]]}），平均 {dev.mean().item():.4f} rad")

    # 2. 夹爪联动
    g = names.index("right_gripper_joint")
    target[0, g] = 0.8
    robot.set_joint_position_target(target)
    run(2.0)
    q = robot.data.joint_pos[0]
    print(f"right_gripper_joint 目标 0.8 → 实际 {q[g].item():+.4f}")
    for name, k in MIMIC.items():
        print(f"  {name:38s} {q[names.index(name)].item():+.4f}（期望 {k * q[g].item():+.4f}）")

    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
