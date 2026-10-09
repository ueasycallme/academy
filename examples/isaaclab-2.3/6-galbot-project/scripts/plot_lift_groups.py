# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.11（matplotlib、tensorboard，不需要 Isaac Sim）
# 验证日期：2026-10-09
"""把 lift 各组训练（6.4.3）的四条关键曲线画在一起：举起奖励、掉落终止比例、接近奖励、动作噪声。

每个运行目录一条线，图例取运行名的最后一段（如 g3_42）或 --labels 给出的名字。

    python scripts/plot_lift_groups.py logs/rsl_rl/galbot_lift/<运行 1> … --labels 第1组 第2组 … --out generated/train/lift_groups.png
"""

import argparse
import glob
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

PANELS = [
    ("Episode_Reward/lifting_object", "举起奖励（每回合）"),
    ("Episode_Termination/object_dropping", "掉落终止的比例"),
    ("Episode_Reward/reaching_object", "接近奖励（每回合）"),
    ("Policy/mean_noise_std", "动作噪声标准差"),
]

parser = argparse.ArgumentParser()
parser.add_argument("runs", nargs="+", help="运行目录（含 events.out.tfevents.*）")
parser.add_argument("--labels", nargs="*", default=None)
parser.add_argument("--out", required=True)
args = parser.parse_args()

cjk = [f.name for f in font_manager.fontManager.ttflist if "Noto Sans CJK" in f.name]
if cjk:
    plt.rcParams["font.family"] = cjk[0]
plt.rcParams.update({"font.size": 13, "axes.titlesize": 13, "legend.fontsize": 13})

fig, axes = plt.subplots(2, 2, figsize=(11, 7), dpi=150)
labels = args.labels or [os.path.basename(r.rstrip("/")).split("_", 2)[-1] for r in args.runs]
for run, label in zip(args.runs, labels):
    ea = EventAccumulator(glob.glob(os.path.join(run, "events.out.tfevents.*"))[0], size_guidance={"scalars": 0})
    ea.Reload()
    for ax, (tag, _) in zip(axes.flat, PANELS):
        if tag in ea.Tags()["scalars"]:
            ev = ea.Scalars(tag)
            ax.plot([e.step for e in ev], [e.value for e in ev], lw=1.2, label=label)
for ax, (_, title) in zip(axes.flat, PANELS):
    ax.set_title(title)
    ax.set_xlabel("迭代")
    ax.grid(alpha=0.3)
# 图例放在整张图下方一行，不遮住任何曲线
handles, names = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, names, loc="lower center", ncol=len(names), frameon=False)
fig.tight_layout(rect=(0, 0.06, 1, 1))
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
fig.savefig(args.out)
print(f"[INFO] 已保存 {args.out}")
