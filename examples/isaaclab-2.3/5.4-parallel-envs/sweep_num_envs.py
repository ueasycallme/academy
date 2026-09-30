# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2 + rsl-rl-lib 3.1.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""用不同的 num_envs 训练官方 Cartpole（RSL-RL，种子 42），统计吞吐、每次迭代耗时、
平均回合长度第一次达到阈值时的迭代与墙上时间，以及按进程测量的显存峰值。

本脚本自身不启动 Isaac Sim，而是逐个调用 Isaac Lab 的训练脚本；需要 psutil 与 nvidia-smi::

    python sweep_num_envs.py --isaaclab /path/to/IsaacLab
    python sweep_num_envs.py --isaaclab /path/to/IsaacLab --configs 64:3000 4096:150
"""

import argparse
import os
import re
import statistics
import subprocess
import time

import psutil


def run(isaaclab: str, num_envs: int, iters: int, seed: int, log_path: str) -> tuple[int, int, float]:
    """运行一次训练，返回 (返回码, 按进程显存峰值 MiB, 总墙上时间 s)。"""
    cmd = [
        os.path.join(isaaclab, "isaaclab.sh"), "-p", "scripts/reinforcement_learning/rsl_rl/train.py",
        "--task", "Isaac-Cartpole-v0", "--headless", "--seed", str(seed),
        "--num_envs", str(num_envs), "--max_iterations", str(iters),
    ]
    start = time.perf_counter()
    with open(log_path, "w") as log:
        proc = subprocess.Popen(cmd, cwd=isaaclab, stdout=log, stderr=subprocess.STDOUT)
        peak = 0
        while proc.poll() is None:
            try:
                tree = {proc.pid} | {c.pid for c in psutil.Process(proc.pid).children(recursive=True)}
            except psutil.NoSuchProcess:
                break
            out = subprocess.run(
                ["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
                capture_output=True, text=True,
            ).stdout
            used = sum(int(m) for pid, m in (line.split(", ") for line in out.strip().splitlines() if line) if int(pid) in tree)
            peak = max(peak, used)
            time.sleep(0.5)
    return proc.returncode, peak, time.perf_counter() - start


def parse(log_path: str, target_len: float) -> dict:
    text = re.sub(r"\x1b\[[0-9;]*m", "", open(log_path, encoding="utf-8", errors="replace").read())
    fps, it_time, first, first_elapsed = [], [], None, None
    for block in re.split(r"\n\s*Learning iteration ", text)[1:]:
        it = int(block.split("/")[0])
        fps.append(float(re.search(r"Computation:\s+(\d+) steps/s", block).group(1)))
        it_time.append(float(re.search(r"Iteration time:\s+([\d.]+)s", block).group(1)))
        m = re.search(r"Mean episode length:\s+([\d.]+)", block)
        if first is None and m and float(m.group(1)) >= target_len:
            first = it
            h, mi, s = re.search(r"Time elapsed:\s+(\d+):(\d+):(\d+)", block).groups()
            first_elapsed = int(h) * 3600 + int(mi) * 60 + int(s)
    train_time = re.search(r"Training time: ([\d.]+) seconds", text)
    return {
        "fps": statistics.median(fps), "it_time": statistics.median(it_time), "iters": len(fps),
        "first": first, "first_elapsed": first_elapsed, "train_time": float(train_time.group(1)) if train_time else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--isaaclab", required=True, help="Isaac Lab 仓库路径（含 isaaclab.sh）")
    parser.add_argument("--configs", nargs="*", default=["64:3000", "256:1200", "1024:400", "4096:150"],
                        help="num_envs:max_iterations，迭代数取到足以学会为止")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--target_len", type=float, default=299.0, help="平均回合长度阈值（Cartpole 上限 300）")
    parser.add_argument("--log_dir", default=".", help="保存各次训练终端输出的目录")
    args = parser.parse_args()

    print("num_envs | 批量 | 环境步/s（中位数） | 每次迭代 s（中位数） | 首次达到阈值：迭代 / 墙上 s | 训练总时长 s | 显存峰值 MiB（按进程） | 返回码")
    for item in args.configs:
        num_envs, iters = (int(x) for x in item.split(":"))
        log_path = os.path.join(args.log_dir, f"train_{num_envs}.log")
        rc, peak, _ = run(args.isaaclab, num_envs, iters, args.seed, log_path)
        r = parse(log_path, args.target_len)
        first = f"{r['first']} / {r['first_elapsed']}" if r["first"] is not None else f"未达到（{r['iters']} 次内）"
        print(f"{num_envs:8d} | {num_envs * 16:6d} | {r['fps']:18,.0f} | {r['it_time']:20.3f} | {first:>26s} | {r['train_time']:12.1f} | {peak:22d} | {rc}", flush=True)


if __name__ == "__main__":
    main()
