# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""同一个 Cartpole 小车关节，分别用隐式执行器与 IdealPDActuator，给 1 m 的位置阶跃目标，比较响应。

用法::

    python actuator_step_demo.py --headless --model implicit
    python actuator_step_demo.py --headless --model ideal_pd
    python actuator_step_demo.py --headless --model ideal_pd --kp 20000 --kd 200 --dt 0.02   # 大增益 + 大步长
    python actuator_step_demo.py --headless --overlap        # 演示执行器配置中正则键重叠时的报错
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="执行器阶跃响应演示")
parser.add_argument("--model", choices=["implicit", "ideal_pd"], default="implicit", help="小车关节的执行器模型")
parser.add_argument("--kp", type=float, default=200.0, help="stiffness（N/m）")
parser.add_argument("--kd", type=float, default=20.0, help="damping（N·s/m）")
parser.add_argument("--dt", type=float, default=1.0 / 120.0, help="物理步长（秒）")
parser.add_argument("--overlap", action="store_true", help="stiffness 用两个会同时匹配小车关节的正则键")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import IdealPDActuatorCfg, ImplicitActuatorCfg
from isaaclab.assets import Articulation, ArticulationCfg
from isaaclab_assets.robots.cartpole import CARTPOLE_CFG


def make_robot_cfg() -> ArticulationCfg:
    actuator_cls = ImplicitActuatorCfg if args.model == "implicit" else IdealPDActuatorCfg
    stiffness = {".*": args.kp, "slider_.*": args.kp} if args.overlap else args.kp
    cart = actuator_cls(joint_names_expr=["slider_to_cart"], effort_limit_sim=400.0, stiffness=stiffness, damping=args.kd)
    pole = ImplicitActuatorCfg(joint_names_expr=["cart_to_pole"], effort_limit_sim=400.0, stiffness=0.0, damping=0.0)
    return CARTPOLE_CFG.replace(
        prim_path="/World/Robot", actuators={"cart_actuator": cart, "pole_actuator": pole}
    )


def main() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=args.dt, device=args.device))
    sim_utils.GroundPlaneCfg().func("/World/ground", sim_utils.GroundPlaneCfg())
    robot = Articulation(make_robot_cfg())
    sim.reset()

    cart = robot.find_joints("slider_to_cart")[0][0]
    target = torch.zeros_like(robot.data.joint_pos)
    target[:, cart] = 1.0  # 1 m 阶跃
    print(f"model={args.model} kp={args.kp} kd={args.kd} dt={args.dt:.4f}")
    print(f"写入 PhysX 的关节刚度 = {robot.data.joint_stiffness[0].tolist()}，阻尼 = {robot.data.joint_damping[0].tolist()}")

    checkpoints = {round(t / args.dt) for t in (0.1, 0.25, 0.5, 1.0, 2.0)}
    max_effort = 0.0
    for step in range(1, round(2.0 / args.dt) + 1):
        robot.set_joint_position_target(target)
        robot.write_data_to_sim()
        sim.step(render=False)
        robot.update(args.dt)
        max_effort = max(max_effort, robot.data.applied_torque[0, cart].abs().item())
        if step in checkpoints:
            print(f"t={step * args.dt:4.2f} s  cart 位置 {robot.data.joint_pos[0, cart].item():8.4f} m")
    print(f"施加的最大力 {max_effort:.1f} N（effort_limit_sim = 400）")

    # 退出三步：释放 SimulationContext → flush → close
    sim.clear_all_callbacks()
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
