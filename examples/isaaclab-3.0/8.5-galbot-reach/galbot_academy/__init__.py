# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0（commit e3f7d9ff1）+ Isaac Sim 6.2.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-23
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04
"""Isaac Academy 主线项目：Galbot One Golf（Isaac Lab 2.3.2）；本目录是 3.0 版的子集（8.5）。

本站修改：模板原本在这里导入 `tasks` 与 `ui_extension_example`。改为不导入任何依赖 Kit 的模块，
使 `galbot_academy.assets` 等纯 Python 工具在不启动 Isaac Sim 时也能使用；
任务由各脚本显式 `import galbot_academy.tasks` 注册（模板生成的脚本已如此）。
"""


def register_tasks() -> None:
    """供 3.0 的 `isaaclab train --external_callback galbot_academy.register_tasks` 调用：导入任务包以注册 Galbot-Reach。

    必须返回 None：train 入口把剩余参数与回调的返回值取交集后交给 Hydra（train_rsl_rl.py 的 _parse_args），
    返回空列表会把 physics=newton_mjwarp 这类覆盖项全部丢掉，返回 None 才保留全部。
    """
    import galbot_academy.tasks  # noqa: F401

    return None
