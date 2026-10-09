# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-09
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""评估一个 lift 策略（6.4.3）：每个环境跑一个完整回合（5 s，目标在回合内不重采样），在超时前最后一步判定。

成功 = 方块中心高出静止高度 ≥ 4 cm，且方块到目标位置的距离 < 5 cm（6.4.3 合格线的口径）。
失败的回合按以下顺序归类（取第一个符合的）：
- 掉落：回合中途因"方块掉下桌面"终止；
- 举起后掉回：回合中某一时刻举起过（≥ 4 cm），最后一步不再举起；
- 推走：从没举起过，但方块水平移动超过 5 cm；
- 没抓起：从没举起过，方块也基本没动；
- 举起但没到目标：最后一步仍举起，但离目标 ≥ 5 cm。

    python scripts/eval_lift.py --headless --checkpoint logs/rsl_rl/galbot_lift/<运行>/model_1499.pt
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="评估 lift 策略")
parser.add_argument("--task", default="Galbot-Lift-Play-v0")
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--num_envs", type=int, default=256)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--lift_height", type=float, default=0.04, help="举起的判据（m）")
parser.add_argument("--goal_tol", type=float, default=0.05, help="到达目标的判据（m）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch
from rsl_rl.runners import OnPolicyRunner

from isaaclab.utils.math import combine_frame_transforms
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from isaaclab_tasks.utils import load_cfg_from_registry, parse_env_cfg

import galbot_academy.tasks  # noqa: F401
from galbot_academy.scenes.lift import CUBE_REST_Z


def main() -> None:
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    env_cfg.seed = args.seed
    agent_cfg = load_cfg_from_registry(args.task, "rsl_rl_cfg_entry_point")
    env = RslRlVecEnvWrapper(gym.make(args.task, cfg=env_cfg))
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    runner.load(args.checkpoint)
    policy = runner.get_inference_policy(device=env.unwrapped.device)

    base = env.unwrapped
    robot, obj = base.scene["robot"], base.scene["object"]
    n, dev = base.num_envs, base.device
    T = int(base.max_episode_length)
    rest_z = base.scene.env_origins[:, 2] + CUBE_REST_Z

    def lift():
        return obj.data.root_pos_w[:, 2] - rest_z

    def goal_dist():
        cmd = base.command_manager.get_command("object_pose")[:, :3]
        goal_w, _ = combine_frame_transforms(robot.data.root_pos_w, robot.data.root_quat_w, cmd)
        return (goal_w - obj.data.root_pos_w).norm(dim=-1)

    obs = env.get_observations()
    start_xy = obj.data.root_pos_w[:, :2].clone()
    alive = torch.ones(n, dtype=torch.bool, device=dev)  # 还在第一个回合里
    dropped = torch.zeros(n, dtype=torch.bool, device=dev)
    ever_lifted = torch.zeros(n, dtype=torch.bool, device=dev)
    max_xy = torch.zeros(n, device=dev)
    last_pos = obj.data.root_pos_w.clone() - base.scene.env_origins  # 上一步方块位置（环境局部坐标），用于判断掉落发生在哪里
    drop_pos = torch.full((n, 3), float("nan"), device=dev)
    ee = base.scene["ee_frame"]
    tcp_prev = ee.data.target_pos_w[:, 0].clone()
    v_prev = torch.zeros(n, 3, device=dev)
    acc_lifted = []
    open_lifted = []  # 方块举起期间，夹爪动作是否为"张开"（二值动作：值 >= 0 为张开）  # 方块举起期间 TCP 的加速度（控制步上的差分），与 check_grasp.py --accel_sweep 的滑脱加速度对照
    with torch.inference_mode():
        for _ in range(T - 1):  # 最后一步会触发超时重置，在它之前读
            act = policy(obs)
            obs, _, dones, extras = env.step(act)
            early = dones.bool() & alive & ~extras["time_outs"].bool()
            drop_pos[early] = last_pos[early]  # 终止发生在本步内，重置后的位置已不可用，取上一步的位置
            dropped |= early
            alive &= ~dones.bool()
            ever_lifted |= alive & (lift() >= args.lift_height)
            max_xy = torch.where(alive, torch.maximum(max_xy, (obj.data.root_pos_w[:, :2] - start_xy).norm(dim=-1)), max_xy)
            last_pos = obj.data.root_pos_w.clone() - base.scene.env_origins
            tcp = ee.data.target_pos_w[:, 0]
            v = (tcp - tcp_prev) / base.step_dt
            acc = (v - v_prev).norm(dim=-1) / base.step_dt
            sel = alive & (lift() >= args.lift_height) & ~dones.bool()
            if sel.any():
                acc_lifted.append(acc[sel])
                open_lifted.append(act[sel, -1] >= 0)
            tcp_prev, v_prev = tcp.clone(), torch.where(dones.bool().unsqueeze(-1), torch.zeros_like(v), v)
        lifted_now = alive & (lift() >= args.lift_height)
        dist = goal_dist()
    success = lifted_now & (dist < args.goal_tol)
    cats = {}
    rest = ~success
    for name, mask in [
        ("掉落（中途终止）", dropped),
        ("举起后掉回", ever_lifted & ~lifted_now),
        ("推走（水平移动 > 5 cm）", ~ever_lifted & (max_xy > 0.05)),
        ("没抓起", ~ever_lifted),
        ("举起但没到目标", lifted_now),
    ]:
        cats[name] = int((rest & mask).sum())
        rest &= ~mask
    print(f"{args.checkpoint}：{n} 个回合")
    print(f"  成功率 {success.float().mean().item() * 100:.1f}%（举起 ≥ {args.lift_height * 100:.0f} cm 且离目标 < {args.goal_tol * 100:.0f} cm）")
    ok = lifted_now
    if ok.any():
        print(f"  最后一步仍举起的 {int(ok.sum())} 个回合：离目标中位数 {dist[ok].median().item() * 100:.2f} cm，"
              f"90% 分位 {dist[ok].quantile(0.9).item() * 100:.2f} cm")
    print("  失败归类：" + "，".join(f"{k} {v}" for k, v in cats.items()))
    if acc_lifted:
        a = torch.cat(acc_lifted)
        print(f"  举起期间 TCP 加速度（{len(a)} 个样本）：中位数 {a.median().item():.1f} m/s²，90% 分位 {a.quantile(0.9).item():.1f}，99% 分位 {a.quantile(0.99).item():.1f}")
    if open_lifted:
        o = torch.cat(open_lifted).float()
        print(f"  举起期间夹爪动作为\"张开\"的比例：{o.mean().item() * 100:.1f}%（{len(o)} 个样本）")
    if dropped.any():
        # 掉落前一步方块在哪：仍在桌面范围内、且已低于桌面，说明是被压穿了桌面，而不是从桌边掉下
        from galbot_academy.scenes.reach import TABLE_CENTER_XY, TABLE_SIZE, TABLE_TOP_Z
        dp = drop_pos[dropped]
        inside = ((dp[:, 0] - TABLE_CENTER_XY[0]).abs() < TABLE_SIZE[0] / 2) & ((dp[:, 1] - TABLE_CENTER_XY[1]).abs() < TABLE_SIZE[1] / 2)
        below = dp[:, 2] < TABLE_TOP_Z
        print(f"  掉落前一步：方块仍在桌面投影范围内 {int(inside.sum())}/{len(dp)}，其中已低于桌面 {int((inside & below).sum())}；"
              f"高度中位数 {dp[:, 2].median().item():.3f} m（桌面 {TABLE_TOP_Z} m）")
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
