# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
# 注：--headless 由实现方验证；GUI（不加 --headless）由校验方在桌面环境验证（见 README）。
"""最小的 Isaac Lab standalone 脚本：与 isaacsim_minimal.py 相同的场景，改用 AppLauncher 启动。

用法::

    python isaaclab_minimal.py --headless
    python isaaclab_minimal.py --headless --device cpu
"""

import argparse
import sys

from isaaclab.app import AppLauncher

# 1. AppLauncher 往命令行里加入 --headless、--device、--enable_cameras、--kit_args 等参数，并据此启动 Kit
parser = argparse.ArgumentParser(description="最小的 Isaac Lab standalone 脚本")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# 2. Kit 启动后再导入 Isaac Lab 的其余模块（它们会间接导入 isaacsim / omni / pxr）
import isaaclab.sim as sim_utils
from isaaclab.assets import RigidObject, RigidObjectCfg


def main() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=1.0 / 120.0, device=args.device))
    ground = sim_utils.GroundPlaneCfg()
    ground.func("/World/ground", ground)
    cube_cfg = RigidObjectCfg(
        prim_path="/World/cube",
        spawn=sim_utils.CuboidCfg(
            size=(0.1, 0.1, 0.1),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(),
            mass_props=sim_utils.MassPropertiesCfg(mass=1.0),
            collision_props=sim_utils.CollisionPropertiesCfg(),
        ),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0.0, 0.0, 1.0)),
    )
    cube = RigidObject(cube_cfg)
    sim.reset()  # 与 World.reset() 同理：play 并初始化资产

    for i in range(240):  # 240 × dt(1/120) = 2 秒仿真时间
        sim.step(render=False)  # 只推进一个物理步（见 3.1 "时间参数"）
        if not args.headless and i % 2 == 1:
            sim.render()  # GUI 下单独刷新画面，不推进物理
        cube.update(sim.get_physics_dt())
    print(f"sim time {sim.current_time:.2f} s, cube z = {float(cube.data.root_pos_w[0, 2]):.3f} m")

    # 3. 退出前释放仿真上下文，否则 close() 可能一直不返回
    sim.clear_all_callbacks()
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()  # Kit 退出时不刷新 stdout，重定向到文件或管道时输出会丢
    simulation_app.close()
