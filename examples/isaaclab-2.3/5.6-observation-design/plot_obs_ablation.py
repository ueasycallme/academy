# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-08
"""读 5.6 四组 Cartpole 训练的 TensorBoard 记录，打印关键迭代的数值并画对照曲线。

    python plot_obs_ablation.py <IsaacLab>/logs/rsl_rl/cartpole --out obs_ablation.png
"""

import argparse
import glob
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator  # noqa: E402

RUNS = [  # 运行名后缀 → 图例
    ("obs56_base", "基线：位置 + 速度"),
    ("obs56_novel", "去掉速度"),
    ("obs56_novel_h3", "去掉速度 + 3 帧历史"),
    ("obs56_base_h3", "基线 + 3 帧历史"),
]
PANELS = [("Train/mean_reward", "每回合平均回报"), ("Train/mean_episode_length", "平均回合长度（步，上限 300）")]

parser = argparse.ArgumentParser()
parser.add_argument("log_root", help="logs/rsl_rl/cartpole 目录")
parser.add_argument("--out", required=True)
args = parser.parse_args()

cjk = [f.name for f in font_manager.fontManager.ttflist if "Noto Sans CJK" in f.name]
if cjk:
    plt.rcParams["font.family"] = cjk[0]
plt.rcParams.update({"font.size": 13, "axes.titlesize": 13, "legend.fontsize": 12})

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), dpi=150)
for suffix, label in RUNS:
    run = sorted(d for d in glob.glob(os.path.join(args.log_root, f"*_{suffix}")) if d.endswith(suffix))[-1]
    ea = EventAccumulator(sorted(glob.glob(os.path.join(run, "events.out.tfevents.*")))[-1], size_guidance={"scalars": 0})
    ea.Reload()
    cells = []
    for ax, (tag, _) in zip(axes, PANELS):
        pts = ea.Scalars(tag)
        steps, vals = [p.step for p in pts], [p.value for p in pts]
        ax.plot(steps, vals, label=label, linewidth=1.4)
        by_step = dict(zip(steps, vals))
        last10 = vals[-10:]
        cells.append(f"{tag.split('/')[-1]}: 第 50 次 {by_step.get(50, float('nan')):.1f}，第 100 次 {by_step.get(100, float('nan')):.1f}，"
                     f"最后 10 次平均 {sum(last10) / len(last10):.1f}")
    print(f"{label:22s} | " + " | ".join(cells))
for ax, (_, title) in zip(axes, PANELS):
    ax.set_title(title)
    ax.set_xlabel("迭代")
    ax.grid(alpha=0.3)
axes[0].legend(loc="lower right")
fig.tight_layout()
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
fig.savefig(args.out)
print(f"已保存 {args.out}")
