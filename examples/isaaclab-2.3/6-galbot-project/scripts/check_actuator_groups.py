# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：usd-core 25.x 或 Isaac Sim 5.1.0 自带的 pxr；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
"""检查执行器分组：每个可动关节恰好被一组匹配（6.1.6）。不需要启动 Isaac Sim。

匹配规则与 Isaac Lab 相同：对关节名做 re.fullmatch（isaaclab/utils/string.py 的 resolve_matching_names）。
关节名从转换得到的 USD 中读取（RevoluteJoint / PrismaticJoint）。

    python scripts/check_actuator_groups.py
    python scripts/check_actuator_groups.py --usd generated/galbot_wheeled/galbot.usd --wheeled
"""

import argparse
import os
import re
import sys
from pathlib import Path

from pxr import Usd, UsdPhysics

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source" / "galbot_academy"))
from galbot_academy.assets.drives import GROUPS, MIMIC_FOLLOWERS  # noqa: E402
from galbot_academy.assets.paths import PROJECT_ROOT  # noqa: E402

# 轮式版额外的两组，与 galbot.py 中 GALBOT_ONE_GOLF_WHEELED_CFG 一致
WHEELED_GROUPS = {"wheels": ["wheel[1-4]_joint"], "rollers": ["wheel_[1-4]_passive_.*"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    gen = Path(os.environ.get("GALBOT_GENERATED_DIR", PROJECT_ROOT / "generated"))
    parser.add_argument("--usd", default=str(gen / "galbot_fixed_base" / "galbot.usd"))
    parser.add_argument("--wheeled", action="store_true", help="加上轮式版的 wheels / rollers 两组")
    args = parser.parse_args()

    stage = Usd.Stage.Open(args.usd)
    joints = [p.GetName() for p in stage.Traverse()
              if p.IsA(UsdPhysics.RevoluteJoint) or p.IsA(UsdPhysics.PrismaticJoint)]
    groups = {name: spec["joint_names_expr"] for name, spec in GROUPS.items()}
    groups["mimic"] = MIMIC_FOLLOWERS
    if args.wheeled:
        groups.update(WHEELED_GROUPS)

    bad = 0
    per_group = {g: 0 for g in groups}
    for j in joints:
        hits = [(g, e) for g, exprs in groups.items() for e in exprs if re.fullmatch(e, j)]
        if len(hits) != 1:
            bad += 1
            print(f"  {j}: {'没有组匹配' if not hits else '被多组匹配 ' + str(hits)}")
        else:
            per_group[hits[0][0]] += 1
    unused = [(g, e) for g, exprs in groups.items() for e in exprs if not any(re.fullmatch(e, j) for j in joints)]
    print(f"可动关节 {len(joints)} 个；各组匹配数：{per_group}")
    for g, e in unused:
        print(f"  表达式没有匹配到任何关节：{g} / {e}")
    print("结果：每个关节恰好被一组匹配" if bad == 0 and not unused else f"结果：有 {bad} 个关节有问题，{len(unused)} 条表达式落空")
    sys.exit(1 if bad or unused else 0)


if __name__ == "__main__":
    main()
