# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""渲染的代价（3.8）：同一个 Galbot 桌面场景、同一视角，比较三种情况下每个物理步的墙上时间与按进程显存。

- none：不建相机、不渲染（训练纯状态策略时就是这样）；
- rt：一台 640×480 相机，RTX 实时模式（本机默认的 /rtx/rendermode）；
- pt：同一台相机，切到路径追踪（/rtx/rendermode = PathTracing），每帧 1 个采样。

另外读出：机器人身上的材质是哪种着色器（URDF 转来的材质长什么样），以及第 1 帧与最后一帧的平均亮度（headless 下第一帧是不是黑的）。

    python scripts/render_cost.py --headless --mode none
    python scripts/render_cost.py --headless --enable_cameras --mode rt --save rt.png
    python scripts/render_cost.py --headless --enable_cameras --mode pt --save pt.png
"""

import argparse
import os
import subprocess
import sys
import time

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="渲染的代价（3.8）")
parser.add_argument("--mode", choices=["none", "rt", "pt"], default="none")
parser.add_argument("--steps", type=int, default=120, help="计时的物理步数（之前另有 30 步热身）")
parser.add_argument("--spp", type=int, default=1, help="路径追踪每帧每像素采样数（/rtx/pathtracing/spp）")
parser.add_argument("--save", default=None, help="把最后一帧 RGB 存成 PNG")
parser.add_argument("--broken_mdl", action="store_true", help="桌上放一个方块，材质指向不存在的 MDL 文件（看缺材质时画面什么样）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
if args.mode != "none" and not args.enable_cameras:
    sys.exit("rt / pt 需要 --enable_cameras")
simulation_app = AppLauncher(args).app

import carb  # noqa: E402
import torch  # noqa: E402

import isaaclab.sim as sim_utils  # noqa: E402
from isaaclab.scene import InteractiveScene  # noqa: E402
from isaaclab.sensors import CameraCfg  # noqa: E402
from isaaclab.utils import configclass  # noqa: E402

from galbot_academy.scenes.reach import TABLE_CENTER_XY, TABLE_TOP_Z, GalbotReachTableSceneCfg  # noqa: E402

DT = 1.0 / 120.0


@configclass
class SceneCfg(GalbotReachTableSceneCfg):
    camera: CameraCfg | None = None


def proc_vram_mib() -> int:
    out = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True).stdout
    return sum(int(m) for p, m in (line.split(", ") for line in out.strip().splitlines()) if int(p) == os.getpid())


def material_summary(stage, root: str) -> str:
    """机器人身上绑定的材质：数一数各种着色器（MDL 文件或 UsdPreviewSurface）各有几个。"""
    from pxr import Usd, UsdShade

    kinds = {}
    for prim in stage.Traverse(Usd.TraverseInstanceProxies()):  # 视觉网格在实例里，普通 Traverse 进不去
        if not prim.GetPath().pathString.startswith(root) or not prim.IsA(UsdShade.Shader):
            continue
        shader = UsdShade.Shader(prim)
        src = shader.GetSourceAsset("mdl")
        kind = os.path.basename(src.path) if src else (shader.GetIdAttr().Get() or "?")
        kinds[kind] = kinds.get(kind, 0) + 1
    return "，".join(f"{k} ×{n}" for k, n in sorted(kinds.items(), key=lambda x: -x[1])) or "无"


def main() -> None:
    settings = carb.settings.get_settings()
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=DT, device=args.device))
    cfg = SceneCfg(num_envs=1, env_spacing=2.5)
    if args.mode != "none":
        cfg.camera = CameraCfg(
            prim_path="{ENV_REGEX_NS}/ViewCam",
            data_types=["rgb"],
            spawn=sim_utils.PinholeCameraCfg(focal_length=18.0, clipping_range=(0.05, 20.0)),
            width=640,
            height=480,
        )
    scene = InteractiveScene(cfg)
    if args.broken_mdl:
        cube = sim_utils.CuboidCfg(size=(0.15, 0.15, 0.15), visual_material=sim_utils.MdlFileCfg(mdl_path="does_not_exist.mdl"))
        cube.func("/World/BrokenMdlCube", cube, translation=(TABLE_CENTER_XY[0], TABLE_CENTER_XY[1], TABLE_TOP_Z + 0.075))
    if args.mode == "pt":
        settings.set_string("/rtx/rendermode", "PathTracing")
        settings.set_int("/rtx/pathtracing/spp", args.spp)
        settings.set_int("/rtx/pathtracing/totalSpp", args.spp)  # 不累积：每帧都是 spp 个采样的结果
    sim.reset()
    robot = scene["robot"]  # 写入默认关节姿态，否则机器人停在 USD 零位（6.1.5）
    robot.write_joint_state_to_sim(robot.data.default_joint_pos, robot.data.default_joint_vel)
    robot.set_joint_position_target(robot.data.default_joint_pos)
    print(f"[3.8] /rtx/rendermode = {settings.get('/rtx/rendermode')}；"
          f"机器人材质：{material_summary(sim.stage, '/World/envs/env_0/Robot')}", flush=True)
    cam = None
    if args.mode != "none":
        cam = scene["camera"]
        # 从桌子对面斜上方看机器人与桌面
        eye = torch.tensor([[TABLE_CENTER_XY[0] + 1.3, TABLE_CENTER_XY[1] - 0.9, TABLE_TOP_Z + 0.75]], device=sim.device)
        target = torch.tensor([[0.2, -0.1, 1.0]], device=sim.device)
        cam.set_world_poses_from_view(eye, target)

    render = args.mode != "none"
    brightness = []

    def step():
        scene.write_data_to_sim()
        sim.step(render=render)
        scene.update(DT)
        if cam is not None:
            return cam.data.output["rgb"]

    rgb = step()
    if cam is not None:
        brightness.append(rgb.float().mean().item())
    for _ in range(29):
        step()
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(args.steps):
        rgb = step()
    torch.cuda.synchronize()
    ms = (time.perf_counter() - t0) / args.steps * 1000
    line = f"[3.8] mode {args.mode}：每个物理步 {ms:.2f} ms（{args.steps} 步，热身 30 步），按进程显存 {proc_vram_mib()} MiB"
    if cam is not None:
        brightness.append(rgb.float().mean().item())
        line += f"；平均亮度 第 1 帧 {brightness[0]:.1f}、最后一帧 {brightness[-1]:.1f}（0–255）"
        if args.save:
            import matplotlib.pyplot as plt

            plt.imsave(args.save, rgb[0].cpu().numpy())
            line += f"；已存 {args.save}"
    print(line, flush=True)
    sim.clear_all_callbacks()
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
