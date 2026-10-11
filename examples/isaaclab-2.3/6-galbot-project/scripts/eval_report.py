# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.11（numpy、matplotlib；--bc_source 另需 h5py；不需要 Isaac Sim）
# 验证日期：2026-10-11
"""读逐样本 CSV，出 6.6.2 的表与图：区间、切片、失败模式、阈值敏感性。

reach 的 CSV 由 `eval_reach.py --csv` 写出，每段目标末尾一行：
    seed, task, widen（目标范围外扩的米数）, env, segment（1–3）, target_x/y/z（目标位置，机器人根坐标系，m）,
    pos_err（TCP 位置误差，m）, rot_err（姿态误差，rad）, moved（该段最后 0.5 s 内右臂关节位置的最大变化，rad）
pick-place BC 的 CSV 由 `eval_bc_pick_place.py --csv` 写出，每回合一行：
    seed, episode, stage（0–3）, stage_name, end（成功 / 方块掉落 / 到回合上限）, steps, lifted（0/1）,
    object_x/y（方块起点）, target_x/y（放置垫），机器人根坐标系，m

    python scripts/eval_report.py --reach s0.csv s1.csv s2.csv --reach_dr dr.csv --reach_wide wide.csv --bc bc100.csv \
        --bc_source datasets/galbot_pick_place.hdf5 --out_dir generated/eval
"""

import argparse
import csv
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

SUCCESS = 0.05  # reach 的成功阈值（m），与 6.6.1 的"< 5 cm"相同
STUCK = 0.01  # 最后 0.5 s 内关节位置变化小于它算"停住"（rad），与 eval_reach.py 相同
ROT_OK = 0.1  # 姿态误差小于它算"姿态对了"（rad）


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """成功率的 Wilson 区间（95%）。"""
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z / (1 + z * z / n) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return c - h, c + h


def rate(ok: np.ndarray) -> str:
    k, n = int(ok.sum()), len(ok)
    lo, hi = wilson(k, n)
    return f"{k / n * 100:.1f}%（{lo * 100:.1f}–{hi * 100:.1f}）"


def load(paths: list[str]) -> dict[str, np.ndarray]:
    rows = []
    for p in paths:
        with open(p) as f:
            rows += list(csv.DictReader(f))
    out = {}
    for key in rows[0]:
        vals = [r[key] for r in rows]
        try:
            out[key] = np.array([float(v) for v in vals])
        except ValueError:
            out[key] = np.array(vals)
    return out


def reach_tables(d: dict, label: str) -> None:
    e = d["pos_err"]
    print(f"\n## reach：{label}（{len(e)} 个样本）")
    print(f"中位数 {np.median(e) * 100:.2f} cm；< 5 cm {rate(e < SUCCESS)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="评估报告：区间、切片、失败模式、阈值敏感性")
    parser.add_argument("--reach", nargs="+", required=True, help="同一评估分布、不同种子的 reach CSV")
    parser.add_argument("--reach_dr", default=None)
    parser.add_argument("--reach_wide", default=None)
    parser.add_argument("--bc", default=None)
    parser.add_argument("--bc_source", default=None, help="6.4.6 的源示范 HDF5：按方块起点是否落在源示范覆盖的 y 范围内再切一次")
    parser.add_argument("--out_dir", default="generated/eval")
    args = parser.parse_args()

    # 表 1：样本量与区间宽度（p = 0.8 与 0.4，即 reach 与 BC 附近）
    print("## 表 1：Wilson 区间宽度（95%）")
    for n in (30, 100, 300, 1000):
        cells = []
        for p in (0.8, 0.4):
            lo, hi = wilson(round(p * n), n)
            cells.append(f"p={p}：±{(hi - lo) / 2 * 100:.1f} 个百分点")
        print(f"N={n}：" + "；".join(cells))

    # 表 2：换评估种子
    print("\n## 表 2：评估种子")
    per_seed = [load([p]) for p in args.reach]
    for d in per_seed:
        e = d["pos_err"]
        print(f"种子 {int(d['seed'][0])}：中位数 {np.median(e) * 100:.2f} cm，< 2 cm {rate(e < 0.02)}，< 5 cm {rate(e < SUCCESS)}，"
              f"均值 {e.mean() * 100:.2f} cm")
    d = load(args.reach)
    e = d["pos_err"]
    print(f"合并 {len(e)} 个：中位数 {np.median(e) * 100:.2f} cm，< 5 cm {rate(e < SUCCESS)}")

    # 表 3：按条件切片（3 个种子合并）。分界取各轴采样范围的中点
    print("\n## 表 3：按目标位置与段序号切片（3 个种子合并）")
    mids = {"x": 0.45, "y": -0.275, "z": 1.325}
    names = {"x": ("近（x < 45 cm）", "远（x ≥ 45 cm）"), "y": ("偏右（y < −27.5 cm）", "偏左、靠身体中线（y ≥ −27.5 cm）"),
             "z": ("低（z < 132.5 cm）", "高（z ≥ 132.5 cm）")}
    for ax, m in mids.items():
        t = d[f"target_{ax}"]
        for name, sel in zip(names[ax], (t < m, t >= m)):
            print(f"{name}：N={sel.sum()}，中位数 {np.median(e[sel]) * 100:.2f} cm，< 5 cm {rate(e[sel] < SUCCESS)}")
    for s in (1, 2, 3):
        sel = d["segment"] == s
        print(f"第 {s} 段：N={sel.sum()}，中位数 {np.median(e[sel]) * 100:.2f} cm，< 5 cm {rate(e[sel] < SUCCESS)}")

    # 表 4：失败模式（误差 ≥ 5 cm 的样本）
    print("\n## 表 4：reach 的失败模式（误差 ≥ 5 cm）")
    fail = e >= SUCCESS
    stuck = fail & (d["moved"] < STUCK)
    moving = fail & (d["moved"] >= STUCK)
    print(f"失败 {fail.sum()} / {len(e)}：停住没到 {stuck.sum()}，还在动 {moving.sum()}；"
          f"其中姿态已对（< {ROT_OK} rad）的 {(fail & (d['rot_err'] < ROT_OK)).sum()}")
    print(f"位置达标但姿态 ≥ {ROT_OK} rad：{((~fail) & (d['rot_err'] >= ROT_OK)).sum()}")
    for name, sel in (("停住没到", stuck), ("还在动", moving)):
        if sel.any():
            i = np.flatnonzero(sel)[np.argmax(e[sel])]
            print(f"  {name}最大的一个：种子 {int(d['seed'][i])} 环境 {int(d['env'][i])} 第 {int(d['segment'][i])} 段，"
                  f"目标 ({d['target_x'][i]:.3f}, {d['target_y'][i]:.3f}, {d['target_z'][i]:.3f})，误差 {e[i] * 100:.2f} cm，"
                  f"姿态 {d['rot_err'][i]:.3f} rad，最后 0.5 s 关节变化 {d['moved'][i]:.4f} rad")
        print(f"  {name}的目标位置均值：x {d['target_x'][sel].mean():.3f}，y {d['target_y'][sel].mean():.3f}，z {d['target_z'][sel].mean():.3f}"
              if sel.any() else "")
    print(f"  全部样本的目标位置均值：x {d['target_x'].mean():.3f}，y {d['target_y'].mean():.3f}，z {d['target_z'].mean():.3f}")

    # 表 5：阈值敏感性
    print("\n## 表 5：成功阈值（3 个种子合并）")
    print("；".join(f"{t} cm：{rate(e < t / 100)}" for t in (2, 3, 5, 8)))

    # 表 6：评估分布
    print("\n## 表 6：评估分布（种子 0）")
    for label, path in (("与训练相同（Galbot-Reach-Play-v0）", args.reach[0]), ("开域随机化（Galbot-Reach-DR-v0）", args.reach_dr),
                        ("目标范围各向外扩 5 cm", args.reach_wide)):
        if path:
            x = load([path])["pos_err"]
            print(f"{label}：中位数 {np.median(x) * 100:.2f} cm，90% 分位 {np.quantile(x, 0.9) * 100:.2f} cm，< 5 cm {rate(x < SUCCESS)}")
    if args.reach_wide:
        w = load([args.reach_wide])
        inside = (w["target_x"] >= 0.30) & (w["target_x"] <= 0.60) & (w["target_y"] >= -0.40) & (w["target_y"] <= -0.15) & (
            w["target_z"] >= 1.15) & (w["target_z"] <= 1.50)
        for label, sel in (("  其中落在训练范围内的", inside), ("  其中落在训练范围外的", ~inside)):
            print(f"{label}：N={sel.sum()}，中位数 {np.median(w['pos_err'][sel]) * 100:.2f} cm，< 5 cm {rate(w['pos_err'][sel] < SUCCESS)}")

    # BC
    if args.bc:
        b = load([args.bc])
        ok = b["stage"] == 3
        print(f"\n## BC：{len(ok)} 回合，成功 {rate(ok)}")
        for s, name in enumerate(["没抓住", "抓住了但没送到", "送到了但没放成", "成功"]):
            sel = b["stage"] == s
            ends = {k: int((b["end"][sel] == k).sum()) for k in ("成功", "方块掉落", "到回合上限")}
            print(f"{name}：{sel.sum()}（{ends}）")
        dist = np.hypot(b["object_x"] - b["target_x"], b["object_y"] - b["target_y"])
        cut = {"object_x": np.median(b["object_x"]), "object_y": np.median(b["object_y"]), "dist": np.median(dist)}
        cols = {"object_x": b["object_x"], "object_y": b["object_y"], "dist": dist}
        labels = {"object_x": "方块起点 x", "object_y": "方块起点 y", "dist": "方块到放置垫的距离"}
        for k, v in cols.items():
            for name, sel in ((f"{labels[k]} < 中位数 {cut[k] * 100:.1f} cm", v < cut[k]), (f"{labels[k]} ≥ 中位数", v >= cut[k])):
                print(f"{name}：N={sel.sum()}，成功 {rate(ok[sel])}")
        if args.bc_source:
            import h5py

            with h5py.File(args.bc_source, "r") as f:
                ys = [f["data"][k]["obs"]["object_position"][0, 1] for k in f["data"]]
            lo, hi = min(ys), max(ys)
            inside = (b["object_y"] >= lo) & (b["object_y"] <= hi)
            print(f"源示范的方块起点 y：{lo * 100:.1f} … {hi * 100:.1f} cm（{len(ys)} 条）")
            for name, sel in (("方块起点 y 在源示范范围内", inside), ("在范围外", ~inside)):
                print(f"{name}：N={sel.sum()}，成功 {rate(ok[sel])}")
        print(f"抓住了但没送到的回合里，方块举起过 3 cm 的：{int(b['lifted'][b['stage'] == 1].sum())} / {int((b['stage'] == 1).sum())}")

    # 图 1：reach 误差随目标位置（俯视 x–y、侧视 x–z），每格取中位数
    cjk = [f.name for f in font_manager.fontManager.ttflist if "Noto Sans CJK" in f.name]
    if cjk:
        plt.rcParams["font.family"] = cjk[0]
    plt.rcParams.update({"font.size": 14, "axes.titlesize": 14})
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), dpi=150, gridspec_kw={"wspace": 0.35})
    bins = {"x": np.linspace(0.30, 0.60, 7), "y": np.linspace(-0.40, -0.15, 6), "z": np.linspace(1.15, 1.50, 8)}
    for ax, (a, b2) in zip(axes, (("x", "y"), ("x", "z"))):
        u, v = d[f"target_{a}"], d[f"target_{b2}"]
        grid = np.full((len(bins[b2]) - 1, len(bins[a]) - 1), np.nan)
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                sel = (u >= bins[a][j]) & (u < bins[a][j + 1]) & (v >= bins[b2][i]) & (v < bins[b2][i + 1])
                if sel.sum() >= 10:
                    grid[i, j] = np.median(e[sel]) * 100
        im = ax.imshow(grid, origin="lower", cmap="viridis", vmin=1.5, vmax=5.5, aspect="auto",
                       extent=(bins[a][0] * 100, bins[a][-1] * 100, bins[b2][0] * 100, bins[b2][-1] * 100))
        ax.set_xlabel(f"目标 {a}（cm）")
        ax.set_ylabel(f"目标 {b2}（cm）")
        ax.set_title("俯视：x–y" if b2 == "y" else "侧视：x–z")
    fig.colorbar(im, ax=axes, label="位置误差中位数（cm），≥ 5.5 同色")
    os.makedirs(args.out_dir, exist_ok=True)
    fig.savefig(os.path.join(args.out_dir, "reach_error_map.png"), bbox_inches="tight")
    print(f"\n[INFO] 图写到 {args.out_dir}/reach_error_map.png")


if __name__ == "__main__":
    main()
