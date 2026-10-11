# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.10（系统 python3）/ 3.11（Isaac 环境）+ numpy；不依赖 Isaac Sim
# 验证日期：2026-10-12
"""无 GPU：fit_actuator 的目标函数与网格搜索（6.3.2）。曲线用一个离散的二阶系统生成，不是 Isaac Sim 的结果。"""

import numpy as np

from fit_actuator import fit, objective, parse_label

DT, N = 1 / 120, 240


def response(k: float, d: float, lag: int, step: float = 0.05, inertia: float = 0.5) -> np.ndarray:
    """单位转动惯量上的 PD + 指令延迟（半隐式欧拉），返回位置曲线。"""
    q = v = 0.0
    target = np.r_[np.zeros(lag), np.full(N, step)][:N]
    out = []
    for i in range(N):
        a = (k * (target[i] - q) - d * v) / inertia
        v += a * DT
        q += v * DT
        out.append(q)
    return np.array(out)


GRID = [(k, d, lag) for k in (200, 400, 800) for d in (10, 20, 40) for lag in (0, 1, 2, 3)]
LABELS = [f"{k}:{d}:{lag}" for k, d, lag in GRID]


def test_objective_zero_on_identical_curve():
    ref = response(400, 20, 1)
    assert objective(ref, ref[None, :], 0.05)[0] == 0.0


def test_grid_search_recovers_truth():
    ref = response(400, 20, 2)
    cand = np.stack([response(*g) for g in GRID])
    J = fit([(ref, cand, 0.05)], LABELS)
    assert parse_label(LABELS[int(np.argmin(J))]) == (400.0, 20.0, 2)


def test_two_excitations_average():
    refs = [response(800, 10, 0, step=s) for s in (0.05, 0.02)]
    cands = [np.stack([response(*g, step=s) for g in GRID]) for s in (0.05, 0.02)]
    J = fit([(refs[0], cands[0], 0.05), (refs[1], cands[1], 0.02)], LABELS)
    assert parse_label(LABELS[int(np.argmin(J))]) == (800.0, 10.0, 0)
    # 线性系统按幅度归一化后两种激励的 J 相同，平均后最小值仍为 0
    assert J.min() < 1e-12
