# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：usd-core 26.08（不需要 Isaac Sim）；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
"""打印 Galbot 厂商 USD 的合成结构（2.3）：默认 Prim 上的合成弧、变体集、载荷加载与否的差别、用到的 Layer。

    python inspect_galbot_layers.py <galbot 描述仓库>/usd/galbot_one_golf.usda
"""

import sys
from pathlib import Path

from pxr import Usd, UsdPhysics


def main(path: str) -> None:
    root_dir = Path(path).resolve().parent
    short = lambda lyr: str(Path(lyr.realPath).resolve().relative_to(root_dir)) if lyr.realPath else lyr.identifier

    stage = Usd.Stage.Open(path)
    prim = stage.GetDefaultPrim()
    print(f"默认 Prim：{prim.GetPath()}")

    print("\n默认 Prim 上的合成弧（由强到弱）：")
    for arc in Usd.PrimCompositionQuery(prim).GetCompositionArcs():
        kind = str(arc.GetArcType()).split(".")[-1].replace("PcpArcType", "").replace("ArcType", "")
        layer = arc.GetTargetNode().layerStack.identifier.rootLayer
        print(f"  {kind:12s} → {short(layer)}")

    print("\n变体集（当前选择 / 可选项）：")
    vsets = prim.GetVariantSets()
    for name in vsets.GetNames():
        vs = vsets.GetVariantSet(name)
        print(f"  {name:8s} 选 {vs.GetVariantSelection():8s}  可选 {vs.GetVariantNames()}")

    def stats(st: Usd.Stage) -> str:
        prims = list(st.Traverse(Usd.TraverseInstanceProxies()))
        bodies = sum(1 for p in prims if p.HasAPI(UsdPhysics.RigidBodyAPI))
        joints = sum(1 for p in prims if p.IsA(UsdPhysics.Joint))
        return f"Prim {len(prims)} 个，刚体 {bodies}，关节 {joints}，用到的 Layer {len(st.GetUsedLayers())} 个"

    print("\n载荷：")
    print(f"  全部加载（默认）：{stats(stage)}")
    print(f"  不加载载荷（LoadNone）：{stats(Usd.Stage.Open(path, Usd.Stage.LoadNone))}")

    print("\n在 Session Layer 里把变体 Physics 切到 none：")
    stage.SetEditTarget(stage.GetSessionLayer())  # 改动只写进 Session Layer，不碰磁盘上的文件，也不改根 Layer
    vsets.GetVariantSet("Physics").SetVariantSelection("none")
    print(f"  {stats(stage)}")
    print(f"  根 Layer 里的选择仍是：{stage.GetRootLayer().GetPrimAtPath(prim.GetPath()).variantSelections['Physics']}；"
          f"Session Layer 里是：{stage.GetSessionLayer().GetPrimAtPath(prim.GetPath()).variantSelections['Physics']}")
    stage.GetSessionLayer().Clear()

    print("\n清空 Session Layer 后，用到的 Layer（Physics = physx）：")
    for lyr in sorted(stage.GetUsedLayers(), key=lambda l: l.identifier):
        if lyr.realPath:
            print(f"  {short(lyr)}")


if __name__ == "__main__":
    main(sys.argv[1])
