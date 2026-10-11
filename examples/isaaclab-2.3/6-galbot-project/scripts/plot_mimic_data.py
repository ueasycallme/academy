# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.11（matplotlib、h5py，不需要 Isaac Sim）
# 验证日期：2026-10-11
"""画 6.4.7 的两张图：源示范与 Mimic 生成数据的对比（图 1）、BC-RNN 训练损失（图 2）。

图 1 左：每条示范开始时方块与放置垫的位置；右：TCP 在桌面上方的俯视轨迹。坐标都是机器人根坐标系（观测本来就是）。
图 2 从 robomimic 运行目录的 logs/log.txt 里读每个 epoch 的 Loss。

    python scripts/plot_mimic_data.py --source ./datasets/galbot_pick_place.hdf5 \
        --generated ./datasets/galbot_pick_place_generated.hdf5 \
        --train_log logs/robomimic/Galbot-PickPlace-IK-Rel-v0/<实验名>/<时间戳>/logs/log.txt --out_dir generated/mimic
"""

import argparse
import json
import os
import re

import h5py
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
parser.add_argument("--generated", required=True)
parser.add_argument("--train_log", required=True)
parser.add_argument("--out_dir", required=True)
args = parser.parse_args()

cjk = [f.name for f in font_manager.fontManager.ttflist if "Noto Sans CJK" in f.name]
if cjk:
    plt.rcParams["font.family"] = cjk[0]
plt.rcParams.update({"font.size": 14, "axes.titlesize": 14, "legend.fontsize": 13})


def load(path):
    """每条示范：(方块起点 xy, 放置垫 xy, TCP 轨迹 xy)，单位 cm。"""
    out = []
    with h5py.File(path, "r") as f:
        for name in f["data"]:
            obs = f["data"][name]["obs"]
            out.append((obs["object_position"][0, :2] * 100, obs["target_position"][0, :2] * 100, obs["eef_pos"][:, :2] * 100))
    return out


src, gen = load(args.source), load(args.generated)
os.makedirs(args.out_dir, exist_ok=True)

fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(11, 5.5), dpi=150)
for data, color, size, label in ((gen, "0.6", 10, f"生成 {len(gen)} 条"), (src, "C3", 40, f"源示范 {len(src)} 条")):
    ax0.scatter([d[0][0] for d in data], [d[0][1] for d in data], s=size, c=color, marker="o", label=f"方块（{label}）")
    ax0.scatter([d[1][0] for d in data], [d[1][1] for d in data], s=size, c=color, marker="s", label=f"放置垫（{label}）")
    for d in data:
        ax1.plot(d[2][:, 0], d[2][:, 1], c=color, lw=0.4 if color == "0.6" else 1.4, alpha=0.5 if color == "0.6" else 1.0)
ax0.set_title("每条示范开始时的位置")
ax1.set_title("TCP 轨迹（俯视）：灰为生成，红为源示范")
for ax in (ax0, ax1):
    ax.set_xlabel("x（cm，向前）")
    ax.set_ylabel("y（cm，向左）")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(alpha=0.3)
# 图例放在整张图下方，不压住任何点
fig.legend(*ax0.get_legend_handles_labels(), loc="lower center", ncol=4, frameon=False, fontsize=12)
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig(os.path.join(args.out_dir, "mimic_data.png"))

# robomimic 每个 epoch 打印 "Train Epoch N" 加一段 JSON
text = open(args.train_log, encoding="utf-8").read()
epochs, losses = [], []
for m in re.finditer(r"Train Epoch (\d+)\n(\{.*?\n\})", text, re.S):
    epochs.append(int(m.group(1)))
    losses.append(json.loads(m.group(2))["Loss"])
fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
ax.plot(epochs, losses, lw=1.0)
ax.set_xscale("log")
ax.set_xlabel("epoch（对数坐标；每个 epoch 100 个梯度步（gradient step））")
ax.set_ylabel("训练损失（负对数似然）")
ax.grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(os.path.join(args.out_dir, "bc_loss.png"))
print(f"[INFO] 源示范 {len(src)} 条，生成 {len(gen)} 条，训练 {len(epochs)} 个 epoch；图写到 {args.out_dir}")
