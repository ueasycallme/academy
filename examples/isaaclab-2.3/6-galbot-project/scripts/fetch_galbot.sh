#!/usr/bin/env bash
# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证日期：2026-09-30
# 克隆 Galbot One Golf 描述仓库并固定到本站使用的 commit。
# 目标目录：环境变量 GALBOT_DESCRIPTION_DIR，默认 <项目根>/third_party/galbot_one_golf_description。
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${GALBOT_DESCRIPTION_DIR:-$PROJECT_ROOT/third_party/galbot_one_golf_description}"
COMMIT=2d496b053f0d4e9e2688f59fac66022f447226be
if [ ! -d "$DEST/.git" ]; then
    git clone https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description.git "$DEST"
fi
git -C "$DEST" fetch --quiet origin
git -C "$DEST" checkout --quiet "$COMMIT"
echo "Galbot 描述仓库：$DEST @ $(git -C "$DEST" rev-parse --short HEAD)"
