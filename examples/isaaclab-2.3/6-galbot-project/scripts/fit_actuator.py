# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.10 / 3.11 + numpy；不启动 Isaac Sim
# 验证日期：2026-10-12
"""用网格搜索拟合执行器参数（6.3.2）。不需要启动 Isaac Sim。

输入是 step_response.py --csv 保存的曲线：一份"测量"（--pair 的前半，取其中一列），一份候选网格
（后半，由 step_response.py --grid 生成，每列一组 K:D:延迟）。对每个候选算目标函数：

    J(K, D, 延迟) = 各激励的 RMSE(候选曲线 − 测量曲线) / 阶跃幅度 的平均

即在同一组采样时刻上逐点比较、按激励幅度归一化，再在几种激励上取平均。给多组 --pair（例如两种阶跃幅度）
就是"多种激励一起拟合"。输出 J 最小的若干组，以及 J 不超过最小值 (1 + --tie) 倍的候选个数：个数多说明拟合不唯一。

    python scripts/fit_actuator.py --pair ref_005.csv:cand_005.csv
    python scripts/fit_actuator.py --pair ref_005.csv:cand_005.csv --pair ref_002.csv:cand_002.csv --noise 0.0005 --truth 600:30:2
"""

import argparse
import csv

import numpy as np


def load(path: str) -> tuple[list[str], np.ndarray, np.ndarray]:
    """返回 (列名, t, 曲线矩阵 (列, 时间))。"""
    with open(path) as f:
        rows = list(csv.reader(f))
    data = np.array([[float(x) for x in r] for r in rows[1:]])
    return rows[0][1:], data[:, 0], data[:, 1:].T


def objective(ref: np.ndarray, cand: np.ndarray, amplitude: float) -> np.ndarray:
    """每个候选与测量曲线的归一化 RMSE。ref: (时间,)；cand: (候选, 时间)。"""
    return np.sqrt(((cand - ref[None, :]) ** 2).mean(axis=1)) / abs(amplitude)


def fit(pairs: list[tuple[np.ndarray, np.ndarray, float]], labels: list[str]) -> np.ndarray:
    """多种激励的目标函数取平均。各激励的候选网格必须相同（列名一致）。"""
    return np.mean([objective(ref, cand, amp) for ref, cand, amp in pairs], axis=0)


def parse_label(label: str) -> tuple[float, float, int]:
    k, d, *rest = label.split(":")
    return float(k), float(d), int(rest[0]) if rest else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="网格搜索拟合 stiffness / damping / 延迟（6.3.2）")
    parser.add_argument("--pair", action="append", required=True, help="测量 CSV:候选 CSV，可给多次（多种激励）")
    parser.add_argument("--ref_col", type=int, default=0, help="测量 CSV 里取第几列（从 0 起）")
    parser.add_argument("--window", type=float, default=None, help="只比较前若干秒")
    parser.add_argument("--noise", type=float, default=0.0, help="给测量曲线加高斯噪声的标准差（rad），模拟编码器噪声")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--truth", default=None, help="已知的真值 K:D:延迟（sim-to-sim 演示时用来算恢复误差）")
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--tie", type=float, default=0.1, help="J ≤ 最小值 × (1 + tie) 的候选算作并列")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    pairs, labels = [], None
    for spec in args.pair:
        ref_path, cand_path = spec.split(":", 1)
        _, t_ref, ref = load(ref_path)
        cand_labels, t_cand, cand = load(cand_path)
        assert np.allclose(t_ref, t_cand), f"{spec}：两份曲线的采样时刻不同"
        assert labels is None or cand_labels == labels, "各激励的候选网格必须相同"
        labels = cand_labels
        r = ref[args.ref_col] + (rng.normal(0.0, args.noise, ref.shape[1]) if args.noise > 0 else 0.0)
        keep = slice(None) if args.window is None else t_ref <= args.window
        amplitude = ref[args.ref_col][-max(1, len(t_ref) // 8):].mean()  # 末 1/8 的均值当作阶跃的实际幅度
        pairs.append((r[keep], cand[:, keep], amplitude))

    J = fit(pairs, labels)
    order = np.argsort(J)
    best = J[order[0]]
    ties = int((J <= best * (1 + args.tie)).sum())
    print(f"[fit] {len(labels)} 个候选，{len(pairs)} 种激励；最小 J = {best:.5f}；J ≤ {1 + args.tie:.2f} × 最小值的有 {ties} 个")
    print(f"{'排名':>4s} {'stiffness':>9s} {'damping':>8s} {'延迟':>4s} {'J':>9s}")
    for rank, i in enumerate(order[: args.top], start=1):
        k, d, lag = parse_label(labels[i])
        print(f"{rank:4d} {k:9g} {d:8g} {lag:4d} {J[i]:9.5f}")
    if args.truth:
        tk, td, tl = parse_label(args.truth)
        k, d, lag = parse_label(labels[order[0]])
        print(f"[fit] 真值 K {tk:g} / D {td:g} / 延迟 {tl}；拟合 K {k:g}（{(k - tk) / tk * 100:+.0f}%）/ D {d:g}（{(d - td) / td * 100:+.0f}%）/ 延迟 {lag}（{lag - tl:+d} 步）")


if __name__ == "__main__":
    main()
