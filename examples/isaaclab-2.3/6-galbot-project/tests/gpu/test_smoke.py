# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）；pytest 9.1.1
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""有 GPU：冒烟测试。建环境 → reset → 走几十步，检查形状与数值（7.4；深入的环境自检见 7.3 的 check_env.py）。"""

import gymnasium as gym
import pytest
import torch

from isaaclab_tasks.utils import parse_env_cfg

pytestmark = pytest.mark.gpu


def test_all_galbot_cfgs_construct():
    """配置类能构造：注册表里每个 Galbot 任务的配置都能解析（不建环境，秒级）。"""
    tasks = [t for t in gym.registry if t.startswith("Galbot-")]
    assert len(tasks) >= 8
    for task in tasks:
        assert parse_env_cfg(task, device="cuda:0", num_envs=2).decimation >= 1


@pytest.mark.parametrize("task", ["Galbot-Reach-v0", "Galbot-Reach-Direct-v0"])
def test_reach_steps(make_env, task):
    env = make_env(task, num_envs=4)
    obs, _ = env.reset()
    assert obs["policy"].shape == (4, 28)
    gen = torch.Generator(device="cuda:0").manual_seed(0)
    for _ in range(30):
        action = torch.randn(4, 7, device="cuda:0", generator=gen) * 0.5
        obs, rew, terminated, truncated, _ = env.step(action)
        assert torch.isfinite(obs["policy"]).all(), "观测出现 NaN / Inf"
        assert rew.shape == (4,) and torch.isfinite(rew).all(), "奖励出现 NaN / Inf"
    assert not terminated.any() and not truncated.any()  # reach 只有 12 s 超时，30 步内不该结束
