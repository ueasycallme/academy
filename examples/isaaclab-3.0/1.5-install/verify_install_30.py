# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab 3.0.0-EA（tag v3.0.0-EA，commit ae37b028e）；Isaac Sim 6.1.0.0（pip，可选）
# 验证日期：2026-10-09
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04；主机内存 16 GB
"""检查 3.0 EA 环境是否装好：Python、PyTorch、Warp、Newton、Isaac Lab，以及（可选的）Isaac Sim。

只做导入与版本检查，不启动仿真、不占 GPU 计算；仿真验证用官方命令
``isaaclab train --rl_library rsl_rl --task Isaac-Cartpole-Direct physics=newton_mjwarp``。
每项检查打印一行 ``[PASS]`` / ``[FAIL]`` / ``[SKIP]``，最后一行是汇总。用法::

    uv run python verify_install_30.py                     # 路线 A（在 Isaac Lab 仓库根目录运行）
    python verify_install_30.py                            # 路线 B / C（先激活环境）
    python verify_install_30.py --require-isaacsim         # 要求装了 Isaac Sim 6.1（路线 A 加 isaacsim extra、路线 B）
"""

from __future__ import annotations

import argparse
import importlib.metadata as md
import importlib.util
import os
import sys

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("--require-isaacsim", action="store_true", help="没有 isaacsim 包时判为失败（默认只提示）")
args = parser.parse_args()

results: list[tuple[str, str, str]] = []


def check(name: str, status: str, detail: str) -> None:
    results.append((name, status, detail))
    print(f"[{status}] {name}: {detail}", flush=True)


def version(dist: str) -> str | None:
    try:
        return md.version(dist)
    except md.PackageNotFoundError:
        return None


# 1. Python：3.0 EA 要求 3.12（pyproject.toml 的 requires-python = ">=3.12,<3.13"）
check("python", "PASS" if sys.version_info[:2] == (3, 12) else "FAIL", f"{sys.version.split()[0]} ({sys.prefix})")

# 2. PyTorch 与 CUDA
torch_ver = version("torch")
if torch_ver is None:
    check("torch", "FAIL", "not installed")
else:
    import torch

    cuda = torch.cuda.is_available()
    check("torch", "PASS" if cuda else "FAIL", f"{torch_ver}, cuda={cuda}" + (f", {torch.cuda.get_device_name(0)}" if cuda else ""))

# 3. Warp 与 Newton（Kit-less 训练的物理后端）
for dist in ("warp-lang", "newton"):
    v = version(dist)
    check(dist, "PASS" if v else "FAIL", v or "not installed")

# 4. Isaac Lab：版本，以及导入路径指向仓库源码（editable 安装后仓库不能移动）
for dist in ("isaaclab", "isaaclab_tasks", "isaaclab_rl", "isaaclab_newton"):
    v = version(dist)
    check(dist, "PASS" if v else "FAIL", v or "not installed")
spec = importlib.util.find_spec("isaaclab")
src = os.path.dirname(spec.origin) if spec and spec.origin and os.path.isfile(spec.origin) else None
check("isaaclab import path", "PASS" if src else "FAIL", src or "namespace package or missing: editable path broken?")

# 5. Isaac Sim（可选）：路线 C 不装它
sim = version("isaacsim")
if sim:
    check("isaacsim", "PASS" if sim.startswith("6.1") else "FAIL", sim)
else:
    check("isaacsim", "FAIL" if args.require_isaacsim else "SKIP", "not installed (Kit-less environment)")

failed = sum(1 for _, s, _ in results if s == "FAIL")
counted = [r for r in results if r[1] != "SKIP"]
print(f"SUMMARY: {len(counted) - failed}/{len(counted)} passed" + (f", {len(results) - len(counted)} skipped" if len(results) > len(counted) else ""))
sys.exit(1 if failed else 0)
