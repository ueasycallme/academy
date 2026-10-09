# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-09
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""给训练"算账"用的小工具（7.2）：在 Galbot-Reach-v0 上用零动作计时 env.step，并对照三种内存读数。

- 每个环境步（4 个物理步 + 各管理器）的耗时，以及其中 4 个物理步的耗时（直接计 sim.step）；
- torch 的显存统计（memory_allocated / memory_reserved / max_memory_allocated）与 nvidia-smi 按进程显存的差别：
  后者还包括 PhysX、Kit、CUDA 上下文，所以总比前者大得多；
- 本进程的主机 RSS 与整机 MemAvailable。
- --cprofile：用 cProfile 包住计时循环，在 simulation_app.close() 之前把统计写盘并打印前 15 项。
  不能用 python -m cProfile 包整个脚本：close() 会直接结束进程，cProfile 来不及写结果（7.2）。

    python scripts/profile_env.py --headless --num_envs 1024
    python scripts/profile_env.py --headless --num_envs 1024 --cprofile generated/profile/env_step.prof
"""

import argparse
import os
import subprocess
import sys
import time

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="env.step 计时与内存读数")
parser.add_argument("--num_envs", type=int, default=1024)
parser.add_argument("--steps", type=int, default=200)
parser.add_argument("--cprofile", default=None, help="把计时循环的 cProfile 统计写到这个文件")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch

import galbot_academy.tasks  # noqa: F401  注册任务
from isaaclab_tasks.utils import parse_env_cfg


def proc_vram_mib() -> int:
    """nvidia-smi 报告的本进程显存（MiB）。"""
    out = subprocess.run(
        ["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
        capture_output=True, text=True,
    ).stdout
    return sum(int(m) for p, m in (line.split(", ") for line in out.strip().splitlines()) if int(p) == os.getpid())


def host_mem_gib() -> tuple[float, float]:
    """（本进程 RSS，整机 MemAvailable），GiB。"""
    with open("/proc/self/status") as f:
        rss = next(int(line.split()[1]) for line in f if line.startswith("VmRSS"))
    with open("/proc/meminfo") as f:
        avail = next(int(line.split()[1]) for line in f if line.startswith("MemAvailable"))
    return rss / 2**20, avail / 2**20


def main() -> None:
    cfg = parse_env_cfg("Galbot-Reach-v0", device=args.device, num_envs=args.num_envs)
    env = gym.make("Galbot-Reach-v0", cfg=cfg).unwrapped
    env.reset()
    act = torch.zeros(env.num_envs, env.action_manager.total_action_dim, device=env.device)

    # 给 sim.step 套计时器，单独算出 env.step 里物理所占的时间
    phys = [0.0]
    orig_step = env.sim.step

    def timed_step(*a, **k):
        torch.cuda.synchronize()
        t = time.perf_counter()
        r = orig_step(*a, **k)
        torch.cuda.synchronize()
        phys[0] += time.perf_counter() - t
        return r

    env.sim.step = timed_step
    for _ in range(50):  # 热身
        env.step(act)
    phys[0] = 0.0
    prof = None
    if args.cprofile:
        import cProfile

        prof = cProfile.Profile()
        prof.enable()
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(args.steps):
        env.step(act)
    torch.cuda.synchronize()
    el = time.perf_counter() - t0
    if prof is not None:
        import pstats

        prof.disable()
        os.makedirs(os.path.dirname(args.cprofile) or ".", exist_ok=True)
        prof.dump_stats(args.cprofile)
        print(f"[7.2] cProfile 统计已写到 {args.cprofile}；按自身耗时（tottime）排序的前 15 项：")
        pstats.Stats(prof).sort_stats("tottime").print_stats(15)
    step_ms, phys_ms = el / args.steps * 1000, phys[0] / args.steps * 1000
    print(f"[7.2] num_envs {args.num_envs}，decimation {cfg.decimation}：每个环境步 {step_ms:.2f} ms，"
          f"其中物理（{cfg.decimation} 次 sim.step）{phys_ms:.2f} ms，其余（管理器、Python）{step_ms - phys_ms:.2f} ms")
    mib = 2**20
    print(f"[7.2] torch 显存：memory_allocated {torch.cuda.memory_allocated() / mib:.0f} MiB，"
          f"memory_reserved {torch.cuda.memory_reserved() / mib:.0f} MiB，max_memory_allocated "
          f"{torch.cuda.max_memory_allocated() / mib:.0f} MiB；nvidia-smi 按进程 {proc_vram_mib()} MiB")
    rss, avail = host_mem_gib()
    print(f"[7.2] 主机：本进程 RSS {rss:.2f} GiB，整机 MemAvailable {avail:.2f} GiB")
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
