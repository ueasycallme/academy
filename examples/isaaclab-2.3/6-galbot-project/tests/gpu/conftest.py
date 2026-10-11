# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）；pytest 9.1.1
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""有 GPU 层（7.4）：整个 pytest 进程只起一次 Kit。

做法同 Isaac Lab v2.3.2 自己的测试：在任何 isaaclab / omni 模块被导入之前创建 AppLauncher。
放在 conftest 里，是为了让本目录的所有测试文件共用这一个 Kit；不调用 close()，进程结束时随之退出。
"""

import sys

from isaaclab.app import AppLauncher

# Kit 会解析 sys.argv。pytest 的参数（如 -m "not slow"）传进去，Kit 报 "Ill formed parameter: -m" 后段错误；
# AppLauncher 只清理 "-m pytest" 这一种（app_launcher.py L806–L815）。所以起 Kit 时只留程序名（7.4 坑二）
_pytest_argv, sys.argv = sys.argv, sys.argv[:1]
simulation_app = AppLauncher(headless=True).app
sys.argv = _pytest_argv

import gymnasium as gym  # noqa: E402
import omni.usd  # noqa: E402
import pytest  # noqa: E402

import galbot_academy.tasks  # noqa: E402, F401  注册任务
from isaaclab_tasks.utils import parse_env_cfg  # noqa: E402


@pytest.fixture
def make_env():
    """建环境的工厂：先换新 stage 再建；用例结束时一定 close。"""
    envs = []

    def _make(task: str, num_envs: int, seed: int = 0):
        # 每个环境建在一个新 stage 上，做法同 Isaac Lab 自己的测试（test_manager_based_env.py L118）。
        # 不这样做，上一个环境 close() 后在同一进程里再建环境会卡住（本站实测，7.4 坑三）
        omni.usd.get_context().new_stage()
        cfg = parse_env_cfg(task, device="cuda:0", num_envs=num_envs)
        cfg.seed = seed
        env = gym.make(task, cfg=cfg)
        envs.append(env)
        return env

    yield _make
    for env in envs:
        env.close()
