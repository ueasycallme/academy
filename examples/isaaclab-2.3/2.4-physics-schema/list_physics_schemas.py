# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；另在 usd-core 26.8 上验证
# 验证日期：2026-09-30
"""列出一个 USD 资产上贴了哪些物理 Schema，并统计刚体、关节、驱动、碰撞体，找出 Articulation 根。

最后做三项检查（对应 2.4 页"常见坑"）：Articulation 根是否恰好一个、是否有嵌套刚体、是否有被关闭的碰撞体。

用法（两种环境都可以，见 2.2 页"两种查看方式"）::

    python list_physics_schemas.py [path/to/robot.usda] [--prims 10]

不传路径时，默认打开本仓库 third_party/ 下的 Galbot One Golf：
https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description （Apache-2.0）
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_USD = REPO_ROOT / "third_party/galbot_one_golf_description/usd/galbot_one_golf.usda"

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("usd", nargs="?", default=str(DEFAULT_USD), help="要打开的 USD 文件")
parser.add_argument("--prims", type=int, default=8, help="逐个列出前多少个带物理 Schema 的 Prim")
args = parser.parse_args()

simulation_app = None
try:
    from pxr import Usd
except ImportError:  # Isaac Sim 的 pip 环境：pxr 要在 SimulationApp 启动后才能导入
    from isaacsim import SimulationApp

    simulation_app = SimulationApp({"headless": True})
    from pxr import Usd


def applied_schemas(prim: Usd.Prim) -> list[str]:
    """读 apiSchemas 元数据，而不是 GetAppliedSchemas()：
    后者只列出当前环境已注册的 Schema，usd-core 里看不到 PhysxSchema 等扩展。"""
    list_op = prim.GetMetadata("apiSchemas")
    return list(list_op.ApplyOperations([])) if list_op else []


def is_physics(name: str) -> bool:
    return name.startswith(("Physics", "Physx"))


def main() -> None:
    stage = Usd.Stage.Open(args.usd)
    prims = list(stage.Traverse(Usd.TraverseInstanceProxies()))

    schema_count: Counter[str] = Counter()
    examples: dict[str, str] = {}
    type_count: Counter[str] = Counter()
    physics_prims = []
    for prim in prims:
        names = [n for n in applied_schemas(prim) if is_physics(n)]
        type_name = prim.GetTypeName()
        if type_name.startswith("Physics"):
            type_count[type_name] += 1
        if names or type_name.startswith("Physics"):
            physics_prims.append((prim, type_name, names))
        for name in names:
            schema_count[name] += 1
            examples.setdefault(name, str(prim.GetPath()))

    print("== 物理相关的 Prim 类型（IsA Schema）==")
    for name, n in type_count.most_common():
        print(f"  {n:4d}  {name}")
    print("\n== 物理相关的 API Schema ==")
    for name, n in schema_count.most_common():
        print(f"  {n:4d}  {name:36s} 例：{examples[name]}")

    print(f"\n== 前 {args.prims} 个带物理 Schema 的 Prim ==")
    for prim, type_name, names in physics_prims[: args.prims]:
        print(f"  {prim.GetPath()}  [{type_name or '-'}]  {names}")

    rigid = [p for p in prims if "PhysicsRigidBodyAPI" in applied_schemas(p)]
    joints = [p for p in prims if p.GetTypeName().endswith("Joint")]
    drives = [p for p in joints if any(n.startswith("PhysicsDriveAPI") for n in applied_schemas(p))]
    roots = [p for p in prims if "PhysicsArticulationRootAPI" in applied_schemas(p)]
    colliders = [p for p in prims if "PhysicsCollisionAPI" in applied_schemas(p)]
    approx = Counter(
        p.GetAttribute("physics:approximation").Get()
        for p in colliders
        if p.GetAttribute("physics:approximation").HasAuthoredValue()
    )
    scenes = [p for p in prims if p.GetTypeName() == "PhysicsScene"]

    print("\n== 统计 ==")
    print(f"刚体 {len(rigid)}，关节 {len(joints)}（带驱动 {len(drives)}），碰撞体 {len(colliders)}")
    print(f"网格碰撞近似方式：{dict(approx)}")
    print(f"Articulation 根：{[str(p.GetPath()) for p in roots]}")
    print(f"PhysicsScene：{[str(p.GetPath()) for p in scenes] or '无（场景由使用方创建，Isaac Lab 默认建在 /physicsScene）'}")

    print("\n== 检查 ==")
    print(f"[{'OK' if len(roots) == 1 else '!!'}] Articulation 根数量为 {len(roots)}（Isaac Lab 要求恰好一个）")
    rigid_paths = {p.GetPath() for p in rigid}
    nested = [p for p in rigid if any(a in rigid_paths for a in p.GetPath().GetAncestorsRange() if a != p.GetPath())]
    print(f"[{'OK' if not nested else '!!'}] 嵌套刚体 {len(nested)} 个" + (f"：{[str(p.GetPath()) for p in nested[:3]]}" if nested else ""))
    disabled = [p for p in colliders if p.GetAttribute("physics:collisionEnabled").Get() is False]
    print(f"[{'OK' if not disabled else '!!'}] 关闭碰撞的碰撞体 {len(disabled)} 个")


if __name__ == "__main__":
    main()
    if simulation_app is not None:
        simulation_app.close()
