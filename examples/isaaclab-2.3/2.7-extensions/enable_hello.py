# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04（Isaac Sim 方式运行时）
"""在 Isaac Sim 里启用本目录的最小扩展（2.7），并演示三个常见坑。

    python enable_hello.py
"""

import sys
from pathlib import Path

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import omni.kit.app  # noqa: E402

manager = omni.kit.app.get_app().get_extension_manager()
ext_dir = Path(__file__).resolve().parent / "exts"

# 1. 扩展目录还不在搜索路径上：找不到这个扩展（这次失败会影响第 2 步，见页面坑一）
print(f"加入搜索路径前，启用 academy.hello：{manager.set_extension_enabled_immediate('academy.hello', True)}")

# 2. 把 exts/ 加进扩展搜索路径（等价于命令行 --ext-folder，或 .kit 里 [settings.app.exts] folders）
manager.add_path(str(ext_dir))
print(f"add_path 之后立即启用：{manager.set_extension_enabled_immediate('academy.hello', True)}")
simulation_app.update()  # 第 1 步对这个名字启用失败过，要等一帧才能成功（推断：失败的查找结果在下一帧前不刷新）
#                          没有先失败过时，add_path 之后立即启用就会成功（校验方对照实测）
print(f"update() 一帧之后再启用：{manager.set_extension_enabled_immediate('academy.hello', True)}")
ext_id = manager.get_enabled_extension_id("academy.hello")
print(f"启用后：is_extension_enabled = {manager.is_extension_enabled('academy.hello')}，ext_id = {ext_id}，"
      f"目录 {Path(manager.get_extension_path(ext_id)).name}")

import academy.hello  # noqa: E402  启用之后，它的 Python 模块才可以导入

print(f"调用扩展提供的函数：{academy.hello.greet()}")

# 3. 名字拼错：不报异常，只返回 False
print(f"启用拼错的名字 academy.helo：{manager.set_extension_enabled_immediate('academy.helo', True)}")

# 4. 反例：__init__.py 没有导入扩展类，扩展照样"启用"，但 on_startup 不会被调用（看上面有没有它的那行输出）
manager.set_extension_enabled_immediate("academy.hello_noimport", True)
print(f"academy.hello_noimport：is_extension_enabled = {manager.is_extension_enabled('academy.hello_noimport')}")

# 5. 停用：调用 on_shutdown
manager.set_extension_enabled_immediate("academy.hello", False)
print(f"停用后：is_extension_enabled = {manager.is_extension_enabled('academy.hello')}")

sys.stdout.flush()  # Kit 退出时不会刷新 stdout 缓冲（CONVENTIONS 第 5 节）
simulation_app.close()
