# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""用 InteractiveSceneCfg 搭一个含地面、灯、Cartpole 与小方块的场景，克隆 N 份，打印场景信息。

用法::

    python scene_demo.py --headless --num_envs 16
    python scene_demo.py --headless --num_envs 16 --ground_global     # 地面设为全局碰撞组（collision_group=-1）
    python scene_demo.py --headless --num_envs 16 --spacing 0          # 所有环境重叠，检验环境间碰撞过滤
    python scene_demo.py --headless --num_envs 16 --spacing 0 --no_filter
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="InteractiveScene 演示")
parser.add_argument("--num_envs", type=int, default=16, help="环境数量")
parser.add_argument("--ground_global", action="store_true", help="地面使用 collision_group=-1")
parser.add_argument("--spacing", type=float, default=4.0, help="环境间距 env_spacing（设为 0 时所有环境重叠）")
parser.add_argument("--no_filter", action="store_true", help="设置 filter_collisions=False")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils import configclass
from isaaclab_assets.robots.cartpole import CARTPOLE_CFG


@configclass
class DemoSceneCfg(InteractiveSceneCfg):
    # 全局实体：路径不含 {ENV_REGEX_NS}，只生成一份
    ground = AssetBaseCfg(prim_path="/World/ground", spawn=sim_utils.GroundPlaneCfg())
    light = AssetBaseCfg(prim_path="/World/light", spawn=sim_utils.DomeLightCfg(intensity=2000.0))
    # 每个环境一份：路径以 {ENV_REGEX_NS} 开头
    robot: ArticulationCfg = CARTPOLE_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    cube = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Cube",
        spawn=sim_utils.CuboidCfg(
            size=(0.1, 0.1, 0.1),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(),
            mass_props=sim_utils.MassPropertiesCfg(mass=0.2),
            collision_props=sim_utils.CollisionPropertiesCfg(),
        ),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(1.0, 1.0, 1.0)),
    )


def main() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=1.0 / 120.0, device=args.device))
    scene_cfg = DemoSceneCfg(num_envs=args.num_envs, env_spacing=args.spacing, filter_collisions=not args.no_filter)
    if args.ground_global:
        scene_cfg.ground.collision_group = -1
    scene = InteractiveScene(scene_cfg)
    sim.reset()

    print(f"env_ns = {scene.env_ns}, env_regex_ns = {scene.env_regex_ns}")
    print(f"robot prim_path = {scene_cfg.robot.prim_path}")
    env_prims = [p for p in sim.stage.GetPrimAtPath("/World/envs").GetChildren()]
    print(f"/World/envs 下的环境 Prim 数 = {len(env_prims)}，前三个：{[p.GetName() for p in env_prims[:3]]}")
    print(f"env_origins 形状 {tuple(scene.env_origins.shape)}，前三行：{scene.env_origins[:3].tolist()}")
    print(f"scene.keys() = {scene.keys()}")
    print(f"articulations = {list(scene.articulations)}，rigid_objects = {list(scene.rigid_objects)}")
    print(f"robot 关节 = {scene['robot'].joint_names}，joint_pos 形状 {tuple(scene['robot'].data.joint_pos.shape)}")

    for _ in range(240):  # 2 秒：方块从 1 m 落下
        scene.write_data_to_sim()
        sim.step(render=False)
        scene.update(sim.get_physics_dt())
    cube_z = scene["cube"].data.root_pos_w[:, 2]
    print(
        f"ground collision_group = {scene_cfg.ground.collision_group}，env_spacing = {scene_cfg.env_spacing}，"
        f"filter_collisions = {scene_cfg.filter_collisions}：方块高度 最小 {cube_z.min():.3f} m，最大 {cube_z.max():.3f} m"
    )

    # 退出三步：释放 SimulationContext → flush → close
    sim.clear_all_callbacks()
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
