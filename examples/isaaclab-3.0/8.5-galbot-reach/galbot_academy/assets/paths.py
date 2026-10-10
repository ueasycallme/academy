# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.12（3.0 EA 环境；不依赖 Isaac Sim）
# 验证日期：2026-10-10
"""资产目录约定。

- Galbot 描述仓库（上游文件，不随本项目分发）：环境变量 `GALBOT_DESCRIPTION_DIR`，
  默认 `<项目根>/third_party/galbot_one_golf_description`，用 `scripts/fetch_galbot.sh` 克隆并固定到 GALBOT_COMMIT。
- 本项目生成的资产（转换得到的 USD 等派生物，不提交）：环境变量 `GALBOT_GENERATED_DIR`，
  默认 `<项目根>/generated`。
"""

import os
from pathlib import Path

GALBOT_REPO_URL = "https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description.git"
GALBOT_COMMIT = "2d496b053f0d4e9e2688f59fac66022f447226be"

# <项目根>/source/galbot_academy/galbot_academy/assets/paths.py → 向上 4 级是项目根
# 3.0 版（8.5）：本目录只是 2.3 项目的一个子集，不重新转换资产，直接复用 2.3 项目生成的 USD 与描述仓库
PROJECT_ROOT = Path(__file__).resolve().parents[3] / "isaaclab-2.3" / "6-galbot-project"


def galbot_description_dir() -> Path:
    """Galbot 描述仓库的根目录；不存在时给出如何获取的提示。"""
    path = Path(os.environ.get("GALBOT_DESCRIPTION_DIR", PROJECT_ROOT / "third_party" / "galbot_one_golf_description"))
    if not (path / "urdf").is_dir():
        raise FileNotFoundError(
            f"找不到 Galbot 描述仓库：{path}。请运行 scripts/fetch_galbot.sh，或设置环境变量 GALBOT_DESCRIPTION_DIR。"
        )
    return path


def generated_asset_dir() -> Path:
    """本项目生成资产的目录（不存在则创建）。"""
    path = Path(os.environ.get("GALBOT_GENERATED_DIR", PROJECT_ROOT / "generated"))
    path.mkdir(parents=True, exist_ok=True)
    return path
