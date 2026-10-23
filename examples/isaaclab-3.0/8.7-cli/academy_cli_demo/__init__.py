# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab 3.0.0（v3.0.0 tag，commit e3f7d9ff1）+ Isaac Sim 6.2.0（pip，isaacsim 6.2.0.0）
# 验证日期：2026-10-23
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04
"""最小的外部任务包（8.7）：把一个任务挂进 `isaaclab train / play`。

三种挂法（页面"注册自己的任务"）：
1. `--external_callback academy_cli_demo.register_tasks`（加 PYTHONPATH 让 Python 找得到本包）；
2. 把本包装进环境，在 pyproject.toml 里声明 `isaaclab.tasks` 入口点组，`isaaclab` 启动子命令前自动导入；
3. 自己写脚本，在里面 `import academy_cli_demo.tasks` 后调用 `isaaclab_rl.entrypoints.api.train(...)`。
"""


def register_tasks() -> None:
    """供 `--external_callback` 调用：导入任务模块，完成 gym.register。

    返回值会与剩余命令行参数取交集后才交给 Hydra。返回 None 表示"全部保留"；
    返回列表（哪怕是空列表）就只保留列表里出现的参数（8.7 坑一）。
    """
    import academy_cli_demo.tasks  # noqa: F401

    return None


def register_tasks_returning_empty() -> list[str]:
    """反例（8.7 坑一）：返回空列表，`physics=…` 这类 Hydra 覆盖会被全部丢掉。"""
    import academy_cli_demo.tasks  # noqa: F401

    return []
