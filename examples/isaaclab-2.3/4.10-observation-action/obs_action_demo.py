# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""在官方 Cartpole 上改观测与动作：policy 组加噪声与 last_action，另建无噪声的 critic 组；可把动作项换成关节位置。

用法::

    python obs_action_demo.py --headless                         # 默认：力（effort）动作
    python obs_action_demo.py --headless --action position        # 换成关节位置动作，执行器刚度保持 0
    python obs_action_demo.py --headless --action position --kp 1000   # 同上，但给小车执行器设刚度
    python obs_action_demo.py --headless --no_noise               # 关闭 policy 组的噪声
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Observation / Action Manager 演示")
parser.add_argument("--num_envs", type=int, default=16, help="环境数量")
parser.add_argument("--action", choices=["effort", "position"], default="effort", help="小车的动作项")
parser.add_argument("--kp", type=float, default=0.0, help="position 模式下小车执行器的 stiffness（官方为 0）")
parser.add_argument("--no_noise", action="store_true", help="policy 组 enable_corruption=False")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.envs.mdp as mdp
from isaaclab.envs import ManagerBasedRLEnv
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.utils import configclass
from isaaclab.utils.noise import GaussianNoiseCfg
from isaaclab_tasks.manager_based.classic.cartpole.cartpole_env_cfg import CartpoleEnvCfg


@configclass
class CriticCfg(ObsGroup):
    """critic 组：与 policy 相同的关节量，但不加噪声。"""

    joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)
    joint_vel_rel = ObsTerm(func=mdp.joint_vel_rel)


@configclass
class MyCartpoleEnvCfg(CartpoleEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = args.num_envs
        # 观测：policy 组的关节位置加高斯噪声，末尾追加上一步动作
        policy = self.observations.policy
        policy.joint_pos_rel.noise = GaussianNoiseCfg(mean=0.0, std=0.05)
        policy.last_action = ObsTerm(func=mdp.last_action)
        policy.enable_corruption = not args.no_noise
        self.observations.critic = CriticCfg()
        # 动作：换成关节位置目标 = 0.5 × 原始动作 + 默认关节位置
        if args.action == "position":
            self.actions.joint_effort = None
            self.actions.cart_pos = mdp.JointPositionActionCfg(
                asset_name="robot", joint_names=["slider_to_cart"], scale=0.5, use_default_offset=True
            )
            self.scene.robot.actuators["cart_actuator"].stiffness = args.kp


def main() -> None:
    env = ManagerBasedRLEnv(cfg=MyCartpoleEnvCfg())
    print(f"观测空间 {env.single_observation_space}")
    print(f"各组的 Term 与维度 {env.observation_manager.active_terms} {env.observation_manager.group_obs_term_dim}")
    print(f"动作空间 {env.single_action_space}，动作项 {env.action_manager.active_terms}")

    obs, _ = env.reset()
    # 用固定动作 1.0 跑 1 秒（60 个环境步），看小车往哪走
    actions = torch.ones(env.num_envs, env.action_manager.total_action_dim, device=env.device)
    robot = env.scene["robot"]
    cart = robot.find_joints("slider_to_cart")[0][0]
    start = robot.data.joint_pos[0, cart].item()
    for _ in range(60):
        obs, *_ = env.step(actions)
    term = env.action_manager.get_term(env.action_manager.active_terms[0])
    print(f"原始动作 {term.raw_actions[0].tolist()} → 处理后 {term.processed_actions[0].tolist()}")
    print(f"env 0 小车位置 {start:.3f} → {robot.data.joint_pos[0, cart].item():.3f} m")

    diff = (obs["policy"][:, :2] - obs["critic"][:, :2]).abs().max().item()
    print(f"policy 组形状 {tuple(obs['policy'].shape)}，critic 组形状 {tuple(obs['critic'].shape)}")
    print(f"policy 与 critic 关节位置的最大差 {diff:.4f}（来自噪声）")
    print(f"policy 组最后一列（last_action）{obs['policy'][0, -1].item():.3f}")

    env.close()  # 环境的 close() 会释放 SimulationContext


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
