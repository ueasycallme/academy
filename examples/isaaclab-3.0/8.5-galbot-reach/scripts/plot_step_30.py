# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：matplotlib（Isaac Lab v3.0.0 环境）；不启动仿真
# 验证日期：2026-10-23
# GPU：不需要
"""把 step_response_30.py 写出的几条曲线（t, q 相对起点）画在一张图上（8.10；样式同 6.3.2 的 plot_step.py）。

    python scripts/plot_step_30.py step_physx.csv step_newton.csv --labels PhysX Newton --step 0.05 --out step_compare.png
"""

import argparse
import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

parser = argparse.ArgumentParser(description="画阶跃响应对照（8.10）")
parser.add_argument("csv", nargs="+")
parser.add_argument("--labels", nargs="+", required=True)
parser.add_argument("--step", type=float, default=0.05)
parser.add_argument("--xmax", type=float, default=0.6)
parser.add_argument("--out", required=True)
args = parser.parse_args()

cjk = [f.name for f in font_manager.fontManager.ttflist if "Noto Sans CJK" in f.name]
if cjk:
    plt.rcParams["font.family"] = cjk[0]
plt.rcParams.update({"font.size": 13, "axes.titlesize": 13, "legend.fontsize": 12})

fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
for path, label, style in zip(args.csv, args.labels, ["-", "--", ":"]):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    t = [float(r["t"]) for r in rows]
    q = [float(r["q"]) * 1000 for r in rows]  # mrad
    ax.plot(t, q, style, linewidth=2, label=label)
ax.axhline(args.step * 1000, color="gray", linewidth=1, linestyle="-.", label="目标")
ax.set_xlim(0, args.xmax)
ax.set_xlabel("阶跃后的时间（s）")
ax.set_ylabel("相对起点（mrad）")
ax.grid(alpha=0.3)
ax.legend(loc="lower right")
fig.tight_layout()
fig.savefig(args.out)
print(f"已保存 {args.out}")
