# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""用 SimulationCfg 配置仿真：一个方块自由下落 1 秒，对比资产 data 与 USD 属性中的位置。

在 3.2 的 isaaclab_minimal.py 基础上，把 dt、render_interval、gravity、use_fabric 做成命令行参数。

用法::

    python sim_cfg_demo.py --headless                       # 默认：GPU、Fabric 开
    python sim_cfg_demo.py --headless --no_fabric           # 关闭 Fabric
    python sim_cfg_demo.py --headless --device cpu          # CPU 管线
    python sim_cfg_demo.py --headless --dt 0.005 --gravity -1.62   # 月球重力
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="SimulationCfg 演示")
parser.add_argument("--dt", type=float, default=1.0 / 120.0, help="物理步长 sim.dt（秒）")
parser.add_argument("--render_interval", type=int, default=2, help="每隔几个物理步渲染一次")
parser.add_argument("--gravity", type=float, default=-9.81, help="z 方向重力加速度（m/s²）")
parser.add_argument("--no_fabric", action="store_true", help="设置 use_fabric=False")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import isaaclab.sim as sim_utils
from isaaclab.assets import RigidObject, RigidObjectCfg


def main() -> None:
    sim_cfg = sim_utils.SimulationCfg(
        dt=args.dt,
        render_interval=args.render_interval,
        gravity=(0.0, 0.0, args.gravity),
        device=args.device,
        use_fabric=not args.no_fabric,
    )
    sim = sim_utils.SimulationContext(sim_cfg)
    cube = RigidObject(
        RigidObjectCfg(
            prim_path="/World/cube",
            spawn=sim_utils.CuboidCfg(
                size=(0.1, 0.1, 0.1),
                rigid_props=sim_utils.RigidBodyPropertiesCfg(),
                mass_props=sim_utils.MassPropertiesCfg(mass=1.0),
                collision_props=sim_utils.CollisionPropertiesCfg(),
            ),
            init_state=RigidObjectCfg.InitialStateCfg(pos=(0.0, 0.0, 10.0)),  # 没有地面，自由下落
        )
    )
    sim.reset()

    steps = round(1.0 / args.dt)  # 1 秒仿真时间
    for _ in range(steps):
        sim.step(render=False)
        cube.update(sim.get_physics_dt())

    usd_z = sim.stage.GetPrimAtPath("/World/cube").GetAttribute("xformOp:translate").Get()[2]
    print(f"device={sim.device} use_fabric={sim_cfg.use_fabric} dt={sim.get_physics_dt():.4f} steps={steps}")
    print(f"sim time {sim.current_time:.3f} s")
    print(f"data.root_pos_w z = {float(cube.data.root_pos_w[0, 2]):.3f} m  (张量在 {cube.data.root_pos_w.device})")
    print(f"USD xformOp:translate z = {usd_z:.3f} m")
    print(f"理论值 z = {10.0 + 0.5 * args.gravity * 1.0:.3f} m")

    # 退出三步：释放 SimulationContext → flush → close（CONVENTIONS 第 5 节）
    sim.clear_all_callbacks()
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
