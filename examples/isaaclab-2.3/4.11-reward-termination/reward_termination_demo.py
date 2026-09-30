# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-09-30
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""在官方 Cartpole 上加一个奖励项、一个终止条件和一个课程项，用随机动作运行，打印分项奖励与回合统计。

用法::

    python reward_termination_demo.py --headless                                  # 随机动作，含新终止条件
    python reward_termination_demo.py --headless --zero_action --no_pole_fallen   # 零动作、不加新终止：看超时
"""

import argparse
import math
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Reward / Termination / Curriculum 演示")
parser.add_argument("--num_envs", type=int, default=16, help="环境数量")
parser.add_argument("--steps", type=int, default=320, help="运行的环境步数（回合上限为 300 步）")
parser.add_argument("--seed", type=int, default=42, help="随机种子")
parser.add_argument("--zero_action", action="store_true", help="动作恒为 0（默认为 [-1, 1] 均匀随机）")
parser.add_argument("--no_pole_fallen", action="store_true", help="不加 pole_fallen 终止条件")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.envs.mdp as mdp
from isaaclab.envs import ManagerBasedRLEnv
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.utils import configclass
from isaaclab_tasks.manager_based.classic.cartpole.cartpole_env_cfg import CartpoleEnvCfg


@configclass
class CurriculumCfg:
    # 环境步计数（common_step_counter）超过 100 后，把 action_rate 的权重改为 -0.1
    action_rate = CurrTerm(
        func=mdp.modify_reward_weight, params={"term_name": "action_rate", "weight": -0.1, "num_steps": 100}
    )


@configclass
class MyCartpoleEnvCfg(CartpoleEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = args.num_envs
        self.seed = args.seed
        # 奖励：惩罚动作变化（正则惩罚类，权重为负）
        self.rewards.action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.01)
        # 终止：摆杆倒下超过 90°（失败，不是超时）
        if not args.no_pole_fallen:
            self.terminations.pole_fallen = DoneTerm(
                func=mdp.joint_pos_out_of_manual_limit,
                params={"asset_cfg": SceneEntityCfg("robot", joint_names=["cart_to_pole"]), "bounds": (-math.pi / 2, math.pi / 2)},
            )
        # 课程：官方 Cartpole 没有课程配置（curriculum 为 None），这里新建一个
        self.curriculum = CurriculumCfg()


def main() -> None:
    env = ManagerBasedRLEnv(cfg=MyCartpoleEnvCfg())
    print(f"step_dt {env.step_dt:.5f} s，episode_length_s {env.max_episode_length_s}，回合上限 {env.max_episode_length} 步")

    env.reset()
    n_terminated = n_truncated = 0
    log = {}
    for step in range(1, args.steps + 1):
        actions = 2.0 * torch.rand(env.num_envs, env.action_manager.total_action_dim, device=env.device) - 1.0
        if args.zero_action:
            actions.zero_()
        _, rew, terminated, truncated, extras = env.step(actions)
        n_terminated += int(terminated.sum())
        n_truncated += int(truncated.sum())
        if "log" in extras and extras["log"]:
            log = {k: float(v) for k, v in extras["log"].items()}  # 保留最近一次重置时的统计
        if step == 1:
            # 核对：总奖励 = Σ(func × weight) × dt
            terms = dict(env.reward_manager.get_active_iterable_terms(0))
            recomputed = sum(v[0] for v in terms.values()) * env.step_dt
            print("第 1 步 env 0 的各项（func × weight，未乘 dt）：")
            for name, value in terms.items():
                print(f"  {name:12s} {value[0]: .4f}")
            print(f"Σ × dt = {recomputed:.6f}，env 返回的奖励 = {rew[0].item():.6f}")

    print(f"{args.steps} 步内：terminated（失败）{n_terminated} 次，truncated（超时）{n_truncated} 次")
    print(f"当前 action_rate 权重 {env.reward_manager.get_term_cfg('action_rate').weight}（课程已生效）")
    print("最近一次重置时的日志：")
    for key in sorted(log):
        print(f"  {key:40s} {log[key]: .4f}")

    env.close()  # 环境的 close() 会释放 SimulationContext


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
