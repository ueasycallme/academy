# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.11（不依赖 Isaac Sim；在 Isaac Sim 的 Python 里运行时会多记 isaacsim / isaaclab 版本）
# 验证日期：2026-10-11
"""写 / 校验生成资产的清单 generated/<变体>/MANIFEST.json（6.1.7）。

convert_galbot.py 转换完会自动写清单；这个脚本用于事后校验，或给已有的生成目录补写一份。

    python scripts/asset_manifest.py verify                    # 固定底座版；一致时退出码 0，不一致时 1
    python scripts/asset_manifest.py verify --variant wheeled --floating_base
    python scripts/asset_manifest.py write                     # 以当前文件与代码参数为准重写清单（确认无误后再用）
"""

import argparse
import sys
from pathlib import Path

# 不安装包也能用：把 source/galbot_academy 加进 sys.path（只用到 galbot_academy.assets 里不依赖 Kit 的模块）
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source" / "galbot_academy"))

from galbot_academy.assets.manifest import toolchain_info, verify_manifest, write_manifest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="写 / 校验资产清单")
    parser.add_argument("mode", choices=["verify", "write"])
    parser.add_argument("--variant", choices=["fixed_base", "wheeled"], default="fixed_base")
    parser.add_argument("--floating_base", action="store_true")
    args = parser.parse_args()
    if args.mode == "write":
        print(f"[manifest] 已写 {write_manifest(args.variant, args.floating_base)}")
        return 0
    diffs = verify_manifest(args.variant, args.floating_base)
    no_tool = toolchain_info()["isaacsim"] is None
    if no_tool:
        print("[manifest] 当前 Python 里没有 isaacsim，不比对工具链版本")
    if not diffs:
        print("[manifest] 一致：来源、参数、文件与清单相同（工具链未比对）" if no_tool else "[manifest] 一致：来源、工具链、参数、文件都与清单相同")
        return 0
    print(f"[manifest] 不一致，共 {len(diffs)} 项：")
    for d in diffs:
        print(f"  {d}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
