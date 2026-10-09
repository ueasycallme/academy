# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：usd-core 26.08；Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04（Isaac Sim 方式运行时）
"""用 pxr 读、筛选、修改、保存 USD（2.5）。

1. 打开 Galbot 厂商 USD，读元数据，按类型、按名字筛选关节，读关节限位与驱动参数；
2. 新建一个场景文件，引用 Galbot，在场景里改一个关节的刚度、加一个带物理的方块；
3. 比较 Save（只存场景这一层）与 Export（把合成结果压平成一个文件）。

厂商文件全程只读，脚本最后核对它没有被改动。两种运行方式同 2.2 的 inspect_usd.py::

    python edit_usd.py [path/to/robot.usda] [--out 输出目录]
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_USD = REPO_ROOT / "third_party/galbot_one_golf_description/usd/galbot_one_golf.usda"

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("usd", nargs="?", default=str(DEFAULT_USD), help="要读取的机器人 USD（只读）")
parser.add_argument("--out", default=None, help="场景文件的输出目录；不给则用临时目录，结束后删除")
args = parser.parse_args()

# usd-core 环境可以直接导入 pxr；Isaac Sim 的 pip 环境要先启动 SimulationApp
simulation_app = None
try:
    from pxr import Usd, UsdGeom, UsdPhysics
except ImportError:
    from isaacsim import SimulationApp

    simulation_app = SimulationApp({"headless": True})
    from pxr import Usd, UsdGeom, UsdPhysics


def md5(path: str) -> str:
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def read_and_filter(robot_usd: str) -> str:
    t0 = time.perf_counter()
    stage = Usd.Stage.Open(robot_usd)
    print(f"打开用时 {time.perf_counter() - t0:.2f} s；defaultPrim = {stage.GetDefaultPrim().GetPath()}，"
          f"upAxis = {stage.GetMetadata('upAxis')}，metersPerUnit = {stage.GetMetadata('metersPerUnit')}")

    prims = list(stage.Traverse(Usd.TraverseInstanceProxies()))
    revolute = [p for p in prims if p.IsA(UsdPhysics.RevoluteJoint)]  # 按类型筛选
    prismatic = [p for p in prims if p.IsA(UsdPhysics.PrismaticJoint)]
    print(f"按类型：转动关节 {len(revolute)} 个，移动关节 {len(prismatic)} 个")

    arm = [p for p in revolute if re.fullmatch(r"right_arm_joint\d", p.GetName())]  # 按名字筛选
    print(f"按名字 right_arm_joint\\d：{len(arm)} 个")
    for p in arm[:3]:
        joint = UsdPhysics.RevoluteJoint(p)
        drive = UsdPhysics.DriveAPI(p, "angular")  # 多实例 API schema：实例名 angular
        print(f"  {p.GetPath()}  限位 [{joint.GetLowerLimitAttr().Get():.1f}, {joint.GetUpperLimitAttr().Get():.1f}]（度）"
              f"  stiffness {drive.GetStiffnessAttr().Get():.4g}  damping {drive.GetDampingAttr().Get():.4g}")
    # 扩展 Schema：usd-core 不认识 PhysX 的 Schema，GetAppliedSchemas() 里看不到它，属性仍在（本页坑四）
    mimic = next(p for p in revolute if any(a.GetName().startswith("physxMimicJoint:") for a in p.GetAttributes()))
    print(f"mimic 跟随关节 {mimic.GetName()} 的 applied schemas：{list(mimic.GetAppliedSchemas())}")
    return str(arm[0].GetPath().MakeRelativePath(stage.GetDefaultPrim().GetPath()))


def modify_and_save(robot_usd: str, joint_rel: str, out_dir: Path) -> None:
    scene_path = str(out_dir / "scene.usda")
    stage = Usd.Stage.CreateNew(scene_path)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    world = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world.GetPrim())
    print(f"\n编辑目标（EditTarget）：{Path(stage.GetEditTarget().GetLayer().identifier).name}")

    # 1. 引用机器人：机器人的全部内容来自厂商文件，场景里只记下"引用了它"
    #    路径原样写进文件：传绝对路径，场景就不能整体搬走；这里换成相对于 scene.usda 的路径（本页坑三）
    robot = stage.DefinePrim("/World/Robot", "Xform")
    robot.GetReferences().AddReference(os.path.relpath(robot_usd, out_dir))

    # 2. 改一个关节的刚度：意见写在场景这一层，比引用进来的值强（2.3 的 LIVRPS）
    joint = stage.GetPrimAtPath(f"/World/Robot/{joint_rel}")
    drive = UsdPhysics.DriveAPI(joint, "angular")
    before = drive.GetStiffnessAttr().Get()
    drive.GetStiffnessAttr().Set(before * 2)
    print(f"{joint.GetPath()} stiffness：{before:.4g} → {drive.GetStiffnessAttr().Get():.4g}")

    # 3. 加一个 Prim 并应用 API schema：方块 + 刚体 + 碰撞 + 质量
    box = UsdGeom.Cube.Define(stage, "/World/Box")
    box.GetSizeAttr().Set(0.1)
    box.AddTranslateOp().Set((0.5, 0.0, 0.05))
    UsdPhysics.RigidBodyAPI.Apply(box.GetPrim())
    UsdPhysics.CollisionAPI.Apply(box.GetPrim())
    UsdPhysics.MassAPI.Apply(box.GetPrim()).GetMassAttr().Set(2.0)
    print(f"/World/Box 的 applied schemas：{list(box.GetPrim().GetAppliedSchemas())}")

    # 4. Save：只把场景这一层（根 Layer）写回 scene.usda；Export：把合成结果压平成一个独立文件
    stage.Save()
    flat_path = str(out_dir / "flattened.usda")
    stage.Export(flat_path)
    for path in (scene_path, flat_path):
        reopened = Usd.Stage.Open(path)  # 先存进变量，Stage 释放后它的 Prim 就失效了（本页坑三）
        n_prims = len(list(reopened.Traverse(Usd.TraverseInstanceProxies())))
        print(f"{Path(path).name:15s} {Path(path).stat().st_size / 1024:9.1f} KB  合成后 Prim {n_prims} 个")

    print("\nscene.usda 的内容（相当于 usdcat）：")
    print(stage.GetRootLayer().ExportToString().split("\n", 1)[1].strip())


def main() -> None:
    before = md5(args.usd)
    joint_rel = read_and_filter(args.usd)
    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        modify_and_save(args.usd, joint_rel, out_dir)
    else:
        with tempfile.TemporaryDirectory() as d:
            modify_and_save(args.usd, joint_rel, Path(d))
    print(f"\n厂商文件未被改动：{md5(args.usd) == before}")


if __name__ == "__main__":
    main()
    # Kit 退出时不会刷新 Python 的 stdout 缓冲（CONVENTIONS 第 5 节）
    sys.stdout.flush()
    if simulation_app is not None:
        simulation_app.close()
