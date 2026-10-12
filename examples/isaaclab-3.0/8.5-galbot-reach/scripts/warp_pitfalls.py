# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：warp-lang 1.16.0，torch 2.11.0+cu128（Isaac Lab v3.0.0-EA 环境）
# 验证日期：2026-10-12
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04
"""8.9 的两个坑：传给 Warp 内核的数组 dtype 不对、device 不对时报什么。不启动仿真。

    python scripts/warp_pitfalls.py
"""

import torch
import warp as wp

from galbot_academy.tasks.reach.mdp.rewards_warp import _tcp_position_error_kernel as K

n, nb = 4, 3
dev = "cuda:0"
good = dict(
    root_pos=wp.zeros(n, dtype=wp.vec3f, device=dev),
    root_quat=wp.array([wp.quat_identity()] * n, dtype=wp.quatf, device=dev),
    body_pos=wp.zeros((n, nb), dtype=wp.vec3f, device=dev),
    body_quat=wp.array([[wp.quat_identity()] * nb] * n, dtype=wp.quatf, device=dev),
    command=wp.zeros((n, 7), dtype=wp.float32, device=dev),
)
out = wp.zeros(n, dtype=wp.float32, device=dev)


def launch(name: str, **override) -> None:
    args = {**good, **override}
    try:
        wp.launch(K, dim=n, inputs=[*args.values(), 0, wp.vec3f(0.0, 0.0, 0.1)], outputs=[out], device=dev)
        wp.synchronize()
        print(f"[8.9] {name}：没有报错，out = {out.numpy().tolist()}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[8.9] {name}：{type(e).__name__}: {str(e).splitlines()[0]}", flush=True)


launch("正常")
launch("指令是 float64 的 torch 张量", command=wp.from_torch(torch.zeros(n, 7, dtype=torch.float64, device=dev)))
cmd_vals = [[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]] * n  # 目标在根系 x = 1 m，正确结果是 ‖(0, 0, 0.1) − (1, 0, 0)‖ ≈ 1.005
launch("指令在 GPU 上（对照）", command=wp.array(cmd_vals, dtype=wp.float32, device=dev))
launch("指令在 CPU 上", command=wp.array(cmd_vals, dtype=wp.float32, device="cpu"))
launch("根位置给成 (N, 3) 的 float32 数组", root_pos=wp.zeros((n, 3), dtype=wp.float32, device=dev))
