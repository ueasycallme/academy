# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.11（matplotlib、Pillow，不需要 Isaac Sim）
# 验证日期：2026-10-09
"""把 check_sensors.py 保存的腕部相机 RGB 与深度图并排画成一张图（6.2.2 图 1）。

    python scripts/plot_wrist_camera.py --in_dir generated/sensors --out generated/sensors/wrist_camera.png

标注位置（方块、夹爪、地面）按默认姿态、128×128 的画面写死；换了姿态或分辨率要相应调整。
"""

import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("--in_dir", default="generated/sensors", help="check_sensors.py 的 --out 目录")
parser.add_argument("--out", default="generated/sensors/wrist_camera.png")
args = parser.parse_args()

cjk = [f.name for f in font_manager.fontManager.ttflist if "Noto Sans CJK" in f.name]
if cjk:
    plt.rcParams["font.family"] = cjk[0]
plt.rcParams.update({"font.size": 15})  # 图宽 1100 像素，页面上缩放后文字约 17–20 px（D-025 要求 ≥ 12 px）

fig, ax = plt.subplots(1, 2, figsize=(10, 5.4), dpi=110)
for a, name, title in zip(ax, ["wrist_rgb.png", "wrist_depth.png"], ["RGB", "深度（近黑远白）"]):
    a.imshow(Image.open(os.path.join(args.in_dir, name)), interpolation="nearest", cmap="gray")
    a.set_title(title)
    a.set_xticks([0, 64, 127])
    a.set_yticks([0, 64, 127])
ax[0].annotate("方块", xy=(75, 73), xytext=(95, 105), fontsize=15, arrowprops=dict(arrowstyle="->"))
ax[0].annotate("夹爪", xy=(22, 75), xytext=(10, 112), fontsize=15, arrowprops=dict(arrowstyle="->"))
ax[0].annotate("地面", xy=(95, 30), xytext=(92, 8), color="white", fontsize=15)
fig.tight_layout()
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
fig.savefig(args.out)
print(f"[INFO] 已保存 {args.out}")
