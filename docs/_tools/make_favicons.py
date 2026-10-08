# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
"""从 favicon.svg 的几何生成 PNG 图标（T-SITE-11）。

SVG 只由 4 个圆角矩形组成，这里用 Pillow 按同一组坐标绘制，8 倍超采样后缩小，得到抗锯齿的 PNG：
favicon-16.png、favicon-32.png、apple-touch-icon.png（180×180，按 iOS 惯例不透明、不加圆角）。
改了 favicon.svg 的坐标后，同步修改下面的 SHAPES 再运行::

    python docs/_tools/make_favicons.py      # 需要 Pillow
"""

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "_static" / "img" / "favicon"
GREEN, DARK, WHITE = (0x76, 0xB9, 0x00, 255), (0x00, 0x48, 0x31, 255), (255, 255, 255, 255)
# (x, y, w, h, rx, 颜色)，坐标系为 64×64，与 favicon.svg 一致
SHAPES = [(9, 41, 46, 12, 2.5, DARK), (17, 26, 30, 12, 2.5, WHITE), (25, 11, 14, 12, 2.5, DARK)]


def render(size: int, rounded: bool) -> Image.Image:
    ss = 8
    k = size * ss / 64
    img = Image.new("RGBA", (size * ss, size * ss), (0, 0, 0, 0) if rounded else GREEN)
    d = ImageDraw.Draw(img)
    if rounded:
        d.rounded_rectangle([0, 0, size * ss - 1, size * ss - 1], radius=14 * k, fill=GREEN)
    for x, y, w, h, rx, c in SHAPES:
        d.rounded_rectangle([x * k, y * k, (x + w) * k - 1, (y + h) * k - 1], radius=rx * k, fill=c)
    return img.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    for name, size, rounded in [("favicon-16.png", 16, True), ("favicon-32.png", 32, True), ("apple-touch-icon.png", 180, False)]:
        render(size, rounded).save(OUT / name)
        print(f"已保存 {OUT / name}")
