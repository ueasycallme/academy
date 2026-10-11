# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""把录下的 pick-place 示范重放成视频，并拼一张关键帧图（6.4.6）。

scripts/tools/hdf5_to_mp4.py 只转换数据集里存下的相机帧（4.19"数据格式"），本项目录的是状态示范，没有图像。
所以这里换个做法：从示范的初始状态开环重放动作，用视口相机逐步渲染。重放与录制在同一设备上做，结果与录制时一致
（scripts/check_mimic_interface.py 的重放 10 / 10 成功）。

    python scripts/replay_pick_place.py --headless --enable_cameras --demo demo_0 --out_dir ./videos/pick_place
"""

import argparse
import os
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="重放 pick-place 示范并录视频")
parser.add_argument("--dataset_file", default="./datasets/galbot_pick_place.hdf5")
parser.add_argument("--demo", default="demo_0")
parser.add_argument("--out_dir", default="./videos/pick_place")
parser.add_argument("--width", type=int, default=640, help="视频宽度（像素），高按 16:9；1280 在本机 16 GB 内存下被内存保护停掉（6.4.6）")
parser.add_argument("--keyframes", default="60,132,260,420,470,510", help="拼关键帧图用的步号（逗号分隔）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import imageio
import numpy as np
import torch
from PIL import Image

from isaaclab.utils.datasets import HDF5DatasetFileHandler

import galbot_academy.tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

TASK = "Galbot-PickPlace-IK-Rel-v0"


def main() -> None:
    os.makedirs(args.out_dir, exist_ok=True)
    handler = HDF5DatasetFileHandler()
    handler.open(args.dataset_file)
    ep = handler.load_episode(args.demo, args.device)
    env_cfg = parse_env_cfg(TASK, device=args.device, num_envs=1)
    env_cfg.terminations.success = None
    env_cfg.terminations.time_out = None
    env_cfg.viewer.resolution = (args.width, args.width * 9 // 16)
    env = gym.make(TASK, cfg=env_cfg, render_mode="rgb_array").unwrapped
    env.sim.reset()
    env.reset_to(ep.data["initial_state"], None, is_relative=True)
    keys = [int(k) for k in args.keyframes.split(",")]
    frames, picked = [], {}
    with torch.inference_mode():
        for k, a in enumerate(ep.data["actions"]):
            env.step(a[None])
            img = env.render()
            frames.append(img)
            if k in keys:
                picked[k] = img
    path = os.path.join(args.out_dir, f"{args.demo}.mp4")
    imageio.mimsave(path, frames, fps=30)
    print(f"[replay] {args.demo}：{len(frames)} 帧，{frames[0].shape[1]}×{frames[0].shape[0]}，写到 {path}", flush=True)
    # 关键帧：每帧缩到 480 宽，按步号顺序 3 列排开。图上不写字（缩放后字太小），步号写在图注里
    tiles = []
    for k in keys:
        if k not in picked:
            continue
        im = Image.fromarray(picked[k]).resize((480, 270))
        tiles.append(np.asarray(im))
    if tiles:
        cols = 3
        rows = [np.concatenate(tiles[i:i + cols], axis=1) for i in range(0, len(tiles), cols)]
        if len(rows) > 1 and rows[-1].shape[1] < rows[0].shape[1]:
            pad = np.zeros((rows[-1].shape[0], rows[0].shape[1] - rows[-1].shape[1], 3), dtype=np.uint8)
            rows[-1] = np.concatenate([rows[-1], pad], axis=1)
        sheet = os.path.join(args.out_dir, f"{args.demo}_keyframes.jpg")
        Image.fromarray(np.concatenate(rows, axis=0)).save(sheet, quality=85)
        print(f"[replay] 关键帧 {sorted(picked)} 拼图写到 {sheet}", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
