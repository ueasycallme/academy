# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""继承官方 Cartpole 配置，改一处权重并加一个自定义奖励 Term，用随机动作跑 100 步，打印各 Manager 的信息。

用法::

    python custom_cartpole.py --headless --num_envs 16
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="自定义 Cartpole 任务")
parser.add_argument("--num_envs", type=int, default=16, help="环境数量")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

from isaaclab.assets import Articulation
from isaaclab.envs import ManagerBasedRLEnv
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils import configclass
from isaaclab_tasks.manager_based.classic.cartpole.cartpole_env_cfg import CartpoleEnvCfg


def cart_distance_from_center(env: ManagerBasedRLEnv, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    """自定义奖励 Term：小车离轨道中心的距离，形状 (num_envs,)。"""
    asset: Articulation = env.scene[asset_cfg.name]
    return torch.abs(asset.data.joint_pos[:, asset_cfg.joint_ids]).sum(dim=1)


@configclass
class MyCartpoleEnvCfg(CartpoleEnvCfg):
    def __post_init__(self):
        super().__post_init__()  # 先让父类完成它的设置
        self.scene.num_envs = args.num_envs
        self.rewards.pole_pos.weight = -2.0  # 改一处：加大摆杆偏离的惩罚
        self.rewards.cart_center = RewTerm(  # 加一处：鼓励小车待在中间
            func=cart_distance_from_center,
            weight=-0.1,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=["slider_to_cart"])},
        )


def main() -> None:
    env = ManagerBasedRLEnv(cfg=MyCartpoleEnvCfg())
    print(f"动作维度 {env.action_manager.total_action_dim}，观测组 {env.observation_manager.group_obs_dim}")
    print(f"奖励 Term：{env.reward_manager.active_terms}")

    obs, _ = env.reset()
    for _ in range(100):
        actions = 2.0 * torch.rand(env.num_envs, env.action_manager.total_action_dim, device=env.device) - 1.0
        obs, rew, terminated, truncated, extras = env.step(actions)

    print(f"obs['policy'] 形状 {tuple(obs['policy'].shape)}，reward 形状 {tuple(rew.shape)}")
    print("环境 0 本步的各奖励项（func × weight，未乘 dt；计入总奖励时再乘 dt）：")
    for name, value in env.reward_manager.get_active_iterable_terms(0):
        print(f"  {name:14s} {value[0]: .5f}")
    print(f"本步终止 {int(terminated.sum())} 个，超时 {int(truncated.sum())} 个")

    env.close()  # 环境的 close() 会释放 SimulationContext


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
