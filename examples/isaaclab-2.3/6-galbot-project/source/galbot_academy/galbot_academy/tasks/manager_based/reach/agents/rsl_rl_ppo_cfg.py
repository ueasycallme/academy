# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-08
"""Galbot reach 的 PPO 配置（6.5.1）：照搬 Isaac-Reach-Franka-v0 的 FrankaReachPPORunnerCfg（isaaclab_tasks v2.3.2），
只改实验名。两个任务的观测、动作维数相近（Franka 观测 32 维、Galbot 28 维，动作都是 7 维），控制周期都是 1/30 s。
"""

from isaaclab.utils import configclass

from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg


@configclass
class GalbotReachPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 24  # 每次迭代每个环境采 24 个控制步
    max_iterations = 1000
    save_interval = 50
    experiment_name = "galbot_reach"
    run_name = ""
    policy = RslRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_obs_normalization=False,
        critic_obs_normalization=False,
        actor_hidden_dims=[64, 64],
        critic_hidden_dims=[64, 64],
        activation="elu",
    )
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.001,
        num_learning_epochs=8,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )
