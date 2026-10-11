# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""同一个多智能体环境，两种用法的形状对比（4.17）。

1. 直接用 DirectMARLEnv：观测、动作、奖励、终止都是按智能体名索引的字典；
2. 用 multi_agent_to_single_agent 拼成单智能体：观测拼接、动作切分、奖励求和、终止取"与"；
3. 把 MARL 环境直接交给 rsl_rl 的封装 RslRlVecEnvWrapper，看报什么错。

    python marl_shapes.py --headless
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="MARL 环境的形状（4.17）")
parser.add_argument("--task", default="Isaac-Cart-Double-Pendulum-Direct-v0")
parser.add_argument("--num_envs", type=int, default=16)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym  # noqa: E402
import torch  # noqa: E402

import isaaclab_tasks  # noqa: E402, F401
from isaaclab.envs import DirectMARLEnv, multi_agent_to_single_agent  # noqa: E402
from isaaclab_tasks.utils import parse_env_cfg  # noqa: E402


def shapes(x) -> str:
    if isinstance(x, dict):
        return "{" + "，".join(f"{k}: {shapes(v)}" for k, v in x.items()) + "}"
    if isinstance(x, torch.Tensor):
        return str(tuple(x.shape))
    return str(x)


def main() -> None:
    cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    env = gym.make(args.task, cfg=cfg)
    marl = env.unwrapped
    assert isinstance(marl, DirectMARLEnv)
    print(f"[4.17] possible_agents {marl.possible_agents}；观测空间 {marl.observation_spaces}；"
          f"动作空间 {marl.action_spaces}；state 空间 {marl.state_space}", flush=True)
    obs, _ = env.reset()
    actions = {a: torch.zeros(args.num_envs, marl.action_spaces[a].shape[0], device=marl.device) for a in marl.possible_agents}
    obs, rew, terminated, truncated, _ = env.step(actions)
    print(f"[4.17] MARL：obs {shapes(obs)}；state {shapes(marl.state())}；rew {shapes(rew)}；terminated {shapes(terminated)}", flush=True)

    single = multi_agent_to_single_agent(env)
    obs, _ = single.reset()
    action = torch.zeros(args.num_envs, single.single_action_space.shape[0], device=marl.device)
    obs, rew, terminated, truncated, _ = single.step(action)
    print(f"[4.17] 拼成单智能体：obs {shapes(obs)}；动作 {tuple(action.shape)}；rew {shapes(rew)}；terminated {shapes(terminated)}", flush=True)

    from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper

    try:
        RslRlVecEnvWrapper(env)
        print("[4.17] RslRlVecEnvWrapper 接受了 MARL 环境", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[4.17] RslRlVecEnvWrapper 直接包 MARL 环境：{type(e).__name__}: {e}", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
