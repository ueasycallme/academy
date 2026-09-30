# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.11 标准库（不依赖 Isaac Sim）；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-09-30
"""统计 Galbot 两个预置 URDF 的连杆与关节：按类型、按部件，以及 mimic 关节。

用法（项目根目录，已 pip install -e source/galbot_academy）::

    python scripts/galbot_joint_stats.py
"""

import collections
import re
import xml.etree.ElementTree as ET

from galbot_academy.assets import galbot_description_dir

# 部件 → 关节名正则（按顺序匹配，第一个命中的算数）
PARTS = [
    ("底盘主动轮", r"^wheel\d_joint$"),
    ("全向轮被动滚子", r"^wheel_\d_passive_\d+_joint$"),
    ("腿 / 躯干升降", r"^leg_joint\d$"),
    ("头", r"^head_joint\d$"),
    ("右臂", r"^right_arm_joint\d$"),
    ("右夹爪", r"^right_gripper_"),
    ("左臂", r"^left_arm_joint\d$"),
    ("左夹爪", r"^left_gripper_"),
]


def stats(urdf_path) -> None:
    root = ET.parse(urdf_path).getroot()
    joints = root.findall("joint")
    by_type = collections.Counter(j.get("type") for j in joints)
    print(f"== {urdf_path.name}：连杆 {len(root.findall('link'))}，关节 {len(joints)}，按类型 {dict(by_type)}")
    movable = [j for j in joints if j.get("type") != "fixed"]
    rows = collections.OrderedDict((name, [0, 0]) for name, _ in PARTS)
    other = []
    for j in movable:
        name = j.get("name")
        part = next((p for p, pat in PARTS if re.search(pat, name)), None)
        if part is None:
            other.append(name)
            continue
        rows[part][0] += 1
        rows[part][1] += j.find("mimic") is not None
    for part, (n, n_mimic) in rows.items():
        if n:
            extra = f"（其中 mimic {n_mimic} 个，独立自由度 {n - n_mimic}）" if n_mimic else ""
            print(f"  {part:12s} {n:3d} 个可动关节{extra}")
    if other:
        print(f"  未归类：{other}")
    root_links = {l.get("name") for l in root.findall("link")} - {j.find("child").get("link") for j in joints}
    print(f"  根连杆：{sorted(root_links)}")


def main() -> None:
    urdf_dir = galbot_description_dir() / "urdf"
    for name in ("galbot_one_golf.urdf", "galbot_one_golf_fixed_base.urdf"):
        stats(urdf_dir / name)


if __name__ == "__main__":
    main()
