# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.11（不依赖 Isaac Sim）
# 验证日期：2026-10-11
"""生成资产的清单（6.1.7）：generated/<变体>/MANIFEST.json。

清单回答"手里这份 USD 是怎么来的"：
- source：描述仓库地址、实际检出的 commit、工作区是否有未提交的改动；
- toolchain：生成时的 Isaac Sim、Isaac Lab（pip 包版本）与 Python 版本；
- params：assets/conversion.py 里的全部生成参数（转换器选项、驱动增益、转换后的修改）；
- files：输出目录下每个文件的 sha256 与大小（config.yaml 除外：转换器每次都把生成时间写进去）。

verify_manifest 用"现在的"来源、工具链、代码参数、文件，逐项和清单比，返回差异列表；空列表表示一致。
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import warnings
from datetime import datetime
from pathlib import Path

from .conversion import conversion_params, variant_dir_name
from .paths import GALBOT_COMMIT, GALBOT_REPO_URL, galbot_description_dir, generated_asset_dir

MANIFEST_NAME = "MANIFEST.json"
SKIP_FILES = {MANIFEST_NAME, "config.yaml"}  # config.yaml 带生成时间与绝对路径，每次转换都不同


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(repo: Path, *cmd: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(repo), *cmd], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def source_info() -> dict:
    repo = galbot_description_dir()
    status = _git(repo, "status", "--porcelain")
    return {"repo": GALBOT_REPO_URL, "commit": _git(repo, "rev-parse", "HEAD"), "pinned_commit": GALBOT_COMMIT,
            "dirty": None if status is None else bool(status)}


def toolchain_info() -> dict:
    from importlib.metadata import PackageNotFoundError, version

    out = {"python": platform.python_version()}
    for pkg in ("isaacsim", "isaaclab"):  # isaaclab 的 pip 包版本号与发布号不同：Isaac Lab 2.3.2 对应 0.54.2
        try:
            out[pkg] = version(pkg)
        except PackageNotFoundError:
            out[pkg] = None
    return out


def file_table(out_dir: Path) -> dict:
    return {
        p.relative_to(out_dir).as_posix(): {"sha256": _sha256(p), "size": p.stat().st_size}
        for p in sorted(out_dir.rglob("*"))
        if p.is_file() and p.name not in SKIP_FILES
    }


def write_manifest(variant: str, floating_base: bool) -> Path:
    """转换完成后调用：把来源、工具链、参数与输出文件的指纹写进 MANIFEST.json。"""
    out_dir = generated_asset_dir() / variant_dir_name(variant, floating_base)
    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": source_info(),
        "toolchain": toolchain_info(),
        "params": conversion_params(variant, floating_base),
        "files": file_table(out_dir),
    }
    path = out_dir / MANIFEST_NAME
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return path


def _diff(a, b, prefix: str = "") -> list[str]:
    """两个 JSON 值的差异，按"键路径：清单 → 现在"列出。"""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            out += _diff(a.get(k, "<无>"), b.get(k, "<无>"), f"{prefix}.{k}" if prefix else str(k))
        return out
    return [] if a == b else [f"{prefix}：{json.dumps(a, ensure_ascii=False)} → {json.dumps(b, ensure_ascii=False)}"]


def verify_manifest(variant: str = "fixed_base", floating_base: bool = False, check_files: bool = True) -> list[str]:
    """返回差异列表（空表示一致）。分四类：来源、工具链、参数、文件。"""
    out_dir = generated_asset_dir() / variant_dir_name(variant, floating_base)
    path = out_dir / MANIFEST_NAME
    if not path.is_file():
        return [f"没有清单 {path}：用 scripts/convert_galbot.py 重新生成，或 scripts/asset_manifest.py write 补写"]
    recorded = json.loads(path.read_text())
    diffs = [f"来源 {d}" for d in _diff(recorded["source"], source_info())]
    tool = toolchain_info()
    if tool["isaacsim"] is not None:  # 在没装 Isaac Sim 的 Python 里校验时，不比工具链（只比来源、参数、文件）
        diffs += [f"工具链 {d}" for d in _diff(recorded["toolchain"], tool)]
    diffs += [f"参数 {d}" for d in _diff(recorded["params"], json.loads(json.dumps(conversion_params(variant, floating_base))))]
    if check_files:
        now = file_table(out_dir)
        for name in sorted(set(recorded["files"]) | set(now)):
            r, n = recorded["files"].get(name), now.get(name)
            if r is None:
                diffs.append(f"文件 {name}：清单里没有（多出来的）")
            elif n is None:
                diffs.append(f"文件 {name}：缺失")
            elif r != n:
                diffs.append(f"文件 {name}：sha256 {r['sha256'][:12]} → {n['sha256'][:12]}，大小 {r['size']} → {n['size']}")
    return diffs


def warn_if_stale(variant: str = "fixed_base", floating_base: bool = False) -> None:
    """环境启动时调用：清单不一致只发警告，不中断（找不到描述仓库等错误也只警告）。"""
    try:
        diffs = verify_manifest(variant, floating_base)
    except Exception as e:  # noqa: BLE001  校验本身出错也不应挡住训练
        warnings.warn(f"[资产清单] 校验失败：{e}", stacklevel=2)
        return
    if diffs:
        shown = "\n  ".join(diffs[:8]) + (f"\n  …共 {len(diffs)} 项" if len(diffs) > 8 else "")
        warnings.warn(f"[资产清单] {variant_dir_name(variant, floating_base)} 与清单不一致（6.1.7）：\n  {shown}", stacklevel=2)
