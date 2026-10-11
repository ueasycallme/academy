# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：matplotlib 3.10（Isaac Sim 5.1.0 的 Python 自带）
# 验证日期：2026-10-11
"""把 sweep_physics.py 的日志画成一张 2×2 图（6.3.1）：左列物理步长、右列位置迭代；上行滑移、下行每控制步墙上时间。不需要启动 Isaac Sim。

每个日志的横轴标签从日志开头的 "[sweep] dt ..." 一行读出；每组的点是成功回合的滑移，横线是中位数，全部失败的组标"0/N 成功"。

    python scripts/plot_sweep.py --dt logs/dt60_d2.log logs/base.log logs/dt240_d8.log \
        --iters logs/pos1.log logs/pos4.log logs/pos8.log logs/base.log --out sweep.png
"""

import argparse
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

parser = argparse.ArgumentParser()
parser.add_argument("--dt", nargs="+", required=True, help="dt 一组的日志（decimation 同步调整的那几组）")
parser.add_argument("--iters", nargs="+", required=True, help="位置迭代一组的日志")
parser.add_argument("--out", required=True)
args = parser.parse_args()

cjk = [f.name for f in font_manager.fontManager.ttflist if "Noto Sans CJK" in f.name]
if cjk:
    plt.rcParams["font.family"] = cjk[0]
plt.rcParams.update({"font.size": 13, "axes.titlesize": 13})

HEAD = re.compile(r"\[sweep\] dt ([\d.]+) s，decimation (\d+).*迭代 位置 (\d+) / 速度 (\d+)")
TRY = re.compile(r"\[sweep\] 第 \d+ 次：(成功|失败)，\d+ 步，滑移 ([\d.]+) cm，每控制步 ([\d.]+) ms")


def read(path):
    head, slips, ms, n = None, [], [], 0
    for line in open(path, errors="replace"):
        if head is None and (m := HEAD.search(line)):
            head = m.groups()
        elif m := TRY.search(line):
            n += 1
            ms.append(float(m.group(3)))
            if m.group(1) == "成功":
                slips.append(float(m.group(2)))
    return head, slips, sorted(ms), n


def median(xs):
    xs = sorted(xs)
    return (xs[(len(xs) - 1) // 2] + xs[len(xs) // 2]) / 2


fig, axes = plt.subplots(2, 2, figsize=(10, 6.4), dpi=150, sharey="row")
for col, (paths, title) in enumerate(((args.dt, "物理步长（控制频率固定 30 Hz）"), (args.iters, "位置迭代次数（dt 1/120）"))):
    labels = []
    for i, path in enumerate(paths):
        (dt, dec, pos, _vel), slips, ms, n = read(path)
        labels.append(f"1/{round(1 / float(dt))}\n×{dec}" if col == 0 else pos)
        ax = axes[0, col]
        if slips:
            ax.scatter([i] * len(slips), slips, s=16, alpha=0.5, color="C0")
            ax.hlines(median(slips), i - 0.25, i + 0.25, color="C3", linewidth=2)
        if len(slips) < n:
            ax.text(i, 0.05, f"{len(slips)}/{n} 成功", ha="center", va="bottom", color="C3")
        axes[1, col].bar(i, median(ms), width=0.55, color="C2")
        axes[1, col].text(i, median(ms), f"{median(ms):.0f}", ha="center", va="bottom")
    for ax in axes[:, col]:
        ax.set_xlim(-0.5, len(paths) - 0.5)
        ax.set_xticks(range(len(paths)), labels)
        ax.grid(alpha=0.3, axis="y")
    axes[0, col].set_title(title)
axes[0, 0].set_ylabel("成功回合的滑移（cm）")
axes[1, 0].set_ylabel("每控制步（ms，中位）")
axes[1, 0].set_xlabel("dt（s）× decimation")
axes[1, 1].set_xlabel("位置迭代（速度迭代 1）")
axes[0, 0].set_ylim(0, None)
axes[1, 0].set_ylim(0, axes[1, 0].get_ylim()[1] * 1.12)  # 给柱顶的数字留空
fig.tight_layout()
fig.savefig(args.out)
print(f"已保存 {args.out}")
