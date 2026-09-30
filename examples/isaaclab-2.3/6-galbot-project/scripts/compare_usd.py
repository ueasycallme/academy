# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：usd-core 25.x 或 Isaac Sim 5.1.0 自带的 pxr；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-09-30
"""按同一组维度统计若干份机器人 USD，用来对比厂商 USD 与自己转换的 USD（6.1.3）。

不需要启动 Isaac Sim：装有 usd-core 的 Python，或 Isaac Sim 的 Python 都可以::

    python scripts/compare_usd.py                       # 默认对比厂商 USD 与 generated/ 下的转换结果
    python scripts/compare_usd.py a.usd b.usd --joint left_arm_joint1
"""

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

from pxr import Usd, UsdGeom, UsdPhysics, UsdShade

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source" / "galbot_academy"))
from galbot_academy.assets.paths import PROJECT_ROOT, galbot_description_dir  # noqa: E402


def applied(prim) -> list[str]:
    """读 apiSchemas 元数据（usd-core 中未注册的 PhysxSchema 也能看到），同 2.4 的脚本。"""
    list_op = prim.GetMetadata("apiSchemas")
    return list(list_op.ApplyOperations([])) if list_op else []


def stats(path: str, joint_name: str) -> dict:
    stage = Usd.Stage.Open(path)
    composed = list(stage.Traverse())  # 组合结构的统计（实例本身）
    prims = list(stage.Traverse(Usd.TraverseInstanceProxies()))  # 物理统计要进入实例内部
    roots = [p.GetPath().pathString for p in prims if p.HasAPI(UsdPhysics.ArticulationRootAPI)]
    bodies = [p for p in prims if p.HasAPI(UsdPhysics.RigidBodyAPI)]
    joints = [p for p in prims if p.IsA(UsdPhysics.Joint)]
    joint_types = Counter(p.GetTypeName().replace("Physics", "") for p in joints)
    drives = [p for p in joints if p.HasAPI(UsdPhysics.DriveAPI, "angular") or p.HasAPI(UsdPhysics.DriveAPI, "linear")]
    mimics = [p for p in joints if any(s.startswith("PhysxMimicJointAPI") for s in applied(p))]

    def attr_range(name, items):
        vals = [p.GetAttribute(name).Get() for p in items if p.GetAttribute(name).HasAuthoredValue()]
        vals = [v for v in vals if v is not None]
        return (min(vals), max(vals), len(vals)) if vals else None

    masses = [p.GetAttribute("physics:mass").Get() or 0.0 for p in prims if p.HasAPI(UsdPhysics.MassAPI)]
    approx = Counter(p.GetAttribute("physics:approximation").Get() for p in prims if p.HasAPI(UsdPhysics.MeshCollisionAPI))
    colliders = sum(1 for p in prims if p.HasAPI(UsdPhysics.CollisionAPI))
    # 用 API 名字判断，不依赖 PhysxSchema 模块（usd-core 中没有它）
    self_coll = [p.GetAttribute("physxArticulation:enabledSelfCollisions").Get() for p in prims if "PhysxArticulationAPI" in applied(p)]
    one = next((p for p in joints if p.GetName() == joint_name), None)

    def get(p, name):
        a = p.GetAttribute(name) if p else None
        return a.Get() if a and a.HasAuthoredValue() else None

    layers = {Path(l.realPath) for l in stage.GetUsedLayers() if l.realPath}
    size = sum(f.stat().st_size for f in layers if f.is_file())
    root = stage.GetDefaultPrim()
    return {
        "defaultPrim": root.GetPath().pathString if root else None,
        "Prim 总数（不含 / 含实例内部）": (len(composed), len(prims)),
        "变体集": {vs: root.GetVariantSet(vs).GetVariantSelection() for vs in root.GetVariantSets().GetNames()} if root else {},
        "带 reference / payload 的 Prim": sum(1 for p in composed if p.HasAuthoredReferences() or p.HasAuthoredPayloads()),
        "实例（instance）Prim": sum(1 for p in composed if p.IsInstance()),
        "Articulation 根": roots,
        "刚体": len(bodies),
        "关节（按类型）": dict(joint_types),
        "带驱动的关节": len(drives),
        "mimic 关节": len(mimics),
        "stiffness 范围（min, max, 个数）": attr_range("drive:angular:physics:stiffness", drives),
        "damping 范围": attr_range("drive:angular:physics:damping", drives),
        "maxForce 范围": attr_range("drive:angular:physics:maxForce", drives),
        "maxJointVelocity 范围": attr_range("physxJoint:maxJointVelocity", joints),
        f"{joint_name}：stiffness / damping / maxForce / maxJointVelocity": (
            get(one, "drive:angular:physics:stiffness"), get(one, "drive:angular:physics:damping"),
            get(one, "drive:angular:physics:maxForce"), get(one, "physxJoint:maxJointVelocity")),
        "总质量 kg（带 MassAPI 的 Prim 数）": (round(sum(masses), 3), len(masses)),
        "碰撞体（网格近似方式）": (colliders, dict(approx)),
        "自碰撞（Articulation 上的设置）": self_coll,
        "材质数": sum(1 for p in prims if p.IsA(UsdShade.Material)),
        "metersPerUnit / upAxis": (UsdGeom.GetStageMetersPerUnit(stage), UsdGeom.GetStageUpAxis(stage)),
        "用到的图层文件数 / 总大小 MB": (len(layers), round(size / 2**20, 1)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("usd", nargs="*", help="要对比的 USD；默认对比厂商 USD 与 generated/ 下的两份转换结果")
    parser.add_argument("--joint", default="left_arm_joint1", help="单独列出的关节")
    args = parser.parse_args()
    files = args.usd or [
        str(galbot_description_dir() / "usd" / "galbot_one_golf.usda"),
        str(Path(os.environ.get("GALBOT_GENERATED_DIR", PROJECT_ROOT / "generated")) / "galbot_wheeled" / "galbot.usd"),
        str(Path(os.environ.get("GALBOT_GENERATED_DIR", PROJECT_ROOT / "generated")) / "galbot_fixed_base" / "galbot.usd"),
    ]
    results = [(f, stats(f, args.joint)) for f in files if Path(f).exists()]
    for f, _ in results:
        print(f"[{results.index((f, _)) + 1}] {f}")
    for key in results[0][1]:
        print(f"\n{key}")
        for i, (_, r) in enumerate(results, 1):
            print(f"  [{i}] {r[key]}")


if __name__ == "__main__":
    main()
