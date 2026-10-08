# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""用同一个相机渲染两张图：视觉网格、碰撞体，便于对比（6.1.4）。

转换得到的 USD 里，碰撞体放在各连杆的 collisions 下，是实例化的，purpose 为 guide，普通渲染看不到。
脚本在一个新的覆盖层里：取消 collisions / visuals 的实例化，把碰撞体改为 default purpose、隐藏视觉网格（另一张图反之），
然后渲染。原始 USD 不被修改。

用法（项目根目录）::

    python scripts/render_collisions.py --headless --enable_cameras
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="渲染视觉网格与碰撞体")
parser.add_argument("--variant", default="fixed_base")
parser.add_argument("--out", default="generated/render", help="输出目录")
parser.add_argument("--size", type=int, nargs=2, default=[960, 720], help="图像宽、高")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

from pathlib import Path

import numpy as np
import omni.replicator.core as rep
import omni.usd
from PIL import Image
from pxr import Gf, Sdf, Usd, UsdGeom, UsdLux, UsdShade

from galbot_academy.assets import generated_asset_dir


def build_stage(show: str) -> None:
    """新建舞台，引用机器人；show 为 "visuals" 或 "collisions"。"""
    omni.usd.get_context().new_stage()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    robot = stage.DefinePrim("/Robot", "Xform")
    robot.GetReferences().AddReference(str(generated_asset_dir() / f"galbot_{args.variant}" / "galbot.usd"))
    UsdLux.DomeLight.Define(stage, "/Dome").CreateIntensityAttr(900.0)
    for prim in list(Usd.PrimRange(robot)):
        if prim.GetName() in ("visuals", "collisions"):
            prim.SetInstanceable(False)  # 取消实例化后才能修改内部 Prim
    for prim in Usd.PrimRange(robot):
        name = prim.GetName()
        if name == "visuals":
            UsdGeom.Imageable(prim).GetVisibilityAttr().Set("inherited" if show == "visuals" else "invisible")
        elif name == "collisions":
            UsdGeom.Imageable(prim).GetVisibilityAttr().Set("inherited" if show == "collisions" else "invisible")
        elif prim.HasAttribute("purpose") and prim.GetAttribute("purpose").Get() == "guide":
            prim.GetAttribute("purpose").Set("default")  # 碰撞体原为 guide
    # 碰撞体涂成橙色：只设 displayColor 不够，网格继承了视觉材质的绑定，所以绑定一个更强的橙色材质
    mat = UsdShade.Material.Define(stage, "/Looks/Collision")
    shader = UsdShade.Shader.Define(stage, "/Looks/Collision/Shader")
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.95, 0.45, 0.1))
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.6)
    mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    for prim in Usd.PrimRange(robot):
        if prim.GetName() == "collisions":
            UsdShade.MaterialBindingAPI.Apply(prim).Bind(mat, UsdShade.Tokens.strongerThanDescendants)
    cam = UsdGeom.Camera.Define(stage, "/Cam")
    xf = UsdGeom.Xformable(cam.GetPrim())
    # 从机器人右前上方看向上半身（相机看向自身 -Z）
    xf.AddTransformOp().Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(2.1, -1.5, 1.5), Gf.Vec3d(0.0, 0.0, 0.7), Gf.Vec3d(0, 0, 1)).GetInverse())
    cam.CreateFocalLengthAttr(18.0)


def render(show: str, path: Path) -> None:
    build_stage(show)
    rp = rep.create.render_product("/Cam", tuple(args.size))
    rgb = rep.AnnotatorRegistry.get_annotator("rgb")
    rgb.attach([rp])
    for _ in range(60):  # 不用 rep.orchestrator.step()（本站实测在此卡住）；直接推进应用，让渲染收敛
        simulation_app.update()
    Image.fromarray(np.asarray(rgb.get_data())[..., :3]).save(path)
    rgb.detach()
    rp.destroy()
    print(f"已保存 {path}")


def main() -> None:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    render("visuals", out / "galbot_visuals.png")
    render("collisions", out / "galbot_collisions.png")


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
