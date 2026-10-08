# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB
"""给官方 Cartpole 加一个自定义指令项"小车目标位置"（4.13），观察重采样与 time_left。

指令每 1–2 s 重采样一次；观测用 generated_commands 读出它，奖励按它算小车位置误差。
脚本零动作跑 6 s（跨过 5 s 的超时重置），打印：
- Command Manager 的 __str__ 表；
- 前 4 个环境每次重采样的时刻、新旧目标、新的 time_left；
- 所有环境实际的重采样间隔范围；
- 重采样那一步，奖励读到的是旧目标还是新目标；
- 超时重置时写进 extras["log"] 的指标。

用法::

    python command_demo.py --headless
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Command Manager 演示")
parser.add_argument("--num_envs", type=int, default=16, help="环境数量")
parser.add_argument("--seed", type=int, default=42, help="随机种子")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

from collections.abc import Sequence  # noqa: E402

import torch  # noqa: E402

import isaaclab.envs.mdp as mdp  # noqa: E402
from isaaclab.envs import ManagerBasedRLEnv  # noqa: E402
from isaaclab.managers import CommandTerm, CommandTermCfg  # noqa: E402
from isaaclab.managers import ObservationTermCfg as ObsTerm  # noqa: E402
from isaaclab.managers import RewardTermCfg as RewTerm  # noqa: E402
from isaaclab.utils import configclass  # noqa: E402
from isaaclab_tasks.manager_based.classic.cartpole.cartpole_env_cfg import CartpoleEnvCfg  # noqa: E402


class CartTargetCommand(CommandTerm):
    """小车沿导轨的目标位置，形状 (num_envs, 1)，单位 m，相对导轨零点。"""

    cfg: "CartTargetCommandCfg"

    def __init__(self, cfg: "CartTargetCommandCfg", env: ManagerBasedRLEnv):
        super().__init__(cfg, env)  # 基类建好 metrics、time_left、command_counter
        self.robot = env.scene[cfg.asset_name]
        self.joint_id = self.robot.find_joints(cfg.joint_name)[0][0]
        self.target = torch.zeros(self.num_envs, 1, device=self.device)
        self.metrics["error"] = torch.zeros(self.num_envs, device=self.device)

    def __str__(self) -> str:
        return f"CartTargetCommand: 目标范围 {self.cfg.target_range} m，重采样间隔 {self.cfg.resampling_time_range} s"

    @property
    def command(self) -> torch.Tensor:
        return self.target

    def _update_metrics(self):
        cart_x = self.robot.data.joint_pos[:, self.joint_id]
        self.metrics["error"] = (cart_x - self.target[:, 0]).abs()  # 重置时取所有重置环境的平均，写进日志

    def _resample_command(self, env_ids: Sequence[int]):
        self.target[env_ids, 0] = torch.empty(len(env_ids), device=self.device).uniform_(*self.cfg.target_range)

    def _update_command(self):
        pass  # 目标在两次重采样之间保持不变


@configclass
class CartTargetCommandCfg(CommandTermCfg):
    class_type: type = CartTargetCommand  # 配置与实现类在这里绑定
    asset_name: str = "robot"
    joint_name: str = "slider_to_cart"
    target_range: tuple[float, float] = (-1.0, 1.0)


SEEN = {}  # 奖励函数最近一次读到的指令，用来检查它在 step() 中读的是哪一个


def cart_target_error(env: ManagerBasedRLEnv, command_name: str) -> torch.Tensor:
    cmd = env.command_manager.get_command(command_name)
    SEEN["cmd"] = cmd[:, 0].clone()
    joint_id = env.command_manager.get_term(command_name).joint_id
    return (env.scene["robot"].data.joint_pos[:, joint_id] - cmd[:, 0]).abs()


@configclass
class CommandsCfg:
    cart_target = CartTargetCommandCfg(resampling_time_range=(1.0, 2.0))


@configclass
class MyCartpoleEnvCfg(CartpoleEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = args.num_envs
        self.seed = args.seed
        self.commands = CommandsCfg()
        # 观测只读出指令，指令本身由 Command Manager 生成
        self.observations.policy.cart_target = ObsTerm(
            func=mdp.generated_commands, params={"command_name": "cart_target"}
        )
        self.rewards.track_target = RewTerm(func=cart_target_error, weight=-1.0, params={"command_name": "cart_target"})


def main() -> None:
    env = ManagerBasedRLEnv(cfg=MyCartpoleEnvCfg())
    print(env.command_manager)
    term = env.command_manager.get_term("cart_target")
    obs, _ = env.reset()
    print(f"step_dt = {env.step_dt:.4f} s；reset 后 command_counter（前 4 个）= {term.command_counter[:4].tolist()}")

    actions = torch.zeros(env.num_envs, env.action_manager.total_action_dim, device=env.device)
    prev_cmd = term.command[:, 0].clone()
    last_t = torch.zeros(env.num_envs, device=env.device)  # 每个环境上一次重采样的时刻
    intervals, checked = [], False
    for step in range(1, int(6.0 / env.step_dt) + 1):
        obs, _, terminated, truncated, extras = env.step(actions)
        t = step * env.step_dt
        cmd = term.command[:, 0]
        changed = (cmd != prev_cmd).nonzero().flatten().tolist()
        for i in changed:
            if i < 4:
                print(f"  t={t:5.3f} s  env {i}: 目标 {prev_cmd[i]:+.3f} → {cmd[i]:+.3f} m，"
                      f"新 time_left {term.time_left[i]:.3f} s，counter {int(term.command_counter[i])}")
            if t < 4.99:  # 只统计由 time_left 触发的重采样（5 s 处是超时重置）
                intervals.append(t - float(last_t[i]))
            last_t[i] = t
            if not checked:
                seen = SEEN["cmd"][i]
                print(f"  ↳ 这一步奖励读到的目标 {seen:+.3f}（{'旧' if seen == prev_cmd[i] else '新'}），"
                      f"观测里的目标 {obs['policy'][i, -1]:+.3f}（{'新' if obs['policy'][i, -1] == cmd[i] else '旧'}）")
                checked = True
        if (terminated | truncated).any():  # extras["log"] 只在有环境重置的那一步重新填写
            print(f"  t={t:5.3f} s  重置 {int((terminated | truncated).sum())} 个环境，"
                  f"extras['log']['Metrics/cart_target/error'] = {extras['log']['Metrics/cart_target/error']:.3f} m")
        prev_cmd = cmd.clone()

    print(f"由 time_left 触发的重采样 {len(intervals)} 次，间隔 {min(intervals):.3f}–{max(intervals):.3f} s"
          f"（配置 1.0–2.0 s，步长 {env.step_dt:.4f} s）")
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()  # Kit 退出时不会刷新 stdout 缓冲（CONVENTIONS 第 5 节）
    simulation_app.close()
