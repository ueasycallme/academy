# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""configclass 的几个行为，以及 Cartpole 环境配置的嵌套结构。只操作配置，不创建仿真。

isaaclab.utils 会导入 pxr，所以仍要先用 AppLauncher 启动 Kit（headless）。

用法::

    python configclass_demo.py --headless
"""

import argparse
import sys
from dataclasses import MISSING

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="configclass 演示")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

from isaaclab.utils import configclass
from isaaclab_tasks.manager_based.classic.cartpole.cartpole_env_cfg import CartpoleEnvCfg


@configclass
class DemoCfg:
    gains: list = [1.0, 2.0]  # 可变默认值：原生 dataclass 会报错，configclass 允许，且每个实例各有一份
    name: str = MISSING  # 必须由使用者填写

    def __post_init__(self):
        print("  用户的 __post_init__ 先执行")


def print_tree(cfg, depth: int = 0, max_depth: int = 2) -> None:
    """打印一个 configclass 实例中嵌套的 configclass 字段。"""
    for key, value in cfg.__dict__.items():
        if hasattr(value, "to_dict") and not callable(value):
            print(f"{'  ' * depth}{key}: {type(value).__name__}")
            if depth < max_depth:
                print_tree(value, depth + 1, max_depth)


def main() -> None:
    print("== 可变默认值 ==")
    a, b = DemoCfg(name="a"), DemoCfg(name="b")
    a.gains.append(3.0)
    print(f"a.gains = {a.gains}, b.gains = {b.gains}")

    print("== replace / to_dict ==")
    c = a.replace(name="c")
    print(f"c.name = {c.name}, a.name = {a.name}, c.to_dict() = {c.to_dict()}")

    print("== MISSING 与 validate ==")
    d = DemoCfg()  # 实例化时不报错
    try:
        d.validate()
    except Exception as e:  # noqa: BLE001
        print(f"{type(e).__name__}: {e}")

    print("== Cartpole 环境配置的嵌套结构（前三层）==")
    env_cfg = CartpoleEnvCfg()
    print(f"decimation = {env_cfg.decimation}, sim.dt = {env_cfg.sim.dt}, scene.num_envs = {env_cfg.scene.num_envs}")
    print_tree(env_cfg)

    print("== 实例化之后再覆盖（Hydra 命令行覆盖走的也是 from_dict）==")
    env_cfg.from_dict({"decimation": 4})
    print(f"decimation = {env_cfg.decimation}, sim.render_interval = {env_cfg.sim.render_interval}")


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
