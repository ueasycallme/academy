# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab 3.0.0（v3.0.0 tag，commit e3f7d9ff1），不装 Isaac Sim（1.5 路线 C + ov[ovrtx]，ovrtx 0.5.1）
# 验证日期：2026-10-23
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04
"""用 OVRTX 渲染器从 tiled camera 取一帧（8.8）。不需要 Isaac Sim。

建 Isaac-Cartpole-Camera-Direct（每个环境一台 96×96 相机），选 renderer=ovrtx，用零动作推进 --steps 步，
记录每步耗时（含渲染）与 torch 显存，把第一个环境最后一帧的 RGB 存成 PNG，并把前 16 个环境拼成 4×4 的图。

    python ovrtx_frame.py --num_envs 64 --steps 50 --out ovrtx_cartpole.png physics=newton_mjwarp renderer=ovrtx
"""

import argparse
import time

import gymnasium as gym
import numpy as np
import torch

from isaaclab.app import add_launcher_args, launch_simulation

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import resolve_task_config, setup_preset_cli

parser = argparse.ArgumentParser(description="OVRTX tiled camera 出一帧（8.8）")
parser.add_argument("--task", default="Isaac-Cartpole-Camera-Direct")
parser.add_argument("--num_envs", type=int, default=64)
parser.add_argument("--steps", type=int, default=50)
parser.add_argument("--warmup", type=int, default=10, help="前若干步不计时（第一次渲染包含初始化）")
parser.add_argument("--out", default="ovrtx_cartpole.png")
add_launcher_args(parser)
args_cli, hydra_args = setup_preset_cli(parser)


def save_png(img: np.ndarray, path: str) -> None:
    from PIL import Image

    Image.fromarray(img).save(path)


def main() -> None:
    env_cfg, _ = resolve_task_config(args_cli.task, "", overrides=hydra_args)
    env_cfg.scene.num_envs = args_cli.num_envs
    with launch_simulation(env_cfg, args_cli):
        env = gym.make(args_cli.task, cfg=env_cfg)
        env.reset()
        base = env.unwrapped
        cam = base.scene.sensors["tiled_camera"]
        print(f"[8.8] 相机 {cam.cfg.width}×{cam.cfg.height}，{args_cli.num_envs} 台；数据类型 {cam.cfg.data_types}", flush=True)
        actions = torch.zeros(env.action_space.shape, device=base.device)
        times = []
        with torch.inference_mode():
            for k in range(args_cli.warmup + args_cli.steps):
                torch.cuda.synchronize()
                t0 = time.perf_counter()
                env.step(actions)
                rgb = cam.data.output["rgb"]
                torch.cuda.synchronize()
                if k >= args_cli.warmup:
                    times.append((time.perf_counter() - t0) * 1000)
        frames = rgb[:, :, :, :3].float().clamp(0, 255).to(torch.uint8).cpu().numpy()  # (环境, 高, 宽, 3)
        n = min(16, frames.shape[0])
        side = int(np.sqrt(n))
        grid = np.concatenate([np.concatenate(list(frames[r * side : (r + 1) * side]), axis=1) for r in range(side)], axis=0)
        save_png(frames[0], args_cli.out)
        save_png(grid, args_cli.out.replace(".png", f"_grid{side}x{side}.png"))
        t = np.array(times)
        print(f"[8.8] 输出 {tuple(rgb.shape)}，dtype {rgb.dtype}，像素均值 {frames.mean():.1f}（全 0 即黑帧）", flush=True)
        print(f"[8.8] 每步（含物理 {env_cfg.decimation} 步与一次渲染）中位 {np.median(t):.2f} ms、最小 {t.min():.2f}、最大 {t.max():.2f} ms"
              f"（{len(t)} 步，前 {args_cli.warmup} 步不计）；torch 显存峰值 {torch.cuda.max_memory_allocated() / 2**20:.0f} MiB", flush=True)
        print(f"[8.8] 已存 {args_cli.out} 与 4×4 拼图", flush=True)
        env.close()


if __name__ == "__main__":
    main()
