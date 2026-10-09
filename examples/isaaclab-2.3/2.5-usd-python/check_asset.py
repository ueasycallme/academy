# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：usd-core 26.08；Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04（Isaac Sim 方式运行时）
"""机器人资产的静态检查清单（2.5）：在送进仿真之前，先用 pxr 查一遍常见问题。

每项给出 通过 / 注意 / 失败；在 usd-core 环境下，有"失败"时退出码为 1，可以放进 CI（Isaac Sim 环境下退出码总是 0）。两种运行方式同 2.2 的 inspect_usd.py::

    python check_asset.py [path/to/robot.usda]
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_USD = REPO_ROOT / "third_party/galbot_one_golf_description/usd/galbot_one_golf.usda"

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("usd", nargs="?", default=str(DEFAULT_USD), help="要检查的机器人 USD")
args = parser.parse_args()

simulation_app = None
try:
    from pxr import Sdf, Usd, UsdGeom, UsdPhysics, UsdUtils
except ImportError:
    from isaacsim import SimulationApp

    simulation_app = SimulationApp({"headless": True})
    from pxr import Sdf, Usd, UsdGeom, UsdPhysics, UsdUtils

results: list[tuple[str, str, str]] = []


def report(level: str, item: str, detail: str) -> None:
    results.append((level, item, detail))
    print(f"[{level}] {item}：{detail}")


def check(path: str) -> None:
    # 1. 依赖文件都能找到（引用、载荷、sublayer、贴图）
    #    .mdl 材质（如 OmniPBR.mdl）按 Kit 的 MDL 搜索路径解析，纯 usd-core 下找不到，只记"注意"
    _, _, unresolved = UsdUtils.ComputeAllDependencies(Sdf.AssetPath(path))
    builtin_mdl = [u for u in unresolved if u.endswith(".mdl")]
    missing = [u for u in unresolved if u not in builtin_mdl]
    report("通过" if not missing else "失败", "依赖文件", f"找不到 {len(missing)} 个 {missing[:3]}")
    if builtin_mdl:
        report("注意", "MDL 材质", f"{builtin_mdl}：按 Kit 的 MDL 搜索路径解析，到 Isaac Sim 里确认")

    stage = Usd.Stage.Open(path)
    # 2. 合成错误：如引用的文件找到了，里面却没有指向的 Prim（2.3）。可能无害（6.1.2 的 head_link1），要人工判断
    #    逐个 Prim 收集合成错误（含实例原型内部）；较新的 USD 有 stage.GetCompositionErrors()，Isaac Sim 5.1 自带的 USD 没有
    errors = []
    for top in [stage.GetPseudoRoot(), *stage.GetPrototypes()]:
        for p in Usd.PrimRange(top, Usd.PrimAllPrimsPredicate):
            errors += [str(e) for e in p.GetPrimIndex().localErrors]
    report("通过" if not errors else "注意", "合成错误", f"{len(errors)} 个" + (f"，第一个：{errors[0]}" if errors else ""))

    # 3. defaultPrim：没有它，被引用时拿到的是空的（2.2 坑二）
    root = stage.GetDefaultPrim()
    report("通过" if root else "失败", "defaultPrim", str(root.GetPath()) if root else "未设置")

    # 4. 单位与朝向：Isaac Sim 用米、Z 向上（2.2）
    up, mpu = UsdGeom.GetStageUpAxis(stage), UsdGeom.GetStageMetersPerUnit(stage)
    report("通过" if (up, mpu) == ("Z", 1.0) else "注意", "单位与朝向", f"upAxis {up}，metersPerUnit {mpu}")

    prims = list(stage.Traverse(Usd.TraverseInstanceProxies()))  # 要进入实例内部（2.5 坑一）
    by_path = {p.GetPath(): p for p in prims}

    # 5. Articulation 根恰好一个（2.4）
    roots = [p for p in prims if p.HasAPI(UsdPhysics.ArticulationRootAPI)]
    report("通过" if len(roots) == 1 else "失败", "Articulation 根", f"{len(roots)} 个 {[str(p.GetPath()) for p in roots[:3]]}")

    # 6. 没有嵌套刚体（2.4）
    bodies = [p for p in prims if p.HasAPI(UsdPhysics.RigidBodyAPI)]
    body_paths = {p.GetPath() for p in bodies}
    nested = [p for p in bodies if any(a in body_paths for a in p.GetPath().GetAncestorsRange() if a != p.GetPath())]
    report("通过" if not nested else "失败", "嵌套刚体", f"刚体 {len(bodies)} 个，其中嵌套 {len(nested)} 个")

    # 7. 关节两端的 body 都存在
    joints = [p for p in prims if p.IsA(UsdPhysics.Joint)]
    dangling = []
    for p in joints:
        j = UsdPhysics.Joint(p)
        for rel in (j.GetBody0Rel(), j.GetBody1Rel()):
            dangling += [f"{p.GetName()} → {t}" for t in rel.GetTargets() if t not in by_path]
    report("通过" if not dangling else "失败", "关节连接", f"关节 {len(joints)} 个，指向不存在的 body {len(dangling)} 处 {dangling[:2]}")

    # 8. 关节限位：下限不大于上限
    bad_limits = [p.GetName() for p in prims if p.IsA(UsdPhysics.RevoluteJoint)
                  and (lo := UsdPhysics.RevoluteJoint(p).GetLowerLimitAttr().Get()) is not None
                  and (hi := UsdPhysics.RevoluteJoint(p).GetUpperLimitAttr().Get()) is not None and lo > hi]
    report("通过" if not bad_limits else "失败", "关节限位", f"下限大于上限 {len(bad_limits)} 个 {bad_limits[:3]}")

    # 9. 质量：没写 mass 的刚体由 PhysX 按碰撞体与密度估算，可能和真机差很多（6.1.4）
    no_mass = [p.GetName() for p in bodies if not (p.HasAPI(UsdPhysics.MassAPI) and (UsdPhysics.MassAPI(p).GetMassAttr().Get() or 0) > 0)]
    report("通过" if not no_mass else "注意", "质量", f"未写质量的刚体 {len(no_mass)} 个 {no_mass[:3]}")

    # 10. 被关掉的碰撞体（2.4）
    colliders = [p for p in prims if p.HasAPI(UsdPhysics.CollisionAPI)]
    disabled = [p.GetName() for p in colliders if UsdPhysics.CollisionAPI(p).GetCollisionEnabledAttr().Get() is False]
    report("通过" if not disabled else "注意", "碰撞体", f"共 {len(colliders)} 个，被关闭 {len(disabled)} 个 {disabled[:3]}")

    # 11. 没有驱动的关节：在 Isaac Lab 里通常由执行器配置补上增益（4.7、6.1.5）
    #     mimic 跟随关节与被动关节（如全向轮的滚子）本来就不需要驱动，所以只归类列出，供人工确认
    def kind(p: Usd.Prim) -> str:
        if any(a.GetName().startswith("physxMimicJoint:") for a in p.GetAttributes()):
            return "mimic 跟随"
        return re.sub(r"\d+", "#", p.GetName())

    no_drive = Counter(kind(p) for p in joints if not p.IsA(UsdPhysics.FixedJoint)
                       and not any(s.startswith("PhysicsDriveAPI") for s in p.GetAppliedSchemas()))
    report("通过" if not no_drive else "注意", "关节驱动",
           f"非固定关节中没有 DriveAPI 的 {sum(no_drive.values())} 个，按名字归类：{dict(no_drive.most_common(4))}")


if __name__ == "__main__":
    check(args.usd)
    n_fail = sum(1 for level, _, _ in results if level == "失败")
    n_warn = sum(1 for level, _, _ in results if level == "注意")
    print(f"\n共 {len(results)} 项：失败 {n_fail}，注意 {n_warn}")
    if simulation_app is not None:
        # Isaac Sim 5.1 实测：close() 直接以退出码 0 结束进程，未捕获的异常也不改变退出码，所以 CI 请用 usd-core 环境跑本脚本
        print("（Isaac Sim 环境下进程退出码总是 0，请看上面的统计行）")
        sys.stdout.flush()  # Kit 退出时不会刷新 stdout 缓冲（CONVENTIONS 第 5 节）
        simulation_app.close()
    sys.exit(1 if n_fail else 0)
