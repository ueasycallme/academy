# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-09
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""克隆 N 个环境，测各阶段用时（3.7）；另有两个小实验看克隆的行为。

场景：地面、灯光，每个环境一台 Cartpole 和一个 0.2 kg 的小方块。

默认（计时）：打印 InteractiveScene 构建用时（Stage 上复制 Prim）、sim.reset() 用时（PhysX 解析）、
每个物理步的耗时（不渲染），以及 env_1 在 USD 里是"继承 env_0"还是"复制"。显存、主机内存请在外部按进程测量。

    python clone_bench.py --headless --num_envs 1024
    python clone_bench.py --headless --num_envs 1024 --no_replicate      # replicate_physics=False
    python clone_bench.py --headless --num_envs 1024 --no_fabric         # use_fabric=False
    python clone_bench.py --headless --num_envs 1024 --clone_in_fabric
    python clone_bench.py --headless --num_envs 1024 --stage_in_memory

--probe edit：建好场景后、reset 之前，用 USD 把 env_0 的方块质量改成 2 kg；reset 之后再改成 5 kg。
              打印 env_1 的 USD 属性与 PhysX 里各环境的质量，看改动传到了哪里。
--probe filter：env_spacing = 0，所有方块落在同一点；对照 filter_collisions 开 / 关时方块是否互相推开。

    python clone_bench.py --headless --num_envs 8 --probe edit
    python clone_bench.py --headless --num_envs 8 --probe edit --no_replicate
    python clone_bench.py --headless --num_envs 8 --probe filter
    python clone_bench.py --headless --num_envs 8 --probe filter --no_filter
"""

import argparse
import sys
import time

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="环境克隆的用时与行为")
parser.add_argument("--num_envs", type=int, default=16)
parser.add_argument("--no_replicate", action="store_true", help="replicate_physics=False")
parser.add_argument("--no_fabric", action="store_true", help="SimulationCfg.use_fabric=False")
parser.add_argument("--no_filter", action="store_true", help="filter_collisions=False")
parser.add_argument("--clone_in_fabric", action="store_true", help="InteractiveSceneCfg.clone_in_fabric=True")
parser.add_argument("--stage_in_memory", action="store_true", help="SimulationCfg.create_stage_in_memory=True")
parser.add_argument("--probe", choices=["edit", "filter"], default=None)
parser.add_argument("--steps", type=int, default=500, help="计时的物理步数")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch
from pxr import UsdPhysics

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.sim.utils.stage import attach_stage_to_usd_context, use_stage
from isaaclab.utils import configclass
from isaaclab_assets.robots.cartpole import CARTPOLE_CFG
from isaacsim.core.cloner import Cloner

DT = 1 / 120

# 给 Cloner.clone 套一个计时器：InteractiveScene 整体克隆环境、spawner 逐个克隆资产，都走这个方法
# （GridCloner.clone 最后也调用它）。累计用时就是"克隆用时"，建场景的其余时间主要是加载资产
_clone_time = [0.0]
_orig_clone = Cloner.clone


def _timed_clone(self, *a, **k):
    t = time.perf_counter()
    try:
        return _orig_clone(self, *a, **k)
    finally:
        _clone_time[0] += time.perf_counter() - t


Cloner.clone = _timed_clone


@configclass
class CloneSceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(prim_path="/World/ground", spawn=sim_utils.GroundPlaneCfg())
    light = AssetBaseCfg(prim_path="/World/light", spawn=sim_utils.DomeLightCfg(intensity=2000.0))
    robot: ArticulationCfg = CARTPOLE_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    cube = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Cube",
        spawn=sim_utils.CuboidCfg(
            size=(0.1, 0.1, 0.1),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(),
            mass_props=sim_utils.MassPropertiesCfg(mass=0.2),
            collision_props=sim_utils.CollisionPropertiesCfg(),
        ),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(1.0, 1.0, 0.5)),
    )


def main() -> None:
    sim_cfg = sim_utils.SimulationCfg(
        dt=DT, device=args.device, use_fabric=not args.no_fabric, create_stage_in_memory=args.stage_in_memory
    )
    sim = sim_utils.SimulationContext(sim_cfg)
    spacing = 0.0 if args.probe == "filter" else 4.0
    cfg = CloneSceneCfg(
        num_envs=args.num_envs,
        env_spacing=spacing,
        replicate_physics=not args.no_replicate,
        filter_collisions=not args.no_filter,
        clone_in_fabric=args.clone_in_fabric,
    )
    t0 = time.perf_counter()
    # 与 ManagerBasedEnv 的做法相同：在初始 Stage（可能在内存中）上建场景，再挂到 USD 上下文
    with use_stage(sim.get_initial_stage()):
        scene = InteractiveScene(cfg)
        attach_stage_to_usd_context()
    t_scene = time.perf_counter() - t0
    stage = sim.get_initial_stage()  # Stage in Memory 时，场景建在这个 Stage 上；否则它就是 USD 上下文里的 Stage

    env1 = stage.GetPrimAtPath("/World/envs/env_1")
    if env1.IsValid():
        inherits = env1.GetInherits().GetAllDirectInherits()
        n_specs = len(env1.GetPrimStack())
        cube1 = stage.GetPrimAtPath("/World/envs/env_1/Cube")
        print(f"[CLONE] env_1：继承 {[str(p) for p in inherits]}，Prim 规格层数 {n_specs}；"
              f"env_1/Cube 存在 {cube1.IsValid()}，自身在根层有规格 {bool(stage.GetRootLayer().GetPrimAtPath('/World/envs/env_1/Cube'))}")
    else:
        print("[CLONE] USD Stage 上没有 env_1（clone_in_fabric 时克隆只在 Fabric 里）")

    if args.probe == "edit":
        mass_attr = lambda i: UsdPhysics.MassAPI(stage.GetPrimAtPath(f"/World/envs/env_{i}/Cube")).GetMassAttr()  # noqa: E731
        mass_attr(0).Set(2.0)
        print(f"[EDIT] reset 前把 env_0/Cube 的 USD 质量改为 2.0：env_1 的 USD 质量读到 {mass_attr(1).Get()}")

    t0 = time.perf_counter()
    # Stage in Memory 时 reset 也要在 use_stage 里：资产初始化按当前 Stage 找 Prim（ManagerBasedEnv 也是这样做的）
    with use_stage(sim.get_initial_stage()):
        sim.reset()
    t_reset = time.perf_counter() - t0
    robot, cube = scene["robot"], scene["cube"]

    if args.probe == "edit":
        print(f"[EDIT] reset 后 PhysX 中各环境方块质量：{[round(m, 3) for m in cube.root_physx_view.get_masses().flatten().tolist()]}")
        mass_attr(0).Set(5.0)
        for _ in range(10):
            sim.step(render=False)
            scene.update(DT)
        print(f"[EDIT] reset 后再把 env_0 的 USD 质量改为 5.0、步进 10 步：env_1 的 USD 质量 {mass_attr(1).Get()}，"
              f"PhysX 中各环境的质量 {[round(m, 3) for m in cube.root_physx_view.get_masses().flatten().tolist()]}")

    if args.probe == "filter":
        for _ in range(round(1.5 / DT)):
            scene.write_data_to_sim()
            sim.step(render=False)
            scene.update(DT)
        p = cube.data.root_pos_w
        spread = (p[:, :2] - p[:, :2].mean(dim=0)).norm(dim=-1)
        print(f"[FILTER] filter_collisions={not args.no_filter}，env_spacing=0：1.5 s 后方块离平均位置的水平距离 "
              f"最大 {spread.max() * 100:.1f} cm，高度 {p[:, 2].min():.3f}–{p[:, 2].max():.3f} m")

    if args.probe is None:
        for _ in range(50):  # 热身
            scene.write_data_to_sim()
            sim.step(render=False)
            scene.update(DT)
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(args.steps):
            scene.write_data_to_sim()
            sim.step(render=False)
            scene.update(DT)
        torch.cuda.synchronize()
        t_step = (time.perf_counter() - t0) / args.steps
        print(f"[BENCH] num_envs {args.num_envs} replicate_physics {cfg.replicate_physics} use_fabric {sim_cfg.use_fabric} "
              f"clone_in_fabric {cfg.clone_in_fabric} stage_in_memory {sim_cfg.create_stage_in_memory}："
              f"建场景 {t_scene:.2f} s（其中克隆 {_clone_time[0]:.3f} s），reset {t_reset:.2f} s，每个物理步 {t_step * 1000:.2f} ms；"
              f"数值有限 {bool(torch.isfinite(robot.data.joint_pos).all())}")

    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
