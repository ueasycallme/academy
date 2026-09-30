# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""统计官方任务中各 RL 库的支持情况：看每个 Isaac-* 任务 ID 注册时是否带 <库>_cfg_entry_point。

用法::

    python count_rl_support.py --headless
"""

import argparse
import collections
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="统计官方任务对各 RL 库的支持")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym

import isaaclab_tasks  # noqa: F401  注册官方任务

LIBS = ("rsl_rl", "skrl", "rl_games", "sb3")


def main() -> None:
    specs = [s for s in gym.registry.values() if s.id.startswith("Isaac-")]
    for label, group in (("全部", specs), ("不含 -Play", [s for s in specs if "Play" not in s.id])):
        count = collections.Counter(k for s in group for k in LIBS if f"{k}_cfg_entry_point" in s.kwargs)
        none = sum(not any(f"{k}_cfg_entry_point" in s.kwargs for k in LIBS) for s in group)
        print(f"{label}：{len(group)} 个任务 ID；" + "，".join(f"{k} {count[k]}" for k in LIBS) + f"；四者都没有 {none}")


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
