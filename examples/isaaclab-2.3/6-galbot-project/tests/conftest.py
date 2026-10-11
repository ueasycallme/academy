# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.10（系统 python3，pytest 6.2.5）/ 3.10（CI，pytest 8.3.3）/ 3.11（Isaac 环境，pytest 9.1.1）；不依赖 Isaac Sim
# 验证日期：2026-10-11
"""tests/ 的总配置（7.4）。

- 把项目里不打包的目录（scripts/、ros2/）与 source/galbot_academy 放进 sys.path，测试可以直接 import；
- 当前 Python 里没有 isaaclab 时，不收集 tests/gpu/：那一层的 conftest 一被导入就会启动 Kit。
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for sub in ("source/galbot_academy", "scripts", "ros2"):
    sys.path.insert(0, str(ROOT / sub))

collect_ignore = [] if importlib.util.find_spec("isaaclab") else ["gpu"]
