# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
"""Isaac Academy 主线项目：Galbot One Golf（Isaac Lab 2.3.2）。

本站修改：模板原本在这里导入 `tasks` 与 `ui_extension_example`。改为不导入任何依赖 Kit 的模块，
使 `galbot_academy.assets` 等纯 Python 工具在不启动 Isaac Sim 时也能使用；
任务由各脚本显式 `import galbot_academy.tasks` 注册（模板生成的脚本已如此）。
"""
