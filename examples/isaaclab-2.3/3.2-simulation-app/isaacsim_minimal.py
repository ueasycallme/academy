# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（本脚本只用 Isaac Sim）
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
# 注：headless 由实现方验证；--gui 由校验方在桌面环境验证（见 README）。
"""最小的 Isaac Sim standalone 脚本：一个方块落到地面上。

用法::

    python isaacsim_minimal.py          # headless
    python isaacsim_minimal.py --gui    # 打开窗口（需要显示器）
"""

import argparse
import sys

# 1. 先启动 Kit：SimulationApp 必须在导入任何 isaacsim.* / omni.* / pxr 模块之前创建
from isaacsim import SimulationApp

parser = argparse.ArgumentParser(description="最小的 Isaac Sim standalone 脚本")
parser.add_argument("--gui", action="store_true", help="打开 GUI 窗口（默认 headless）")
args = parser.parse_args()
simulation_app = SimulationApp({"headless": not args.gui})

# 2. Kit 启动后，扩展模块才可以导入
from isaacsim.core.api import World
from isaacsim.core.api.objects import DynamicCuboid


def main() -> None:
    world = World(stage_units_in_meters=1.0, physics_dt=1.0 / 120.0, rendering_dt=1.0 / 60.0)
    world.scene.add_default_ground_plane()
    cube = world.scene.add(DynamicCuboid(prim_path="/World/cube", name="cube", position=[0.0, 0.0, 1.0], size=0.1))
    world.reset()  # stop + play，并初始化场景对象；不调用它，物理不会推进

    for i in range(240):  # 240 × physics_dt(1/120) = 2 秒仿真时间
        world.step(render=False)  # 只推进一个物理步；render=True 会推进一整个 rendering_dt（见 3.1 "时间参数"）
        if args.gui and i % 2 == 1:
            world.render()  # 需要画面时单独刷新，不推进物理
    print(f"sim time {world.current_time:.2f} s, cube z = {float(cube.get_world_pose()[0][2]):.3f} m")

    # 3. 退出前释放仿真上下文，否则 close() 可能一直不返回
    world.clear_all_callbacks()
    world.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()  # Kit 退出时不刷新 stdout，重定向到文件或管道时输出会丢
    simulation_app.close()
