# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-08
"""看一个 Kit 应用（2.6）：AppLauncher 选了哪个 .kit、启用了多少扩展、几个设置的值，以及在运行时读写设置。

用法（在 Isaac Lab 环境中）::

    python kit_inspect.py --headless
    python kit_inspect.py --headless --enable_cameras
    python kit_inspect.py --headless --kit_args="--/physics/updateToUsd=true"
"""

import argparse
import sys
import time

# 1. 启动前：Omniverse 的模块还不在搜索路径上
try:
    import omni.kit.app  # noqa: F401

    print("启动前 import omni.kit.app：成功")
except ImportError as e:
    print(f"启动前 import omni.kit.app：{type(e).__name__}")

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

t0 = time.perf_counter()
launcher = AppLauncher(args)
simulation_app = launcher.app
print(f"启动用时 {time.perf_counter() - t0:.1f} s")

# 2. 启动后才能导入 Kit 的模块
import carb
import omni.kit.app

app = omni.kit.app.get_app()
settings = carb.settings.get_settings()

print(f"体验文件（.kit）：{launcher._sim_experience_file.split('/')[-1]}")  # AppLauncher 的内部属性，仅作演示
print(f"Kit 版本：{app.get_kit_version()}")
manager = app.get_extension_manager()
enabled = [e for e in manager.get_extensions() if e.get("enabled")]
print(f"已启用的扩展：{len(enabled)} 个（已发现 {len(manager.get_extensions())} 个）")
for name in ["omni.physx", "omni.physx.fabric", "omni.kit.material.library", "isaacsim.core.api"]:
    print(f"  {name:28s} {'启用' if manager.is_extension_enabled(name) else '未启用'}")

# 3. 设置：.kit 的 [settings] 节、命令行 --/路径=值、代码里 set，都写进同一棵设置树
for path in ["/app/version", "/isaaclab/cameras_enabled", "/app/useFabricSceneDelegate", "/physics/updateToUsd"]:
    print(f"  {path:30s} = {settings.get(path)}")
settings.set("/physics/updateToUsd", True)
print(f"运行时 set 之后 /physics/updateToUsd = {settings.get('/physics/updateToUsd')}")

# 4. 事件循环：每次 update() 推进一帧
frame = app.get_update_number()
for _ in range(3):
    simulation_app.update()
print(f"update() 3 次：帧号 {frame} → {app.get_update_number()}")

sys.stdout.flush()  # Kit 退出时不会刷新 stdout 缓冲（CONVENTIONS 第 5 节）
simulation_app.close()
