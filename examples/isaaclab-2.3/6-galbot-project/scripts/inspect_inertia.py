# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：usd-core 25.x 或 Isaac Sim 5.1.0 自带的 pxr；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-09-30
"""检查转换得到的 Galbot USD 的质量、质心、惯量与碰撞体，并与 URDF 的 <inertial> 对照（6.1.4）。

- 每个刚体：质量、质心到刚体原点的距离、惯量主值、碰撞体个数与近似方式，以及可疑项标记；
- URDF 对照：合并固定关节后，一个 USD 刚体对应 URDF 中一组由固定关节连在一起的连杆，按组求质量之和；
- 按部件小计质量。

不需要启动 Isaac Sim::

    python scripts/inspect_inertia.py
    python scripts/inspect_inertia.py --usd generated/galbot_fixed_base/galbot.usd --urdf galbot_one_golf_fixed_base.urdf
"""

import argparse
import math
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

from pxr import Usd, UsdPhysics

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source" / "galbot_academy"))
from galbot_academy.assets.paths import PROJECT_ROOT, galbot_description_dir  # noqa: E402

PARTS = [("底盘与躯干底座", "base_link"), ("腿 / 躯干升降", "leg_"), ("头", "head_"), ("左臂", "left_arm_"),
         ("左夹爪", "left_gripper_"), ("右臂", "right_arm_"), ("右夹爪", "right_gripper_")]


def urdf_groups(urdf_path: Path) -> dict[str, float]:
    """URDF 连杆按"由固定关节连成的一组"归到组内最上层的连杆，返回 组根连杆名 → 质量之和。"""
    root = ET.parse(urdf_path).getroot()
    parent = {j.find("child").get("link"): (j.find("parent").get("link"), j.get("type")) for j in root.findall("joint")}
    mass = {}
    for link in root.findall("link"):
        m = link.find("inertial/mass")
        mass[link.get("name")] = float(m.get("value")) if m is not None else 0.0
    groups = defaultdict(float)
    for name, m in mass.items():
        top = name
        while top in parent and parent[top][1] == "fixed":
            top = parent[top][0]
        groups[top] += m
    return groups


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--usd", default=str(Path(os.environ.get("GALBOT_GENERATED_DIR", PROJECT_ROOT / "generated")) / "galbot_fixed_base" / "galbot.usd"))
    parser.add_argument("--urdf", default="galbot_one_golf_fixed_base.urdf", help="description 仓库 urdf/ 下的文件名")
    args = parser.parse_args()
    stage = Usd.Stage.Open(args.usd)
    prims = list(stage.Traverse(Usd.TraverseInstanceProxies()))
    bodies = [p for p in prims if p.HasAPI(UsdPhysics.RigidBodyAPI)]
    body_paths = {p.GetPath(): p for p in bodies}
    colliders = defaultdict(Counter)
    for p in prims:
        if p.HasAPI(UsdPhysics.CollisionAPI):
            q = p.GetPath()
            while q not in body_paths and q != q.GetParentPath():
                q = q.GetParentPath()
            approx = p.GetAttribute("physics:approximation").Get() if p.HasAPI(UsdPhysics.MeshCollisionAPI) else p.GetTypeName()
            colliders[q][approx or "none"] += 1
    groups = urdf_groups(galbot_description_dir() / "urdf" / args.urdf)

    print(f"{'刚体':34s} {'质量 kg':>8s} {'URDF 组质量':>10s} {'质心距原点 m':>11s}  惯量主值 kg·m²              碰撞体")
    part_mass, flags = defaultdict(float), []
    for p in bodies:
        name = p.GetName()
        m = p.GetAttribute("physics:mass").Get() or 0.0
        com = p.GetAttribute("physics:centerOfMass").Get()
        inertia = p.GetAttribute("physics:diagonalInertia").Get()
        d = math.dist(com, (0, 0, 0)) if com is not None else float("nan")
        i = sorted(inertia) if inertia is not None else [float("nan")] * 3
        coll = dict(colliders.get(p.GetPath(), {}))
        print(f"{name:34s} {m:8.3f} {groups.get(name, float('nan')):10.3f} {d:11.3f}  {i[0]:.2e} {i[1]:.2e} {i[2]:.2e}  {coll}")
        part = next((label for label, prefix in PARTS if name.startswith(prefix)), "其他")
        part_mass[part] += m
        if m < 0.01:
            flags.append(f"{name}：质量 {m} kg 过小")
        if i[0] + i[1] < i[2] * 0.999:
            flags.append(f"{name}：惯量主值不满足三角不等式")
        if i[2] > 0 and i[0] > 0 and i[2] / i[0] > 1000:
            flags.append(f"{name}：惯量主值相差 {i[2] / i[0]:.0f} 倍")
        if d > 0.3:
            flags.append(f"{name}：质心距刚体原点 {d:.2f} m")
        if not coll:
            flags.append(f"{name}：没有碰撞体")
        if abs(m - groups.get(name, m)) > 1e-3:
            flags.append(f"{name}：质量 {m:.3f} 与 URDF 组质量 {groups.get(name):.3f} 不一致")
    total = sum(part_mass.values())
    print(f"\n全机 {total:.3f} kg（URDF 全部连杆合计 {sum(groups.values()):.3f} kg）；按部件：" +
          "，".join(f"{k} {v:.2f}" for k, v in part_mass.items()))
    approx_all = sum((c for c in colliders.values()), Counter())
    print(f"碰撞体合计 {sum(approx_all.values())} 个：{dict(approx_all)}")
    print("可疑项：" + ("无" if not flags else ""))
    for f in flags:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
