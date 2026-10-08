# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""检查 Galbot-Reach-DR-v0 的域随机化是否生效（6.4.2）。

从仿真读回每个环境的右臂连杆质量、驱动刚度与阻尼、armature，看它们是否彼此不同、是否落在设定范围内；
看第二次 reset 后右臂的初始位置与速度（第一次 reset 的初速度会被夹成 0，见 4.6 常见坑四）；
比较带噪声的观测与不带噪声的原值，确认噪声在 ±0.01 内；最后检查 -Play 配置里哪些随机化被关掉。

    python scripts/check_dr.py --headless
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="检查域随机化")
parser.add_argument("--num_envs", type=int, default=8)
parser.add_argument("--seed", type=int, default=0)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

import galbot_academy.tasks  # noqa: F401
from galbot_academy.assets.drives import GROUPS
from galbot_academy.tasks.manager_based.reach import mdp
from galbot_academy.tasks.manager_based.reach.reach_dr_env_cfg import GalbotReachDREnvCfg_PLAY
from galbot_academy.tasks.manager_based.reach.reach_env_cfg import ARM

TASK = "Galbot-Reach-DR-v0"


def span(x: torch.Tensor) -> str:
    return f"{x.min().item():.4f} … {x.max().item():.4f}"


def main() -> None:
    cfg = parse_env_cfg(TASK, device=args.device, num_envs=args.num_envs)
    cfg.seed = args.seed
    env = gym.make(TASK, cfg=cfg)
    base = env.unwrapped
    robot = base.scene["robot"]
    names, bodies = robot.joint_names, robot.body_names
    arm = [i for i, n in enumerate(names) if n.startswith("right_arm_joint")]
    links = [i for i, n in enumerate(bodies) if n.startswith("right_arm_link")]
    print(f"{TASK}：{args.num_envs} 个环境，种子 {args.seed}")

    # 质量：PhysX 读回的值 / 默认值
    mass = robot.root_physx_view.get_masses()[:, links].to(base.device)
    ratio = mass / robot.data.default_mass[:, links].to(base.device)
    print(f"  右臂连杆质量 / 标称：{span(ratio)}（设定 ×[0.9, 1.1]）；link3 各环境 {[round(x, 3) for x in mass[:, 2].tolist()]} kg")
    # 增益：写进 PhysX 的刚度、阻尼 / 参数表的标称值
    k = robot.root_physx_view.get_dof_stiffnesses()[:, arm].to(base.device)
    d = robot.root_physx_view.get_dof_dampings()[:, arm].to(base.device)
    k0, d0 = GROUPS["arms"]["stiffness"], GROUPS["arms"]["damping"]
    print(f"  右臂刚度 / {k0:g}：{span(k / k0)}；阻尼 / {d0:g}：{span(d / d0)}（设定 ×[0.8, 1.2]）")
    print(f"    joint1 刚度各环境 {[round(x, 1) for x in k[:, 0].tolist()]}")
    arma = robot.root_physx_view.get_dof_armatures()[:, arm]
    print(f"  右臂 armature：{span(arma)} kg·m²（设定 +[0, 0.005]）")
    distinct = len({round(x, 4) for x in ratio[:, 2].tolist()})
    print(f"  link3 质量在 {args.num_envs} 个环境中有 {distinct} 个不同取值")

    # 初始状态：先 reset、走一步，再 reset，读第二次 reset 后的状态
    env.reset()
    env.step(torch.zeros(env.action_space.shape, device=base.device))
    env.reset()
    off = robot.data.joint_pos[:, arm] - robot.data.default_joint_pos[:, arm]
    vel = robot.data.joint_vel[:, arm]
    print(f"  第二次 reset 后右臂：位置偏移 {span(off)} rad（设定 ±0.2），速度 {span(vel)} rad/s（设定 ±0.1）")

    # 观测噪声：带噪声的 joint_pos 项与不带噪声的原值之差
    obs = base.observation_manager.compute()["policy"]
    arm_cfg = ARM.replace()  # 在 Manager 之外直接调用 Term 函数时，SceneEntityCfg 要先 resolve，否则 joint_ids 是全部关节
    arm_cfg.resolve(base.scene)
    raw = mdp.joint_pos_rel(base, arm_cfg)
    diff = obs[:, :7] - raw
    print(f"  观测 joint_pos 项的噪声：{span(diff)}（设定 ±0.01），enable_corruption = {cfg.observations.policy.enable_corruption}")
    env.close()

    play = GalbotReachDREnvCfg_PLAY()
    ev = play.events
    print(f"  -Play 配置：enable_corruption = {play.observations.policy.enable_corruption}；arm_mass = {ev.arm_mass}，"
          f"arm_gains = {ev.arm_gains}，arm_armature = {ev.arm_armature}；reset_robot_joints 保留 = {ev.reset_robot_joints is not None}")


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
