# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）；pytest 9.1.1
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""训练回归的区间口径（7.4）：换评估种子后，成功率应落在 6.6.2 的 Wilson 区间里。

本文件不导入 isaaclab、不起 Kit，而是另起一个进程跑 eval_reach.py；这样不会和 tests/gpu/ 的 Kit 进程同时占着内存。
Kit 出错时返回码可能仍是 0，所以断言输出里的数，不只看返回码（7.4 坑一）。
"""

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = [pytest.mark.gpu, pytest.mark.slow]
ROOT = Path(__file__).resolve().parents[2]


def test_eval_success_rate_in_interval():
    """评估种子 1 的 < 5 cm 比例，应落在 6.6.2 表 3 种子 0 的 Wilson 区间 77.9–83.5% 里。"""
    if importlib.util.find_spec("isaaclab") is None:
        pytest.skip("要在装了 Isaac Lab 的 Python 里运行")
    if "omni.kit.app" in sys.modules:
        # 本进程已经起了 Kit（同时收集了 tests/gpu/），再起评估子进程就是两个 Kit 并存（7.4 坑四）
        pytest.skip("本进程已起 Kit：请单独运行 pytest tests/regression")
    ckpt = os.environ.get("GALBOT_REACH_CKPT")
    if not ckpt:
        pytest.skip("设 GALBOT_REACH_CKPT 指向 6.5.1 种子 42 的 model_999.pt")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "eval_reach.py"), "--headless", "--checkpoint", ckpt, "--seed", "1"],
        capture_output=True, text=True, timeout=900,
    )
    m = re.search(r"< 5 cm ([\d.]+)%", proc.stdout)
    assert m, f"返回码 {proc.returncode}，输出里没有评估结果：\n{proc.stdout[-2000:]}"
    assert 77.9 <= float(m.group(1)) <= 83.5
