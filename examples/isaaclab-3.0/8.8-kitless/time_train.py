# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab 3.0.0-EA（v3.0.0-EA tag）；1.5 路线 A（装 isaacsim 6.1.0.0）与路线 C（不装）两个环境
# 验证日期：2026-10-12
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04
"""给一条 `isaaclab train` 命令计时（8.8）：启动到第一次迭代的时间、每次迭代的时间。

本脚本只计时，显存与 RSS 由外部的采样脚本记录（本站用 scratch 里的 run.sh：每秒读一次
`nvidia-smi --query-compute-apps` 与 /proc 的 VmRSS，按进程树累加）。

- 启动时间：从启动子进程到 rsl_rl 打印第一行 "Learning iteration 0/N" 为止（含导入、建场景、第一次 rollout 与更新）；
- 每次迭代：本脚本记下每一行 "Learning iteration k/N" 出现的时刻，相邻两次之差就是一次迭代的墙上时间；
  跳过前 --skip 次后取均值、中位数与范围。rsl_rl 自己打印的 "Iteration time" 只到 0.01 s，太粗，只作对照。

    python time_train.py -- isaaclab train --rl_library rsl_rl --task Isaac-Cartpole-Direct --max_iterations 100 physics=newton_mjwarp
"""

import argparse
import re
import statistics
import subprocess
import sys
import time

parser = argparse.ArgumentParser(description="给 isaaclab train 计时（8.8）")
parser.add_argument("--skip", type=int, default=10, help="每次迭代的时间跳过前几次")
parser.add_argument("--log", default=None, help="把子进程输出另存到这个文件")
parser.add_argument("cmd", nargs=argparse.REMAINDER, help="-- 之后是要计时的命令")
args = parser.parse_args()
cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd

ITER = re.compile(r"Learning iteration (\d+)/(\d+)")
ITER_TIME = re.compile(r"Iteration time:\s*([\d.]+)\s*s")
t0 = time.perf_counter()
first_iter_s = None
iter_stamps = []
iter_times = []
log = open(args.log, "w") if args.log else None
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
for line in proc.stdout:
    if log:
        log.write(line)
    m = ITER.search(line)
    if m:
        now = time.perf_counter() - t0
        iter_stamps.append(now)
        if first_iter_s is None:
            first_iter_s = now
    m = ITER_TIME.search(line)
    if m:
        iter_times.append(float(m.group(1)))
rc = proc.wait()
total_s = time.perf_counter() - t0
gaps = [b - a for a, b in zip(iter_stamps[:-1], iter_stamps[1:])]
kept = gaps[args.skip:]
if first_iter_s is None or not kept:
    print(f"[8.8] 失败：rc {rc}，没有读到迭代输出", flush=True)
    sys.exit(1)
print(f"[8.8] rc {rc}；启动到第一次迭代 {first_iter_s:.1f} s；每次迭代 均值 {statistics.mean(kept) * 1000:.1f} ms、"
      f"中位 {statistics.median(kept) * 1000:.1f} ms（{min(kept) * 1000:.1f}–{max(kept) * 1000:.1f}，{len(kept)} 次，跳过前 {args.skip} 次）；"
      f"rsl_rl 自报中位 {statistics.median(iter_times[args.skip:]):.2f} s；总用时 {total_s:.1f} s", flush=True)
