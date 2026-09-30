# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2 + rsl-rl-lib 3.1.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""按官方 Cartpole 的 agent 配置建一个 RSL-RL ActorCritic，打印网络结构、参数量，
以及对同一个观测输出的动作均值、标准差、采样动作和价值；可选加载训练好的检查点对比。

用法::

    python inspect_actor_critic.py --headless
    python inspect_actor_critic.py --headless --checkpoint /path/to/logs/rsl_rl/cartpole/<时间戳>/model_99.pt
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="看一眼 actor 与 critic")
parser.add_argument("--checkpoint", default=None, help="RSL-RL 检查点（model_*.pt），不给则用刚初始化的网络")
parser.add_argument("--seed", type=int, default=42, help="随机种子")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch
from rsl_rl.modules import ActorCritic
from rsl_rl.utils import resolve_obs_groups

from isaaclab.envs import ManagerBasedRLEnv
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from isaaclab_tasks.manager_based.classic.cartpole.agents.rsl_rl_ppo_cfg import CartpolePPORunnerCfg
from isaaclab_tasks.manager_based.classic.cartpole.cartpole_env_cfg import CartpoleEnvCfg


def main() -> None:
    torch.manual_seed(args.seed)
    env_cfg = CartpoleEnvCfg()
    env_cfg.scene.num_envs = 4
    env_cfg.seed = args.seed
    env = RslRlVecEnvWrapper(ManagerBasedRLEnv(cfg=env_cfg))  # 创建时会 reset 一次
    agent_cfg = CartpolePPORunnerCfg()

    obs = env.get_observations()
    # Cartpole 没设置 obs_groups（配置中为 MISSING，训练脚本转成字典后为 {}）；缺省时 critic 用 policy 的观测
    groups = agent_cfg.obs_groups if isinstance(agent_cfg.obs_groups, dict) else {}
    obs_groups = resolve_obs_groups(obs, groups, ["critic"])
    policy_cfg = agent_cfg.policy.to_dict()
    policy_cfg.pop("class_name")
    policy = ActorCritic(obs, obs_groups, env.num_actions, **policy_cfg).to(env.device)
    if args.checkpoint:
        policy.load_state_dict(torch.load(args.checkpoint, map_location=env.device)["model_state_dict"])
    print(f"来源：{'检查点 ' + args.checkpoint if args.checkpoint else '刚初始化（种子 ' + str(args.seed) + '）'}")
    print(f"obs_groups {obs_groups}，动作维度 {env.num_actions}")
    print(f"actor：{policy.actor}")
    print(f"critic：{policy.critic}")
    count = lambda m: sum(p.numel() for p in m.parameters())
    print(f"参数量：actor {count(policy.actor)}，critic {count(policy.critic)}，另有标准差参数 {policy.std.numel()} 个")

    # 固定一个观测：摆杆偏 0.2 rad，其余为 0
    one = obs.clone()
    one["policy"][:] = torch.tensor([0.0, 0.2, 0.0, 0.0], device=env.device)
    with torch.no_grad():
        policy.act(one)  # 训练时：从高斯分布采样
        sampled = policy.distribution.sample()
        print(f"观测 [0, 0.2, 0, 0] → 动作均值 {policy.action_mean[0, 0].item():+.4f}，标准差 {policy.action_std[0, 0].item():.4f}")
        print(f"  训练时采样 4 次（4 个环境）：{[round(v, 3) for v in sampled[:, 0].tolist()]}")
        print(f"  回放时 act_inference：{policy.act_inference(one)[0, 0].item():+.4f}（即均值）")
        print(f"  critic 给出的价值：{policy.evaluate(one)[0, 0].item():+.4f}")

    env.close()  # 环境的 close() 会释放 SimulationContext


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
