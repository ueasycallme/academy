# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""测量 Isaac Lab 自带任务在不同 num_envs 下的显存峰值与仿真吞吐。

用随机动作驱动环境，不训练策略。结果以一行 JSON 打印到标准输出，便于汇总成表。

显存取整卡读数（``nvidia-smi --query-gpu=memory.used``）：Isaac Sim 的 PhysX 与渲染显存
不经过 PyTorch 的分配器，``torch.cuda.max_memory_allocated`` 看不到这部分。因此测量前
请关闭其他占用 GPU 的程序；脚本同时记录启动前的基线读数。
"""

from __future__ import annotations

import argparse
import subprocess
import threading
import time

from isaaclab.app import AppLauncher


def gpu_used_mib() -> int:
    """读取整卡已用显存（MiB）。"""
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=True,
    )
    return int(out.stdout.strip().splitlines()[0])


class PeakSampler(threading.Thread):
    """后台每 0.2 秒采样一次整卡显存，记录峰值。"""

    def __init__(self, interval: float = 0.2):
        super().__init__(daemon=True)
        self.interval = interval
        self.peak = 0
        self._stop = threading.Event()

    def run(self) -> None:
        while not self._stop.is_set():
            self.peak = max(self.peak, gpu_used_mib())
            time.sleep(self.interval)

    def stop(self) -> None:
        self._stop.set()


parser = argparse.ArgumentParser(description="Measure VRAM and throughput of an Isaac Lab task.")
parser.add_argument("--task", type=str, default="Isaac-Reach-Franka-v0", help="Gym task id.")
parser.add_argument("--num_envs", type=int, default=256, help="Number of parallel environments.")
parser.add_argument("--warmup", type=int, default=50, help="RL steps before timing starts.")
parser.add_argument("--steps", type=int, default=500, help="Timed RL steps.")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

baseline = gpu_used_mib()
sampler = PeakSampler()
sampler.start()

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

# 以下导入依赖已启动的 Kit 应用
import gymnasium as gym  # noqa: E402
import json  # noqa: E402
import torch  # noqa: E402

import isaaclab_tasks  # noqa: E402, F401
from isaaclab_tasks.utils import parse_env_cfg  # noqa: E402


def main() -> None:
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    env = gym.make(args.task, cfg=env_cfg)
    env.reset()
    action_shape = env.action_space.shape
    device = env.unwrapped.device

    def random_actions() -> torch.Tensor:
        return 2.0 * torch.rand(action_shape, device=device) - 1.0

    with torch.inference_mode():
        for _ in range(args.warmup):
            env.step(random_actions())
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(args.steps):
            env.step(random_actions())
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - t0

    after_steps = gpu_used_mib()
    sampler.stop()
    result = {
        "task": args.task,
        "num_envs": args.num_envs,
        "headless": bool(args.headless),
        "steps": args.steps,
        "step_dt_s": env.unwrapped.step_dt,
        "rl_steps_per_s": round(args.steps / elapsed, 1),
        "env_steps_per_s": round(args.steps * args.num_envs / elapsed),
        "baseline_mib": baseline,
        "peak_mib": max(sampler.peak, after_steps),
        "peak_minus_baseline_mib": max(sampler.peak, after_steps) - baseline,
        "torch_max_allocated_mib": round(torch.cuda.max_memory_allocated() / 2**20),
    }
    print("RESULT " + json.dumps(result), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
