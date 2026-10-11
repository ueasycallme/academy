# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：matplotlib 3.10（Isaac Sim 5.1.0 的 Python 自带）
# 验证日期：2026-10-08（3 段表头与 --labels 为 6.3.2 所加，验证日期 2026-10-12）
"""把 step_response.py --csv 保存的曲线画成一张图（6.1.5）。不需要启动 Isaac Sim。

    python scripts/plot_step.py generated/step/implicit.csv --out generated/step/step_response.png --step 0.5
    python scripts/plot_step.py a.csv b.csv --title "左图|右图" --out both.png --step 0.05 --xmax 0.8   # 6.3.2：并排两图
"""

import argparse
import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

parser = argparse.ArgumentParser()
parser.add_argument("csv", nargs="+", help="一份或几份 CSV；几份时并排画，--title / --labels 用 | 分隔各图")
parser.add_argument("--out", required=True)
parser.add_argument("--step", type=float, default=0.5, help="阶跃幅度，画成虚线")
parser.add_argument("--title", default="right_arm_joint2 阶跃 0.5 rad（隐式，60 N·m，1.5 rad/s）")
parser.add_argument("--labels", default=None, help="逗号分隔的图例，替代按表头生成的（6.3.2）")
parser.add_argument("--xmax", type=float, default=None, help="横轴只画到这一时刻（6.3.2）")
args = parser.parse_args()

# 中文字体：系统里有 Noto Sans CJK 就用它
cjk = [f.name for f in font_manager.fontManager.ttflist if "Noto Sans CJK" in f.name]
if cjk:
    plt.rcParams["font.family"] = cjk[0]
plt.rcParams.update({"font.size": 13, "axes.titlesize": 13, "legend.fontsize": 12})

titles = args.title.split("|")
label_sets = args.labels.split("|") if args.labels else [None] * len(args.csv)
fig, axes = plt.subplots(1, len(args.csv), figsize=(5.25 * len(args.csv) if len(args.csv) > 1 else 8, 4.2), dpi=150, squeeze=False)
for ax, path, title, labels in zip(axes[0], args.csv, titles, label_sets):
    with open(path) as f:
        rows = list(csv.reader(f))
    header, data = rows[0], [[float(x) for x in r] for r in rows[1:]]
    t = [r[0] for r in data]
    names = labels.split(",") if labels else None
    for i, label in enumerate(header[1:], start=1):
        k, d, *rest = label.split(":")  # 表头 K:D（6.1.5）或 K:D:延迟（6.3.2）
        text = f"K={k}, D={d}" + (f", 延迟 {rest[0]}" if rest and rest[0] != "0" else "")
        ax.plot(t, [r[i] for r in data], label=names[i - 1] if names else text, linewidth=1.6)
    ax.axhline(args.step, color="0.4", linestyle="--", linewidth=1.0, label="目标")
    if args.xmax:
        ax.set_xlim(0, args.xmax)
    ax.set_xlabel("时间（s）")
    ax.set_ylabel("相对起点的位置（rad）")
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right", ncol=1 if len(args.csv) > 1 else 2)
fig.tight_layout()
fig.savefig(args.out)
print(f"已保存 {args.out}")
