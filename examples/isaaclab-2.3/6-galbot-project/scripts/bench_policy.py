# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab 2.3.2（rsl_rl 3.1.2）；torch 2.7.0+cu128、onnxruntime 1.20.1；不需要 Isaac Sim
# 验证日期：2026-10-11
# CPU：Intel Core i7-14700KF（20 核 28 线程）；GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""核对与测量导出的策略（6.7.1）。两个子命令：

consistency：检查点里的 actor（torch，CPU）、TorchScript（torch.jit.load）、ONNX（onnxruntime，CPU）三种加载方式，
    在随机观测与一条真实评估轨迹（eval_reach.py --record_obs 存下的 .npz）上的输出差。
latency：torch CPU、torch GPU、onnxruntime CPU 在批 1 与批 64 下每次调用的延迟（预热后计时）。

    python scripts/bench_policy.py consistency logs/rsl_rl/galbot_reach/<运行>/model_999.pt --traj traj.npz
    python scripts/bench_policy.py latency logs/rsl_rl/galbot_reach/<运行>/model_999.pt
部署件取 <运行>/deploy/（export_policy.py --dynamic-batch 的输出）。
"""

import argparse
import os
import sys
import time

import numpy as np
import onnxruntime as ort
import torch

sys.path.insert(0, os.path.dirname(__file__))
from export_policy import load_policy  # noqa: E402


def stats(a: np.ndarray, b: np.ndarray) -> str:
    d = np.abs(a.astype(np.float64) - b.astype(np.float64))
    return f"最大差 {d.max():.2e}，平均差 {d.mean():.2e}"


def consistency(args, deploy: str) -> None:
    policy = load_policy(args.checkpoint)
    jit = torch.jit.load(os.path.join(deploy, "policy.pt"), map_location="cpu")
    sess = ort.InferenceSession(os.path.join(deploy, "policy.onnx"), providers=["CPUExecutionProvider"])
    inputs = {"随机观测 1000 个（标准正态，种子 0）": np.random.default_rng(0).standard_normal((1000, 28)).astype(np.float32)}
    gpu_actions = None
    if args.traj:
        rec = np.load(args.traj)
        obs = rec["obs"]  # (步数, 环境数, 28)
        inputs[f"评估轨迹 {obs.shape[1]} 条 × {obs.shape[0]} 步"] = obs.transpose(1, 0, 2).reshape(-1, obs.shape[2])
        gpu_actions = rec["actions"].transpose(1, 0, 2).reshape(-1, rec["actions"].shape[2])
    for name, x in inputs.items():
        with torch.inference_mode():
            ref = policy.act_inference({"policy": torch.from_numpy(x)}).numpy()  # 检查点 actor，即 play.py 用的推理策略
            out_jit = jit(torch.from_numpy(x)).numpy()
        out_onnx = sess.run(None, {"obs": x})[0]
        print(f"[consistency] {name}：动作绝对值最大 {np.abs(ref).max():.2f}")
        print(f"  TorchScript vs 检查点：{stats(out_jit, ref)}")
        print(f"  ONNX       vs 检查点：{stats(out_onnx, ref)}")
        if gpu_actions is not None and name.startswith("评估轨迹"):
            print(f"  仿真里 GPU 上算的动作 vs 检查点（CPU）：{stats(gpu_actions, ref)}")


def timeit(fn, warmup: int, n: int) -> tuple[float, float]:
    for _ in range(warmup):
        fn()
    t = np.empty(n)
    for i in range(n):
        t0 = time.perf_counter_ns()
        fn()
        t[i] = time.perf_counter_ns() - t0
    t /= 1e3  # 微秒
    return float(np.median(t)), float(np.percentile(t, 99))


def latency(args, deploy: str) -> None:
    rows = []
    for batch in (1, 64):
        x = np.random.default_rng(0).standard_normal((batch, 28)).astype(np.float32)
        # torch：用部署件 policy.pt（TorchScript），inference_mode 下调用；CPU 分别测 1 线程与默认线程数
        for device, threads in [("cpu", t) for t in args.torch_threads] + [("cuda", None)]:
            if threads:
                torch.set_num_threads(threads)
            jit = torch.jit.load(os.path.join(deploy, "policy.pt"), map_location=device)
            xt = torch.from_numpy(x).to(device)

            def run_torch(jit=jit, xt=xt, device=device):
                with torch.inference_mode():
                    y = jit(xt)
                    if device == "cuda":
                        y.cpu()  # 结果拿回 CPU 才算完成（同时同步 GPU）
                    return y

            name = f"torch {device.upper()}" + (f"（{threads} 线程）" if device == "cpu" else "（结果拷回 CPU）")
            rows.append((name, batch, *timeit(run_torch, args.warmup, args.n)))
        for threads in args.ort_threads:
            so = ort.SessionOptions()
            so.intra_op_num_threads = threads
            so.inter_op_num_threads = 1
            sess = ort.InferenceSession(os.path.join(deploy, "policy.onnx"), so, providers=["CPUExecutionProvider"])
            rows.append((f"onnxruntime CPU（{threads} 线程）", batch, *timeit(lambda: sess.run(None, {"obs": x}), args.warmup, args.n)))
    print(f"[latency] 每种组合预热 {args.warmup} 次，再计时 {args.n} 次；单位 μs")
    for name, batch, med, p99 in rows:
        print(f"  {name:28s} 批 {batch:3d}：中位数 {med:8.1f}，99% 分位 {p99:8.1f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="核对与测量导出的策略")
    parser.add_argument("mode", choices=["consistency", "latency"])
    parser.add_argument("checkpoint")
    parser.add_argument("--deploy_dir", default=None, help="默认 <运行目录>/deploy")
    parser.add_argument("--traj", default=None, help="eval_reach.py --record_obs 存下的 .npz")
    parser.add_argument("--warmup", type=int, default=1000)
    parser.add_argument("-n", type=int, default=10000)
    parser.add_argument("--ort_threads", type=int, nargs="+", default=[1, 4])
    parser.add_argument("--torch_threads", type=int, nargs="+", default=[1, torch.get_num_threads()], help="默认 1 与 torch 的默认线程数")
    args = parser.parse_args()
    deploy = args.deploy_dir or os.path.join(os.path.dirname(args.checkpoint), "deploy")
    consistency(args, deploy) if args.mode == "consistency" else latency(args, deploy)


if __name__ == "__main__":
    main()
