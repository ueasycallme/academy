# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-09
# GPU：NVIDIA GeForce RTX 5070 12 GB
"""把环境缩到 1 个，逐步打印观测各项、奖励各项、指令与 NaN 检查（7.3）。

    python scripts/debug_step.py --headless                      # Galbot-Reach-v0，1 个环境，零动作 3 步
    python scripts/debug_step.py --headless --breakpoint         # 第 1 步后停在 pdb，可以查看 env 的任何量
    python scripts/debug_step.py --headless --debugpy            # 等 VS Code 从 127.0.0.1:5678 attach
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("--task", default="Galbot-Reach-v0")
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--steps", type=int, default=3)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--breakpoint", action="store_true", help="第 1 步之后调用 breakpoint()")
parser.add_argument("--debugpy", action="store_true", help="在 127.0.0.1:5678 等待 VS Code 等调试器 attach（需 pip install debugpy）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym  # noqa: E402
import torch  # noqa: E402

import galbot_academy.tasks  # noqa: E402, F401
from isaaclab_tasks.utils import parse_env_cfg  # noqa: E402


def print_obs(env, obs):
    """按观测项拆开 env 0 的观测向量（组内各项按定义顺序拼接）。"""
    om = env.observation_manager
    for group, names in om.active_terms.items():
        vec, start = obs[group][0], 0
        print(f"  观测组 {group}（{vec.numel()} 维）")
        for name, dims in zip(names, om.group_obs_term_dim[group]):
            n = int(torch.tensor(dims).prod())
            print(f"    {name:16s} {vec[start:start + n]}")
            start += n


def main():
    if args.debugpy:
        import debugpy  # 不在 Isaac Lab 的依赖里，需要另外安装

        debugpy.listen(("127.0.0.1", 5678))
        print("debugpy 在 127.0.0.1:5678 等待调试器连接……", flush=True)
        debugpy.wait_for_client()  # 调试器 attach 之后才往下走
        print("调试器已连接", flush=True)
    torch.set_printoptions(precision=3, sci_mode=False, linewidth=140)  # 小数 3 位、不用科学计数，一行放得下
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    env_cfg.seed = args.seed
    env = gym.make(args.task, cfg=env_cfg).unwrapped
    obs, _ = env.reset()
    print(f"环境数 {env.num_envs}，step_dt {env.step_dt:.4f} s，动作维数 {env.action_manager.total_action_dim}")
    print("reset 之后：")
    print_obs(env, obs)

    actions = torch.zeros(env.num_envs, env.action_manager.total_action_dim, device=env.device)
    for step in range(1, args.steps + 1):
        obs, rew, terminated, truncated, _ = env.step(actions)
        print(f"第 {step} 步：总奖励 {rew[0].item():+.4f}，terminated {bool(terminated[0])}，truncated {bool(truncated[0])}")
        # 各奖励项的值 = 函数值 × 权重（每秒的速率，未乘 dt），与 RewardManager 内部的 _step_reward 相同
        for name, (value,) in env.reward_manager.get_active_iterable_terms(0):
            print(f"    奖励 {name:44s} {value:+.5f}")
        print(f"    指令 ee_pose（根坐标系）{env.command_manager.get_command('ee_pose')[0]}")
        nan = {g: bool(torch.isnan(o).any()) for g, o in obs.items()}
        print(f"    观测中有 NaN：{nan}")
        if step == 1:
            print_obs(env, obs)
            if args.breakpoint:
                breakpoint()  # 停在这里时仿真不会自己往前走：下一步要等 env.step() 被调用

    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()  # Kit 退出时不会刷新 stdout 缓冲（CONVENTIONS 第 5 节）
    simulation_app.close()
