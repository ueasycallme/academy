# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：tensorboard 2.21 + matplotlib 3.10（Isaac Sim 5.1.0 的 Python 自带）
# 验证日期：2026-10-08（--preset base_vel 为 6.4.5 所加，验证日期 2026-10-11）
"""从 rsl_rl 训练日志（TensorBoard 事件文件）画出 reach 的几条关键曲线（6.5.1）。不需要启动 Isaac Sim。

    python scripts/plot_training.py logs/rsl_rl/galbot_reach/<运行 1> [<运行 2> …] --out generated/train/reach_curves.png
    python scripts/plot_training.py logs/rsl_rl/galbot_base_vel/<运行> --preset base_vel --out base_vel_curves.png   # 6.4.5
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
    ("Train/mean_reward", "Mean reward（每回合）"),
    ("Metrics/ee_pose/position_error", "TCP 位置误差（m）"),
    ("Metrics/ee_pose/orientation_error", "TCP 姿态误差（rad）"),
    ("Policy/mean_noise_std", "动作噪声标准差"),
]

parser = argparse.ArgumentParser()
parser.add_argument("runs", nargs="+", help="运行目录（含 events.out.tfevents.*）")
parser.add_argument("--out", required=True)
parser.add_argument("--preset", choices=["reach", "base_vel"], default="reach", help="base_vel：底盘速度跟踪的曲线（6.4.5）")
args = parser.parse_args()
if args.preset == "base_vel":
    PANELS = [
        ("Train/mean_reward", "Mean reward（每回合）"),
        ("Metrics/base_velocity/error_vel_xy", "线速度误差（m/s）"),
        ("Metrics/base_velocity/error_vel_yaw", "角速度误差（rad/s）"),
        ("Episode_Termination/tipped", "倾覆终止的比例"),
    ]

cjk = [f.name for f in font_manager.fontManager.ttflist if "Noto Sans CJK" in f.name]
if cjk:
    plt.rcParams["font.family"] = cjk[0]
plt.rcParams.update({"font.size": 13, "axes.titlesize": 13, "legend.fontsize": 12})

fig, axes = plt.subplots(2, 2, figsize=(10, 6.4), dpi=150)
for run in args.runs:
    ev = sorted(glob.glob(os.path.join(run, "events.out.tfevents.*")))[-1]
    ea = EventAccumulator(ev, size_guidance={"scalars": 0})
    ea.Reload()
    label = "_".join(os.path.basename(os.path.normpath(run)).split("_")[2:])  # 时间戳之后的 run_name
    for ax, (tag, title) in zip(axes.flat, PANELS):
        pts = ea.Scalars(tag)
        ax.plot([p.step for p in pts], [p.value for p in pts], label=label, linewidth=1.4)
for ax, (_, title) in zip(axes.flat, PANELS):
    ax.set_title(title)
    ax.set_xlabel("迭代")
    ax.grid(alpha=0.3)
axes.flat[0].legend(loc="lower right")
fig.tight_layout()
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
fig.savefig(args.out)
print(f"已保存 {args.out}")
