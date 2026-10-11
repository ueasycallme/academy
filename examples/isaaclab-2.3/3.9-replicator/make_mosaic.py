# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：matplotlib 3.10（Isaac Sim 5.1.0 的 Python 自带）
# 验证日期：2026-10-11
"""把 synth_data.py 的输出拼成 2×2 图（3.9）：第 a 帧的 RGB、分割、带 2D 框的 RGB，以及第 b 帧的 RGB。不需要 Isaac Sim。

    python make_mosaic.py /tmp/synth --out mosaic.png --a 0 --b 100
"""

import argparse
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Rectangle

parser = argparse.ArgumentParser()
parser.add_argument("out_dir")
parser.add_argument("--out", required=True)
parser.add_argument("--a", type=int, default=0)
parser.add_argument("--b", type=int, default=100)
args = parser.parse_args()

cjk = [f.name for f in font_manager.fontManager.ttflist if "Noto Sans CJK" in f.name]
if cjk:
    plt.rcParams["font.family"] = cjk[0]
plt.rcParams.update({"font.size": 14})


def path(kind: str, i: int, ext: str) -> str:
    return os.path.join(args.out_dir, f"{kind}_{i:04d}.{ext}")


rgb_a = plt.imread(path("rgb", args.a, "png"))
seg_a = plt.imread(path("semantic_segmentation", args.a, "png"))
rgb_b = plt.imread(path("rgb", args.b, "png"))
boxes = np.load(path("bounding_box_2d_tight", args.a, "npy"))
labels = json.load(open(path("bounding_box_2d_tight_labels", args.a, "json")))

fig, ax = plt.subplots(2, 2, figsize=(10, 7.8), dpi=120)
ax[0, 0].imshow(rgb_a)
ax[0, 0].set_title(f"第 {args.a} 帧：RGB")
ax[0, 1].imshow(seg_a)
ax[0, 1].set_title(f"第 {args.a} 帧：语义分割（着色）")
ax[1, 0].imshow(rgb_a)
for b in boxes:
    ax[1, 0].add_patch(Rectangle((b["x_min"], b["y_min"]), b["x_max"] - b["x_min"], b["y_max"] - b["y_min"],
                                 fill=False, edgecolor="yellow", linewidth=2))
    ax[1, 0].text(b["x_min"], b["y_min"] - 4, labels[str(b["semanticId"])]["class"], color="yellow", fontsize=13)
ax[1, 0].set_title(f"第 {args.a} 帧：2D 框（{len(boxes)} 个）")
ax[1, 1].imshow(rgb_b)
ax[1, 1].set_title(f"第 {args.b} 帧：RGB（另一组随机化）")
for a in ax.flat:
    a.set_xticks([])
    a.set_yticks([])
fig.tight_layout()
fig.savefig(args.out)
print(f"已保存 {args.out}")
