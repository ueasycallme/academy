# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""在官方 Cartpole 上演示三种事件时机：startup 随机化质量、reset 随机化初始关节位置、interval 定时触发。

用法::

    python event_demo.py --headless                   # 回合 5 s，interval 间隔 1–2 s
    python event_demo.py --headless --episode_s 1.0   # 回合 1 s，比 interval 间隔短
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Event Manager 演示")
parser.add_argument("--num_envs", type=int, default=8, help="环境数量")
parser.add_argument("--episode_s", type=float, default=5.0, help="episode_length_s")
parser.add_argument("--seed", type=int, default=42, help="随机种子")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.envs.mdp as mdp
from isaaclab.envs import ManagerBasedRLEnv
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils import configclass
from isaaclab_tasks.manager_based.classic.cartpole.cartpole_env_cfg import CartpoleEnvCfg

CALLS: dict[str, torch.Tensor] = {}


def count_calls(env: ManagerBasedRLEnv, env_ids: torch.Tensor | None, key: str):
    """自定义事件：只记录每个环境被调用的次数。env_ids 为 None 表示所有环境。"""
    if key not in CALLS:
        CALLS[key] = torch.zeros(env.num_envs, dtype=torch.long, device=env.device)
    if env_ids is None:
        CALLS[key] += 1
    else:
        CALLS[key][env_ids] += 1


@configclass
class MyCartpoleEnvCfg(CartpoleEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = args.num_envs
        self.seed = args.seed
        self.episode_length_s = args.episode_s
        # startup：小车与摆杆的质量各乘 [0.5, 1.5] 内的随机数，只在启动时做一次
        self.events.randomize_mass = EventTerm(
            func=mdp.randomize_rigid_body_mass,
            mode="startup",
            params={
                "asset_cfg": SceneEntityCfg("robot", body_names=["cart", "pole"]),
                "mass_distribution_params": (0.5, 1.5),
                "operation": "scale",
            },
        )
        # reset：官方配置已有 reset_cart_position / reset_pole_position（在默认位置上加随机偏移）
        # interval：每 1–2 s 触发一次，分别用逐环境计时与全局计时
        self.events.tick_per_env = EventTerm(
            func=count_calls, mode="interval", interval_range_s=(1.0, 2.0), params={"key": "per_env"}
        )
        self.events.tick_global = EventTerm(
            func=count_calls, mode="interval", interval_range_s=(1.0, 2.0), is_global_time=True, params={"key": "global"}
        )


def main() -> None:
    env = ManagerBasedRLEnv(cfg=MyCartpoleEnvCfg())
    robot = env.scene["robot"]
    body_ids = [robot.body_names.index(n) for n in ("cart", "pole")]
    masses = robot.root_physx_view.get_masses()[:, body_ids]
    print(f"默认质量 cart / pole：{robot.data.default_mass[0, body_ids].tolist()} kg")
    print("startup 之后各环境的质量（kg）：")
    for i in range(4):
        print(f"  env {i}: cart {masses[i, 0]:.3f}  pole {masses[i, 1]:.3f}")

    env.reset()
    print("reset 之后各环境的初始关节位置（slider_to_cart m，cart_to_pole rad）：")
    for i in range(4):
        print(f"  env {i}: {robot.data.joint_pos[i, 0]: .3f}  {robot.data.joint_pos[i, 1]: .3f}")

    actions = torch.zeros(env.num_envs, env.action_manager.total_action_dim, device=env.device)
    steps = 300  # 5 s
    resets = 0
    for _ in range(steps):
        _, _, terminated, truncated, _ = env.step(actions)
        resets += int((terminated | truncated).sum())
    masses_after = robot.root_physx_view.get_masses()[:, body_ids]
    print(f"运行 {steps} 步（5 s），期间重置 {resets} 次；质量是否改变：{not torch.equal(masses, masses_after)}")
    zeros = torch.zeros(env.num_envs, dtype=torch.long)  # 从未触发时 CALLS 里没有这一项
    print(f"interval 触发次数，逐环境计时：{CALLS.get('per_env', zeros).tolist()}")
    print(f"interval 触发次数，全局计时：  {CALLS.get('global', zeros).tolist()}")

    env.close()  # 环境的 close() 会释放 SimulationContext


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
