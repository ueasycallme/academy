# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip，omni.replicator.core 1.12.27）；不用 Isaac Lab
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""用 Replicator 在 Galbot 的桌面场景里生成带标注的合成图像（3.9）。

四步各在一处：随机化（rep.trigger.on_frame 里的 modify / randomizer）→ 渲染（render_product + orchestrator.step）
→ 标注（BasicWriter 打开的 rgb、semantic_segmentation、bounding_box_2d_tight 三个标注器）→ 写盘（BasicWriter）。

场景：6.2.1 那张桌子（--robot 时再放 Galbot 的 USD）、3 个 5 cm 方块，一台在桌角斜上方的相机（没有用腕部相机：那需要跟随手臂运动，本页只做独立脚本）。方块用 USD 属性打标签（UsdSemantics.LabelsAPI），桌子用 rep.modify.semantics。

    python synth_data.py --frames 200 --out /tmp/synth
    python synth_data.py --frames 5 --out /tmp/nolabel --no_labels    # 缺标签时的输出
"""

import argparse
import json
import os
import subprocess
import sys
import time

parser = argparse.ArgumentParser(description="Replicator 合成数据（3.9）")
parser.add_argument("--frames", type=int, default=200)
parser.add_argument("--out", required=True)
parser.add_argument("--width", type=int, default=640)
parser.add_argument("--height", type=int, default=480)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--no_labels", action="store_true", help="不打语义标签，看分割与框是否为空")
parser.add_argument("--robot", action="store_true", help="场景里放 Galbot。只是一个 USD，没有 Isaac Lab 的默认关节姿态，停在零位（腿在下限，6.1.5），会矮在桌下")
parser.add_argument("--run_async", action="store_true", help="用 orchestrator.run() 而不是逐帧 step()，且不等写完就退出（坑二）")
parser.add_argument("--mode", choices=["run", "step"], default="run", help="run：run_until_complete(num_frames)；step：逐帧 step()")
parser.add_argument("--gui", action="store_true", help="开窗口（默认 headless）")
parser.add_argument("--launcher", choices=["simapp", "lab", "lab_orch_on"], default="simapp",
                    help="simapp：Isaac Sim 的 SimulationApp（默认）；lab：Isaac Lab 的 AppLauncher（坑一的对照）；"
                         "lab_orch_on：AppLauncher，但把 Replicator 的 orchestrator 重新打开")
args = parser.parse_args()
if args.launcher == "simapp":
    # 默认用 Isaac Sim 自己的 SimulationApp。Isaac Lab 的渲染体验文件把 Replicator 的 orchestrator 关了
    # （isaaclab.python.headless.rendering.kit L100–L101），帧数就控制不住（坑一）
    from isaacsim import SimulationApp

    simulation_app = SimulationApp({"headless": not args.gui})
else:
    from isaaclab.app import AppLauncher

    kit_args = "--/exts/omni.replicator.core/Orchestrator/enabled=true" if args.launcher == "lab_orch_on" else ""
    simulation_app = AppLauncher(headless=not args.gui, enable_cameras=True, kit_args=kit_args).app

import omni.replicator.core as rep  # noqa: E402
import omni.usd  # noqa: E402
from isaacsim.core.utils.semantics import add_labels  # noqa: E402

TABLE_POS, TABLE_SIZE = (0.65, -0.25, 0.93), (0.6, 1.0, 0.04)  # 与 6.2.1 的桌子相同：中心与尺寸（m）
CUBE = 0.05
CUBE_Z = TABLE_POS[2] + TABLE_SIZE[2] / 2 + CUBE / 2


def proc_vram_mib() -> int:
    out = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True).stdout
    return sum(int(m) for p, m in (line.split(", ") for line in out.strip().splitlines()) if int(p) == os.getpid())


def build_scene():
    omni.usd.get_context().new_stage()
    rep.set_global_seed(args.seed)
    rep.create.plane(scale=10, visible=True)
    if args.robot:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "6-galbot-project", "source", "galbot_academy"))
        from galbot_academy.assets.paths import generated_asset_dir

        rep.create.from_usd(str(generated_asset_dir() / "galbot_fixed_base" / "galbot.usd"))  # 不打标签：分割里算背景
    table = rep.create.cube(position=TABLE_POS, scale=TABLE_SIZE)
    cubes = rep.create.cube(count=3, scale=CUBE, position=(0.6, -0.25, CUBE_Z))
    light = rep.create.light(light_type="Dome", intensity=1000)
    if not args.no_labels:
        # 方式一：直接写 USD 属性（UsdSemantics.LabelsAPI），任何能改 USD 的代码都能做
        for prim in cubes.get_output_prims()["prims"]:  # Usd.Prim（Replicator 建的 Xform，标签对子网格同样有效）
            add_labels(prim, ["cube"], instance_name="class")
        # 方式二：Replicator 的 modify.semantics
        with table:
            rep.modify.semantics([("class", "table")])
    # 桌角斜上方较远处，用长焦拉近，桌面占满画面
    camera = rep.create.camera(position=(1.8, -1.8, 2.4), look_at=(0.65, -0.25, CUBE_Z), focal_length=60.0)
    return cubes, light, camera


def main() -> None:
    cubes, light, camera = build_scene()
    # 只在请求的帧采集，不随时间线播放采集（官方示例同样关掉 capture-on-play）。
    # 要在 new_stage() 之后设：换 stage 会重置 Replicator，这个开关回到持久化设置里的值
    rep.orchestrator.set_capture_on_play(False)
    # 随机化：每帧触发一次。方块位置与朝向、颜色，环境光强度
    with rep.trigger.on_frame(max_execs=args.frames):  # 上限：最多随机化这么多次
        with cubes:
            rep.modify.pose(
                position=rep.distribution.uniform((0.45, -0.45, CUBE_Z), (0.85, -0.05, CUBE_Z)),
                rotation=rep.distribution.uniform((0, 0, -180), (0, 0, 180)),
            )
            rep.randomizer.color(colors=rep.distribution.uniform((0.1, 0.1, 0.1), (1.0, 1.0, 1.0)))
        with light:
            rep.modify.attribute("inputs:intensity", rep.distribution.uniform(300.0, 2000.0))
    # 渲染产品 + 写入器（写入器按参数打开对应的标注器）
    render_product = rep.create.render_product(camera, (args.width, args.height))
    writer = rep.WriterRegistry.get("BasicWriter")
    writer.initialize(output_dir=args.out, rgb=True, semantic_segmentation=True, bounding_box_2d_tight=True,
                      colorize_semantic_segmentation=True)
    writer.attach([render_product])

    t0 = time.perf_counter()
    if args.run_async:
        rep.orchestrator.run(num_frames=args.frames)  # 异步：立即返回
        print(f"[3.9] run() 返回用了 {time.perf_counter() - t0:.2f} s，不等写完就退出", flush=True)
        return
    if args.mode == "run":
        rep.orchestrator.run_until_complete(num_frames=args.frames)  # 生成 frames 帧后返回
        writer.detach()
        render_product.destroy()
        rep.orchestrator.wait_until_complete()
        total = time.perf_counter() - t0
        print(f"[3.9] run_until_complete：{args.frames} 帧，{args.width}×{args.height}，总计 {total:.1f} s，"
              f"平均每帧 {total / args.frames * 1000:.0f} ms；按进程显存 {proc_vram_mib()} MiB", flush=True)
        summarize(args.out)
        return
    per = []
    for _ in range(args.frames):
        t = time.perf_counter()
        rep.orchestrator.step()  # 同步：随机化 → 渲染 → 把这一帧交给标注器与写入器
        per.append(time.perf_counter() - t)
    writer.detach()  # 先断开写入器与渲染产品，再等后台写盘结束（顺序同官方示例）
    render_product.destroy()
    rep.orchestrator.wait_until_complete()
    total = time.perf_counter() - t0
    per.sort()
    print(f"[3.9] {args.frames} 帧，{args.width}×{args.height}：每帧 step 中位 {per[len(per) // 2] * 1000:.1f} ms"
          f"（首帧 {max(per) * 1000:.0f} ms），总计 {total:.1f} s；按进程显存 {proc_vram_mib()} MiB", flush=True)
    summarize(args.out)


def summarize(out: str) -> None:
    files = sorted(os.listdir(out))
    kinds = {}
    for f in files:
        kind = f.rsplit("_", 1)[0]
        kinds[kind] = kinds.get(kind, 0) + 1
    size = sum(os.path.getsize(os.path.join(out, f)) for f in files)
    print(f"[3.9] 输出 {len(files)} 个文件、{size / 2**20:.1f} MiB：" + "，".join(f"{k} ×{n}" for k, n in kinds.items()), flush=True)
    import numpy as np

    boxes = np.load(os.path.join(out, "bounding_box_2d_tight_0000.npy"))
    labels = json.load(open(os.path.join(out, "bounding_box_2d_tight_labels_0000.json")))
    seg_labels = json.load(open(os.path.join(out, "semantic_segmentation_labels_0000.json")))
    print(f"[3.9] 第 0 帧：2D 框 {len(boxes)} 个，字段 {boxes.dtype.names}；框标签 {labels}；分割标签 {seg_labels}", flush=True)


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
