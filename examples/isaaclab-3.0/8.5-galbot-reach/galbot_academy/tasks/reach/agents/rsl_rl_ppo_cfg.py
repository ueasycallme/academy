# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""Galbot reach 的 PPO 配置（6.5.1）：照搬 Isaac-Reach-Franka-v0 的 FrankaReachPPORunnerCfg（isaaclab_tasks v2.3.2），
只改实验名。两个任务的观测、动作维数相近（Franka 观测 32 维、Galbot 28 维，动作都是 7 维），控制周期都是 1/30 s。

3.0 EA 版（8.5）：rsl_rl 升到 5.x，网络配置从一个 policy（RslRlPpoActorCriticCfg，已弃用）拆成 actor 与 critic 两个
RslRlMLPModelCfg，写法照 3.0 的 FrankaReachPPORunnerCfg；数值与 2.3 版相同。
"""

from isaaclab.utils import configclass

from isaaclab_rl.rsl_rl import RslRlMLPModelCfg, RslRlOnPolicyRunnerCfg, RslRlPpoAlgorithmCfg


@configclass
class GalbotReachPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 24  # 每次迭代每个环境采 24 个控制步
    max_iterations = 1000
    save_interval = 50
    experiment_name = "galbot_reach"
    run_name = ""
    actor = RslRlMLPModelCfg(
        hidden_dims=[64, 64],
        activation="elu",
        obs_normalization=False,
        distribution_cfg=RslRlMLPModelCfg.GaussianDistributionCfg(init_std=1.0),
    )
    critic = RslRlMLPModelCfg(hidden_dims=[64, 64], activation="elu", obs_normalization=False)
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.001,  # 0.01 在 500 次迭代内更好、1000 次退化，见 6.5.2"训练预算与消融结论"（D-028）
        num_learning_epochs=8,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )
