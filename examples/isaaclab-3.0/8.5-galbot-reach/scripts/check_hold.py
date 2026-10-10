# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""迁移后的自检（3.0 EA 版，8.5）：Galbot-Reach 零动作保持 2 s，打印关节偏离默认姿态的最大值、TCP 相对机器人根的位置，
与 2.3 的数字对照（6.2.1：TCP 约 (0.684, -0.071, 1.409) m；6.1.6：保持误差 0.0527 rad）。
四元数顺序或执行器字段迁移错了，这两个数会明显不同。

    python scripts/check_hold.py physics=isaacsim_physx
    python scripts/check_hold.py physics=newton_mjwarp
"""

import argparse
import sys

from isaaclab.app import add_launcher_args, launch_simulation
from isaaclab.utils.string import list_intersection

from isaaclab_rl.entrypoints.common import add_frontend_args, create_isaaclab_env

from isaaclab_tasks.utils import setup_preset_cli
from isaaclab_tasks.utils.hydra import hydra_task_config

import galbot_academy

parser = argparse.ArgumentParser(description="零动作保持检查（3.0 EA）")
parser.add_argument("--task", default="Galbot-Reach")
parser.add_argument("--agent", default="rsl_rl_cfg_entry_point")
parser.add_argument("--num_envs", type=int, default=4)
add_launcher_args(parser)
add_frontend_args(parser)  # create_isaaclab_env 要读其中的参数（如 --frontend）
args, remaining = setup_preset_cli(parser)
galbot_academy.register_tasks()
sys.argv = [sys.argv[0]] + list_intersection(remaining, None)


@hydra_task_config(args.task, args.agent)
def main(env_cfg, agent_cfg) -> None:
    import torch

    from isaaclab.utils.math import subtract_frame_transforms

    from galbot_academy.assets.galbot import REACH_EE_BODY, REACH_EE_OFFSET_POS, REACH_EE_OFFSET_ROT
    from galbot_academy.tasks.reach.mdp.tcp import tcp_pose_w

    phys = env_cfg.sim.physics
    solver = getattr(phys, "solver_cfg", None)
    print(f"[8.5] 配置：physics {type(phys).__name__}"
          + (f"，nconmax {solver.nconmax}，njmax {solver.njmax}" if solver is not None and hasattr(solver, "nconmax") else "")
          + f"；robot usd {env_cfg.scene.robot.spawn.usd_path}")
    sys.stdout.flush()
    with launch_simulation(env_cfg, args):
        env_cfg.scene.num_envs = args.num_envs
        env_cfg.commands.ee_pose.debug_vis = False
        env = create_isaaclab_env(args.task, env_cfg, args, convert_marl_to_single_agent=False).unwrapped
        env.reset()
        robot = env.scene["robot"]
        act = torch.zeros(env.num_envs, env.action_manager.total_action_dim, device=env.device)
        for _ in range(round(2.0 / env.step_dt)):
            env.step(act)
        d = robot.data
        err = (d.joint_pos.torch - d.default_joint_pos.torch).abs()
        worst = err.max(dim=0).values.argmax().item()
        body = robot.find_bodies(REACH_EE_BODY)[0][0]
        p_w, q_w = tcp_pose_w(robot, body, REACH_EE_OFFSET_POS, REACH_EE_OFFSET_ROT)
        p_b, _ = subtract_frame_transforms(d.root_pos_w.torch, d.root_quat_w.torch, p_w, q_w)
        print(f"[8.5] physics {type(env_cfg.sim.physics).__name__}：零动作保持 2 s，关节最大偏离 {err.max().item():.4f} rad"
              f"（{robot.joint_names[worst]}），数值有限 {bool(torch.isfinite(d.joint_pos.torch).all())}")
        print(f"[8.5] env_0 TCP 相对机器人根 {[round(x, 3) for x in p_b[0].tolist()]} m；TCP 世界系四元数（XYZW）"
              f"{[round(x, 3) for x in q_w[0].tolist()]}")
        sys.stdout.flush()
        env.close()


if __name__ == "__main__":
    main()
