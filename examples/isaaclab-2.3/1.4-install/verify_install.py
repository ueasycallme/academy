# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""检查主线环境是否装好：Python、Isaac Sim、PyTorch、Isaac Lab，最后 headless 启动一次仿真。

每项检查打印一行 ``[PASS]`` 或 ``[FAIL]``，最后一行是汇总。用法::

    python verify_install.py            # 默认 headless
"""

from __future__ import annotations

import importlib.metadata as md
import sys

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str) -> None:
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}", flush=True)


# 1. Python 版本：Isaac Sim 5.x 要求 3.11
check("python", sys.version_info[:2] == (3, 11), sys.version.split()[0])

# 2. Isaac Sim pip 包版本
try:
    sim_ver = md.version("isaacsim")
    check("isaacsim", sim_ver.startswith("5.1.0"), sim_ver)
except md.PackageNotFoundError:
    check("isaacsim", False, "not installed")

# 3. Isaac Lab 各包（editable 安装后应能查到版本，且导入路径指向仓库源码）
for pkg in ("isaaclab", "isaaclab_tasks", "isaaclab_rl"):
    try:
        check(pkg, True, md.version(pkg))
    except md.PackageNotFoundError:
        check(pkg, False, "not installed")

# 4. isaaclab 的导入路径必须指向真实存在的源码目录。
#    editable 安装后若移动了 Isaac Lab 仓库，dist-info 仍在（上面的版本检查会通过），
#    但 import isaaclab 只能得到一个空的命名空间包，isaaclab.app 找不到。
#    这里在启动 Kit 之前检查，失败时直接汇总退出，而不是抛 ModuleNotFoundError。
import importlib.util  # noqa: E402
import os  # noqa: E402


def _isaaclab_source_dir() -> str | None:
    spec = importlib.util.find_spec("isaaclab")
    if spec is None:
        return None
    if spec.origin and os.path.isfile(spec.origin):
        return os.path.dirname(spec.origin)
    return None  # 命名空间包：没有 __init__.py，说明 editable 路径已失效


src_dir = _isaaclab_source_dir()
app_ok = src_dir is not None and importlib.util.find_spec("isaaclab.app") is not None
check(
    "isaaclab import path",
    app_ok,
    src_dir if app_ok else "isaaclab 不是一个有效的包（常见原因：editable 安装后移动了 Isaac Lab 仓库；在新位置重新运行 ./isaaclab.sh --install）",
)


def summarize() -> int:
    failed = [n for n, ok, _ in results if not ok]
    summary = f"SUMMARY: {len(results) - len(failed)}/{len(results)} passed"
    print(summary + (f"; failed: {', '.join(failed)}" if failed else ""), flush=True)
    return 1 if failed else 0


if not app_ok:
    sys.exit(summarize())

# 5. 启动 Kit（headless），之后才能导入依赖 Isaac Sim 扩展的模块
from isaaclab.app import AppLauncher  # noqa: E402

app_launcher = AppLauncher(headless=True)
simulation_app = app_launcher.app

import torch  # noqa: E402

import isaaclab.sim as sim_utils  # noqa: E402


def main() -> None:
    """Kit 启动后的检查。

    结束前必须显式释放 SimulationContext（clear_all_callbacks + clear_instance），
    否则 simulation_app.close() 不会返回（本站实测：进程卡在 close() 且 CPU 占满）。
    Isaac Lab 的 ManagerBasedEnv.close() 也是这样做的（v2.3.2 manager_based_env.py L543–L544）。
    """
    check(
        "torch",
        torch.cuda.is_available(),
        f"{torch.__version__}, cuda={torch.version.cuda}, "
        f"device={torch.cuda.get_device_name(0) if torch.cuda.is_available() else '-'}",
    )
    # 6. 创建仿真上下文并步进 100 次
    try:
        sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=0.01, device="cuda:0"))
        sim_utils.GroundPlaneCfg().func("/World/ground", sim_utils.GroundPlaneCfg())
        sim.reset()
        for _ in range(100):
            sim.step()
        check("simulation", True, f"stepped 100 x dt={sim.get_physics_dt()}")
        # 释放仿真上下文，保证 simulation_app.close() 能正常退出
        sim.clear_all_callbacks()
        sim.clear_instance()
    except Exception as exc:  # noqa: BLE001
        check("simulation", False, repr(exc))



if __name__ == "__main__":
    main()
    code = summarize()
    simulation_app.close()
    sys.exit(code)
