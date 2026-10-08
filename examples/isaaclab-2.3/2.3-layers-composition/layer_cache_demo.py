# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：usd-core 26.08（不需要 Isaac Sim）
# 验证日期：2026-10-08
"""2.3 常见坑一：被引用的文件在磁盘上改了，但只要还有打开的 Stage 持有这个 Layer，重新打开 Stage 仍读到旧值。"""

import tempfile
from pathlib import Path

from pxr import Sdf, Usd

ASSET = '#usda 1.0\n(\n    defaultPrim = "Part"\n)\n\ndef Xform "Part"\n{\n    float mass = {mass}\n}\n'
SCENE = '#usda 1.0\n\ndef Xform "Robot" (\n    prepend references = @./asset.usda@\n)\n{\n}\n'


def mass_of(stage: Usd.Stage) -> float:
    return stage.GetPrimAtPath("/Robot").GetAttribute("mass").Get()


with tempfile.TemporaryDirectory() as d:
    asset, scene = Path(d) / "asset.usda", Path(d) / "scene.usda"
    asset.write_text(ASSET.replace("{mass}", "1.0"))
    scene.write_text(SCENE)

    first = Usd.Stage.Open(str(scene))  # 一直开着，相当于 Isaac Sim 里的当前 Stage
    print(f"第一次打开：mass = {mass_of(first)}")

    asset.write_text(ASSET.replace("{mass}", "9.0"))  # 在磁盘上改被引用的文件
    print(f"改文件后，第一个 Stage 还开着，重新打开：mass = {mass_of(Usd.Stage.Open(str(scene)))}")

    Sdf.Layer.Find(str(asset)).Reload()
    print(f"对该 Layer 调用 Reload() 后：mass = {mass_of(Usd.Stage.Open(str(scene)))}")

    asset.write_text(ASSET.replace("{mass}", "5.0"))
    del first  # 没有 Stage 再持有这些 Layer，它们随之释放
    print(f"再改成 5.0，并关掉所有 Stage 后重新打开：mass = {mass_of(Usd.Stage.Open(str(scene)))}")
