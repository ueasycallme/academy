# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""加载 Cartpole，打印 Articulation.data 的关键字段，给小车施加力并步进，观察状态变化。

还演示两点：默认根状态在环境系、实际根位置在世界系；不调用 update() 时读到的是旧数据。

用法::

    python articulation_data_demo.py --headless --num_envs 4
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Articulation.data 演示")
parser.add_argument("--num_envs", type=int, default=4, help="环境数量")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils import configclass
from isaaclab_assets.robots.cartpole import CARTPOLE_CFG


@configclass
class CartpoleOnlySceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(prim_path="/World/ground", spawn=sim_utils.GroundPlaneCfg())
    robot: ArticulationCfg = CARTPOLE_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")


def main() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=1.0 / 120.0, device=args.device))
    scene = InteractiveScene(CartpoleOnlySceneCfg(num_envs=args.num_envs, env_spacing=4.0))
    sim.reset()
    robot = scene["robot"]
    data = robot.data

    print("== 名字与索引 ==")
    print(f"joint_names = {robot.joint_names}")
    print(f"body_names  = {robot.body_names}")
    cart_ids, cart_names = robot.find_joints("slider_.*")
    print(f"find_joints('slider_.*') -> {cart_ids}, {cart_names}")

    print("== 字段形状 ==")
    for name in ["root_state_w", "root_pos_w", "body_pos_w", "joint_pos", "joint_vel", "joint_acc",
                 "default_root_state", "default_joint_pos", "joint_pos_limits", "joint_stiffness", "joint_damping"]:
        print(f"{name:20s} {tuple(getattr(data, name).shape)}")

    print("== 坐标系：默认根状态在环境系，root_pos_w 在世界系 ==")
    print(f"env_origins[1]            = {scene.env_origins[1].tolist()}")
    print(f"default_root_state[1, :3] = {data.default_root_state[1, :3].tolist()}")
    print(f"root_pos_w[1]             = {[round(v, 3) for v in data.root_pos_w[1].tolist()]}")
    print(f"joint_pos_limits[0]       = {data.joint_pos_limits[0].tolist()}")
    print(f"joint_stiffness[0] = {data.joint_stiffness[0].tolist()}, joint_damping[0] = {data.joint_damping[0].tolist()}")

    # 给小车一个 50 N 的推力（cart_actuator 刚度为 0，只能用力或速度控制）
    effort = torch.zeros_like(data.joint_pos)
    effort[:, cart_ids[0]] = 50.0

    print("== 不调用 update()：读到的是旧数据 ==")
    before = data.joint_pos[0, cart_ids[0]].item()
    for _ in range(60):
        robot.set_joint_effort_target(effort)
        robot.write_data_to_sim()
        sim.step(render=False)  # 故意不调用 robot.update()
    print(f"推进 0.5 s 后未 update：cart 位置 {data.joint_pos[0, cart_ids[0]].item():.4f}（推进前 {before:.4f}）")
    robot.update(sim.get_physics_dt())
    print(f"调用 update() 之后：     cart 位置 {data.joint_pos[0, cart_ids[0]].item():.4f}")

    print("== 正常循环：设目标 → 写入 → 步进 → update ==")
    for _ in range(60):
        robot.set_joint_effort_target(effort)
        robot.write_data_to_sim()
        sim.step(render=False)
        robot.update(sim.get_physics_dt())
    print(f"再推进 0.5 s：cart 位置 {data.joint_pos[:, cart_ids[0]].tolist()}")
    print(f"cart 速度 {[round(v, 3) for v in data.joint_vel[:, cart_ids[0]].tolist()]}")
    print(f"applied_torque[0] = {data.applied_torque[0].tolist()}")

    # 退出三步：释放 SimulationContext → flush → close
    sim.clear_all_callbacks()
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
