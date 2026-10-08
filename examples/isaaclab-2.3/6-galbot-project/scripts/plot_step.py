# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：matplotlib 3.10（Isaac Sim 5.1.0 的 Python 自带）
# 验证日期：2026-10-08
"""把 step_response.py --csv 保存的曲线画成一张图（6.1.5）。不需要启动 Isaac Sim。

    python scripts/plot_step.py generated/step/implicit.csv --out generated/step/step_response.png --step 0.5
"""

import argparse
import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

parser = argparse.ArgumentParser()
parser.add_argument("csv")
parser.add_argument("--out", required=True)
parser.add_argument("--step", type=float, default=0.5, help="阶跃幅度，画成虚线")
parser.add_argument("--title", default="right_arm_joint2 阶跃 0.5 rad（隐式，60 N·m，1.5 rad/s）")
args = parser.parse_args()

# 中文字体：系统里有 Noto Sans CJK 就用它
cjk = [f.name for f in font_manager.fontManager.ttflist if "Noto Sans CJK" in f.name]
if cjk:
    plt.rcParams["font.family"] = cjk[0]
plt.rcParams.update({"font.size": 13, "axes.titlesize": 13, "legend.fontsize": 12})

with open(args.csv) as f:
    rows = list(csv.reader(f))
header, data = rows[0], [[float(x) for x in r] for r in rows[1:]]
t = [r[0] for r in data]

fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
for i, label in enumerate(header[1:], start=1):
    k, d = label.split(":")
    ax.plot(t, [r[i] for r in data], label=f"K={k}, D={d}", linewidth=1.6)
ax.axhline(args.step, color="0.4", linestyle="--", linewidth=1.0, label="目标")
ax.set_xlabel("时间（s）")
ax.set_ylabel("相对起点的位置（rad）")
ax.set_title(args.title)
ax.grid(alpha=0.3)
ax.legend(loc="lower right", ncol=2)
fig.tight_layout()
fig.savefig(args.out)
print(f"已保存 {args.out}")
