# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；另在 usd-core 26.8 上验证
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04（Isaac Sim 方式运行时）
"""打开一个 USD 文件，打印它的元数据、Prim 树、类型统计，以及一个关节和一个网格的属性。

两种运行方式::

    # 方式一：独立环境里装 usd-core（不需要 Isaac Sim，秒级启动）
    python inspect_usd.py path/to/robot.usda

    # 方式二：在 Isaac Sim 的 pip 环境里运行（pxr 要在 SimulationApp 启动后才能导入，脚本会自动 headless 启动）
    python inspect_usd.py path/to/robot.usda

不传路径时，默认打开本仓库 third_party/ 下的 Galbot One Golf：
https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description （Apache-2.0）
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_USD = REPO_ROOT / "third_party/galbot_one_golf_description/usd/galbot_one_golf.usda"

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("usd", nargs="?", default=str(DEFAULT_USD), help="要打开的 USD 文件")
parser.add_argument("--depth", type=int, default=3, help="Prim 树打印的层数")
parser.add_argument("--joint", default="/galbot_one_golf/joints/left_arm_joint1", help="要展示属性的关节 Prim 路径")
parser.add_argument("--mesh", default="/galbot_one_golf/left_arm_link1/visuals/link1/mesh_22", help="要展示属性的网格 Prim 路径")
args = parser.parse_args()

# usd-core 环境可以直接导入 pxr；Isaac Sim 的 pip 环境要先启动 SimulationApp
simulation_app = None
try:
    from pxr import Usd, UsdGeom
except ImportError:
    from isaacsim import SimulationApp

    simulation_app = SimulationApp({"headless": True})
    from pxr import Usd, UsdGeom


def short(value, limit: int = 50) -> str:
    text = str(value)
    return text if len(text) <= limit else text[:limit] + "…"


def print_tree(prim: Usd.Prim, depth: int, max_depth: int, max_children: int = 6) -> None:
    children = prim.GetChildren()
    name = prim.GetName() or "/"
    print(f"{'  ' * depth}{name}  [{prim.GetTypeName() or '-'}]  子节点 {len(children)}")
    if depth >= max_depth:
        return
    for child in children[:max_children]:
        print_tree(child, depth + 1, max_depth, max_children)
    if len(children) > max_children:
        print(f"{'  ' * (depth + 1)}… 另有 {len(children) - max_children} 个")


def print_properties(prim: Usd.Prim) -> None:
    print(f"{prim.GetPath()}  类型 {prim.GetTypeName()}  applied schemas {list(prim.GetAppliedSchemas())}")
    for attr in prim.GetAttributes():
        if attr.HasAuthoredValue():
            value = attr.Get()
            size = f"  ({len(value)} 个)" if type(value).__name__.endswith("Array") else ""  # 只给数组类型标长度
            print(f"  attribute  {attr.GetName():40s} {str(attr.GetTypeName()):12s} {short(value)}{size}")
    for rel in prim.GetRelationships():
        if rel.GetTargets():
            print(f"  relationship {rel.GetName():38s} -> {[str(t) for t in rel.GetTargets()]}")


def main() -> None:
    print(f"USD 版本: {Usd.GetVersion()}")
    stage = Usd.Stage.Open(args.usd)

    print("\n== Stage 元数据 ==")
    print(f"defaultPrim   : {stage.GetDefaultPrim().GetPath()}")
    print(f"upAxis        : {UsdGeom.GetStageUpAxis(stage)}")
    print(f"metersPerUnit : {UsdGeom.GetStageMetersPerUnit(stage)}")
    variant_sets = stage.GetDefaultPrim().GetVariantSets()
    print(f"变体选择      : {({n: variant_sets.GetVariantSelection(n) for n in variant_sets.GetNames()})}")

    print(f"\n== Prim 树（前 {args.depth} 层，每层最多列 6 个）==")
    print_tree(stage.GetPseudoRoot(), 0, args.depth)

    print("\n== 类型统计 ==")
    plain = Counter(p.GetTypeName() or "-" for p in stage.Traverse())
    proxies = Counter(p.GetTypeName() or "-" for p in stage.Traverse(Usd.TraverseInstanceProxies()))
    print(f"默认遍历（不进入实例内部）: 共 {sum(plain.values())} 个 Prim，{plain.most_common(5)}")
    print(f"含实例内部               : 共 {sum(proxies.values())} 个 Prim，{proxies.most_common(5)}")

    print("\n== 关节 Prim ==")
    print_properties(stage.GetPrimAtPath(args.joint))
    print("\n== 网格 Prim ==")
    print_properties(stage.GetPrimAtPath(args.mesh))

    # 没有写元数据时 USD 的默认值（与 Isaac Sim 的米、Z 向上不同）
    empty = Usd.Stage.CreateInMemory()
    print("\n== 空 Stage 的默认值 ==")
    print(f"upAxis        : {UsdGeom.GetStageUpAxis(empty)}")
    print(f"metersPerUnit : {UsdGeom.GetStageMetersPerUnit(empty)}")


if __name__ == "__main__":
    main()
    # Kit 退出时不会刷新 Python 的 stdout 缓冲；不先刷新，输出重定向到文件或管道时会丢失（CONVENTIONS 第 5 节）
    sys.stdout.flush()
    if simulation_app is not None:
        simulation_app.close()
