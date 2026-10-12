# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0（PhysX 后端）；rsl_rl 5.4.1
# 验证日期：2026-10-10（--load_models_only 为 8.10 所加，2026-10-12，RTX 5090）
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""评估一个 reach 策略（3.0 EA 版，8.5）。指标与 2.3 版的 eval_reach.py（6.5.1、6.6.1）完全相同：
跑一个完整回合，在每段目标（4 s）的最后一步记录 TCP 误差，报告位置误差的中位数、90% 分位、< 2 cm / < 5 cm 的比例、
均值与最大值，姿态误差的中位数，以及"停住但没到"的样本数。

与 2.3 版的差别只在启动方式：按 3.0 的 play 入口（isaaclab_rl/entrypoints/backends/play_rsl_rl.py）解析物理预设、
用 launch_simulation 启动（PhysX 后端经 Isaac Sim，Newton 后端不启动 Kit），数据用 .torch 取张量。

    python scripts/eval_reach.py --checkpoint <运行目录>/model_999.pt physics=isaacsim_physx
    python scripts/eval_reach.py --checkpoint <运行目录>/model_999.pt physics=newton_mjwarp
"""

import argparse
import sys

from isaaclab.app import add_launcher_args, launch_simulation
from isaaclab.utils.string import list_intersection

from isaaclab_rl.entrypoints.common import add_frontend_args, create_isaaclab_env

from isaaclab_tasks.utils import setup_preset_cli
from isaaclab_tasks.utils.hydra import hydra_task_config

import galbot_academy

parser = argparse.ArgumentParser(description="评估 reach 策略（3.0 EA）")
parser.add_argument("--task", default="Galbot-Reach-Play")
parser.add_argument("--agent", default="rsl_rl_cfg_entry_point")
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--num_envs", type=int, default=256)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--load_models_only", action="store_true",
                    help="只加载 actor 与 critic，不加载优化器状态（convert_ckpt_23_to_30.py 转出的检查点没有优化器状态，8.10）")
parser.add_argument("--cmd_quat_wxyz", action="store_true",
                    help="把策略观测里目标姿态的四元数改回 2.3 的 (w, x, y, z) 顺序，用来评估 2.3 训练的检查点（8.10 对照）")
add_launcher_args(parser)
add_frontend_args(parser)  # create_isaaclab_env 要读其中的参数（如 --frontend）
args, remaining = setup_preset_cli(parser)
galbot_academy.register_tasks()  # 注册 Galbot-Reach / Galbot-Reach-Play
sys.argv = [sys.argv[0]] + list_intersection(remaining, None)  # 其余参数（如 physics=...）交给 Hydra


@hydra_task_config(args.task, args.agent)
def main(env_cfg, agent_cfg) -> None:
    import torch
    from rsl_rl.runners import OnPolicyRunner

    import importlib.metadata

    from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg

    if args.cmd_quat_wxyz:
        orig = env_cfg.observations.policy.pose_command.func

        def pose_command_wxyz(env, command_name: str):  # 管理器按函数签名核对参数，不能用 **kw
            c = orig(env, command_name=command_name)
            return torch.cat([c[:, :3], c[:, 6:7], c[:, 3:6]], dim=1)  # (x, y, z, qx, qy, qz, qw) → (…, qw, qx, qy, qz)

        env_cfg.observations.policy.pose_command.func = pose_command_wxyz
        print("[8.10] 观测里的目标四元数改为 (w, x, y, z) 顺序", flush=True)
    with launch_simulation(env_cfg, args):
        env_cfg.scene.num_envs = args.num_envs
        env_cfg.seed = args.seed
        # 与 3.0 的 play 入口相同：按已安装的 rsl_rl 版本整理配置（不做这一步，rsl_rl 5.x 建模型时会报参数错误）
        agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, importlib.metadata.version("rsl-rl-lib"))
        env = RslRlVecEnvWrapper(create_isaaclab_env(args.task, env_cfg, args, convert_marl_to_single_agent=False))
        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
        runner.load(args.checkpoint, load_cfg={"actor": True, "critic": True} if args.load_models_only else None)
        policy = runner.get_inference_policy(device=env.unwrapped.device)

        base = env.unwrapped
        robot = base.scene["robot"]
        arm = [i for i, n in enumerate(robot.joint_names) if n.startswith("right_arm_joint")]
        cmd = base.command_manager.get_term("ee_pose")
        seg = round(cmd.cfg.resampling_time_range[0] / base.step_dt)  # 每段目标的控制步数
        T = int(base.max_episode_length)
        win = round(0.5 / base.step_dt)  # 每段最后 0.5 s：用位置变化判断手臂是否还在动（6.1.5）
        q_hist = []
        obs = env.get_observations()
        pos_err, rot_err, stuck = [], [], 0
        with torch.inference_mode():
            for k in range(T - 1):  # 最后一步会触发超时重置，在它之前读
                obs, _, _, _ = env.step(policy(obs))
                q_hist = (q_hist + [robot.data.joint_pos.torch[:, arm].clone()])[-win:]  # 3.0：.torch
                if (k + 1) % seg == 0 or k == T - 2:
                    pe, re = cmd.metrics["position_error"].clone(), cmd.metrics["orientation_error"].clone()
                    moved = (q_hist[-1] - q_hist[0]).abs().max(dim=1).values
                    pos_err.append(pe)
                    rot_err.append(re)
                    stuck += int(((pe > 0.05) & (moved < 0.01)).sum())
        pe, re = torch.cat(pos_err), torch.cat(rot_err)
        n = len(pe)
        bad = int((~torch.isfinite(pe)).sum())
        if bad:  # 8.10：数值发散的样本会让中位数等统计变成 nan
            print(f"  非有限（nan / inf）的样本：{bad} / {n}；下面的统计只算有限值", flush=True)
            fin = torch.isfinite(pe) & torch.isfinite(re)
            pe, re = pe[fin], re[fin]
            print(f"  把非有限样本记为失败：< 5 cm {(pe < 0.05).sum().item() / n * 100:.1f}%（{int((pe < 0.05).sum())} / {n}）", flush=True)
        print(f"{args.checkpoint}：{args.num_envs} 个环境 × {n // args.num_envs} 段目标 = {n} 个样本（每段末尾）")
        print(f"  位置误差：中位数 {pe.median().item() * 100:.2f} cm，90% 分位 {pe.quantile(0.9).item() * 100:.2f} cm，"
              f"< 2 cm {(pe < 0.02).float().mean().item() * 100:.1f}%，< 5 cm {(pe < 0.05).float().mean().item() * 100:.1f}%")
        print(f"  位置误差：均值 {pe.mean().item() * 100:.2f} cm，最大 {pe.max().item() * 100:.2f} cm")
        print(f"  姿态误差：中位数 {re.median().item():.3f} rad，90% 分位 {re.quantile(0.9).item():.3f} rad")
        print(f"  误差 > 5 cm 且最后 0.5 s 内右臂关节位置变化 < 0.01 rad 的样本（停住但没到）：{stuck} / {n}")
        sys.stdout.flush()
        env.close()


if __name__ == "__main__":
    main()
