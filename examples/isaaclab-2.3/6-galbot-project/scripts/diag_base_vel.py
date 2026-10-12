# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-12
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""底盘速度跟踪策略的逐步诊断（6.4.5 调参轮第 0 步）。只评估、不训练，不算成功率（成功率用 eval_base_vel.py）。

两种模式：
- fixed：与 eval_base_vel.py 相同的 4 组固定指令（每组 --num_envs 个回合、--seconds 秒），逐步记录底盘速度，
  回答"过冲是稳态还是暂态"：打印各时刻的速度均值与 10% / 90% 分位、峰值与末 2 s 均值；
- train：训练时的指令分布（随机指令、每 4 s 重采样、10% 零指令、12 s 回合），跑 --seconds 秒，
  统计倾覆：倾覆回合占结束回合的比例、倾覆时刻落在回合内的哪一段。

两种模式都统计主动轮动作：每步 |Δ速度目标| 的中位 / 90% 分位 / 最大值、|Δ| > 6 rad/s 的步数比例、
力矩达到上限的步数比例（刚重置的环境不计）。--no_tip 去掉倾覆终止项，只记录：倾斜第一次超过 0.5 rad 的时刻
与每回合最大倾斜，用来看"判据 0.5 是否偏紧"（最大倾斜落在 (0.5, 0.7] 的回合占多少）。--dump 把逐步数据存成 .npz。

    python scripts/diag_base_vel.py --headless --mode fixed --checkpoint <运行>/model_499.pt --dump diag_fixed.npz
    python scripts/diag_base_vel.py --headless --mode train --num_envs 256 --seconds 36 --checkpoint <运行>/model_499.pt
    python scripts/diag_base_vel.py --headless --mode train --no_tip --num_envs 256 --seconds 36 --checkpoint <运行>/model_499.pt
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="底盘速度跟踪的逐步诊断（6.4.5）")
parser.add_argument("--task", default="Galbot-BaseVel-v0")
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--mode", choices=["fixed", "train"], default="fixed")
parser.add_argument("--num_envs", type=int, default=64)
parser.add_argument("--seconds", type=float, default=4.0)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--no_tip", action="store_true", help="去掉倾覆终止项，只记录倾斜")
parser.add_argument("--tip_angle", type=float, default=0.5, help="倾覆判据（rad），与任务配置一致")
parser.add_argument("--dump", default=None, help="逐步数据存到这个 .npz")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper  # noqa: E402
from isaaclab_tasks.utils import load_cfg_from_registry, parse_env_cfg  # noqa: E402

import galbot_academy.tasks  # noqa: E402, F401
from galbot_academy.assets.omni_base import WHEEL_JOINTS  # noqa: E402

SCENARIOS = {  # 与 eval_base_vel.py 相同
    "直行 0.5 m/s": (0.5, 0.0, 0.0),
    "侧移 0.5 m/s": (0.0, 0.5, 0.0),
    "原地转 0.5 rad/s": (0.0, 0.0, 0.5),
    "组合": (0.3, 0.3, 0.3),
}
TIMES = (0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0)  # fixed 模式打印这些时刻的速度


def tilt(robot) -> torch.Tensor:
    """底盘倾斜角（rad）= acos(−g_z)，与 mdp.bad_orientation 同一个式子。"""
    return torch.acos((-robot.data.projected_gravity_b[:, 2]).clamp(-1.0, 1.0))


def run(env, policy, robot, steps: int) -> dict[str, np.ndarray]:
    """跑 steps 个控制步，逐步记录。fresh[k] 表示该环境在第 k 步之前刚重置（它的 Δ 不计）。"""
    base = env.unwrapped
    wheel_ids = robot.find_joints(WHEEL_JOINTS, preserve_order=True)[0]
    effort_limit = robot.data.joint_effort_limits[0, wheel_ids].max().item()
    rec = {k: [] for k in ("vel", "target", "torque", "tilt", "tipped", "timeout", "ep_t", "cmd", "fresh")}
    obs = env.get_observations()
    fresh = torch.ones(base.num_envs, dtype=torch.bool, device=base.device)
    for _ in range(steps):
        ep_t = (base.episode_length_buf + 1).float() * base.step_dt  # 本步结束时在回合内的时刻
        cmd = base.command_manager.get_command("base_velocity").clone()
        obs, _, dones, _ = env.step(policy(obs))
        tipped = base.termination_manager.get_term("tipped") if not args.no_tip else torch.zeros_like(dones, dtype=torch.bool)
        rec["vel"].append(torch.cat([robot.data.root_lin_vel_b[:, :2], robot.data.root_ang_vel_b[:, 2:3]], dim=1))
        rec["target"].append(robot.data.joint_vel_target[:, wheel_ids].clone())
        rec["torque"].append(robot.data.applied_torque[:, wheel_ids].clone())
        rec["tilt"].append(tilt(robot))
        rec["tipped"].append(tipped.clone())
        rec["timeout"].append(base.termination_manager.time_outs.clone())
        rec["ep_t"].append(ep_t)
        rec["cmd"].append(cmd)
        rec["fresh"].append(fresh.clone())
        fresh = dones.bool()  # 下一步之前刚重置的环境
    out = {k: torch.stack(v).cpu().numpy() for k, v in rec.items()}  # (步, 环境, …)
    out["effort_limit"] = np.array(effort_limit)
    out["step_dt"] = np.array(base.step_dt)
    return out


def action_stats(name: str, d: dict[str, np.ndarray]) -> None:
    """|Δ速度目标| 与力矩打满的比例。重置后的第一步、以及刚重置的环境都不计 Δ。"""
    tgt, fresh = d["target"], d["fresh"]
    done = d["tipped"] | d["timeout"]
    valid = ~fresh[1:] & ~done[1:] & ~done[:-1]  # 本步与上一步都没有重置
    delta = np.abs(tgt[1:] - tgt[:-1])[valid]  # (有效步, 4)
    sat = (np.abs(d["torque"]) >= d["effort_limit"] - 0.1)[~done]
    print(f"[diag] {name}：|Δ轮速目标| 中位 {np.median(delta):.3f}、90% {np.quantile(delta, 0.9):.3f}、最大 {delta.max():.2f} rad/s；"
          f"|Δ| > 6 rad/s 占 {(delta > 6).mean() * 100:.2f}%；力矩达到上限 {d['effort_limit']:.4g} N·m 的轮·步占 {sat.mean() * 100:.2f}%"
          f"（{delta.size} 个轮·步）", flush=True)


def fixed_mode(env, policy, robot, cfg_ranges) -> dict[str, np.ndarray]:
    base = env.unwrapped
    steps = round(args.seconds / base.step_dt)
    dumps = {}
    for idx, (name, (vx, vy, wz)) in enumerate(SCENARIOS.items()):
        cfg_ranges.lin_vel_x, cfg_ranges.lin_vel_y, cfg_ranges.ang_vel_z = (vx, vx), (vy, vy), (wz, wz)
        env.reset()
        d = run(env, policy, robot, steps)
        comp = 2 if wz != 0 and vx == 0 and vy == 0 else (1 if vy != 0 and vx == 0 else 0)  # 主看哪一个分量
        label = ("vx", "vy", "wz")[comp]
        v = d["vel"][:, :, comp]  # (步, 环境)
        t = (np.arange(steps) + 1) * base.step_dt
        cells = []
        for s in TIMES:
            k = min(steps - 1, round(s / base.step_dt) - 1)
            cells.append(f"{s:g}s {v[k].mean():.3f}[{np.quantile(v[k], 0.1):.3f},{np.quantile(v[k], 0.9):.3f}]")
        mean_curve = v.mean(axis=1)
        k_peak = int(mean_curve.argmax())
        tail = v[t > args.seconds - 2.0].mean()
        print(f"[diag] {name}（指令 {vx}, {vy}, {wz}）{label} 均值[10%,90%]：" + "；".join(cells), flush=True)
        print(f"[diag] {name}：均值曲线峰值 {mean_curve[k_peak]:.3f}（t = {t[k_peak]:.2f} s），末 2 s 均值 {tail:.3f}；"
              f"倾覆 {int(d['tipped'].any(axis=0).sum())} / {base.num_envs} 回合；最大倾斜 中位 {np.median(d['tilt'].max(axis=0)):.3f}、"
              f"最大 {d['tilt'].max():.3f} rad", flush=True)
        action_stats(name, d)
        dumps.update({f"s{idx}_{k}": v_ for k, v_ in d.items()})
    return dumps


def train_mode(env, policy, robot) -> dict[str, np.ndarray]:
    base = env.unwrapped
    d = run(env, policy, robot, round(args.seconds / base.step_dt))
    period = 4.0  # 指令重采样周期（与任务配置一致）
    ended = d["tipped"] | d["timeout"]
    n_tip, n_end = int(d["tipped"].sum()), int(ended.sum())
    print(f"[diag] 训练指令分布，{base.num_envs} 个环境 × {args.seconds:g} s：结束回合 {n_end} 个，其中倾覆 {n_tip} 个"
          f"（{n_tip / max(n_end, 1) * 100:.1f}%）", flush=True)
    # 倾覆时刻（--no_tip 时为倾斜第一次超过判据的时刻）落在回合内哪一段
    if args.no_tip:
        over = d["tilt"] > args.tip_angle
        first = over & ~np.concatenate([np.zeros_like(over[:1]), over[:-1]], axis=0)  # 每次越线的第一步
        events = first & ~d["fresh"]
    else:
        events = d["tipped"]
    ep_t = d["ep_t"][events]
    since = np.mod(ep_t - 1e-6, period)
    start = ep_t <= 1.0
    after_switch = ~start & (since <= 1.0)
    print(f"[diag] {'越过判据' if args.no_tip else '倾覆'}事件 {events.sum()} 个：回合开始 1 s 内 {start.mean() * 100:.1f}%、"
          f"指令切换后 1 s 内 {after_switch.mean() * 100:.1f}%、其他 {(~start & ~after_switch).mean() * 100:.1f}%"
          f"（均匀分布时分别约 8%、17%、75%）；时刻中位 {np.median(ep_t) if ep_t.size else float('nan'):.2f} s", flush=True)
    if args.no_tip:
        # 每个完整回合（以 time_out 结束）的最大倾斜；不完整的首尾段不计
        peaks = []
        for e in range(base.num_envs):
            ends = np.flatnonzero(d["timeout"][:, e])
            for a, b in zip(ends[:-1], ends[1:]):
                peaks.append(d["tilt"][a + 2 : b, e].max())  # a+1 是重置后的第一步，跳过
        peaks = np.array(peaks)
        tipped_eps = peaks > args.tip_angle
        mid = (peaks > args.tip_angle) & (peaks <= 0.7)
        print(f"[diag] 完整回合 {peaks.size} 个：最大倾斜 > {args.tip_angle} rad 的 {tipped_eps.sum()} 个（{tipped_eps.mean() * 100:.1f}%），"
              f"其中落在 ({args.tip_angle}, 0.7] 的 {mid.sum()} 个（占越线回合 {mid.sum() / max(tipped_eps.sum(), 1) * 100:.1f}%）；"
              f"越线回合的最大倾斜 中位 {np.median(peaks[tipped_eps]) if tipped_eps.any() else float('nan'):.3f} rad；"
              f"全部回合最大倾斜 中位 {np.median(peaks):.3f}、90% {np.quantile(peaks, 0.9):.3f} rad", flush=True)
    action_stats("训练指令分布", d)
    return d


def main() -> None:
    cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    cfg.seed = args.seed
    if args.no_tip:
        cfg.terminations.tipped = None
    if args.mode == "fixed":
        cfg.commands.base_velocity.rel_standing_envs = 0.0
        cfg.commands.base_velocity.resampling_time_range = (1.0e6, 1.0e6)
        cfg.episode_length_s = args.seconds + 1.0
    agent = load_cfg_from_registry(args.task, "rsl_rl_cfg_entry_point")
    env = RslRlVecEnvWrapper(gym.make(args.task, cfg=cfg))
    runner = OnPolicyRunner(env, agent.to_dict(), log_dir=None, device=agent.device)
    runner.load(args.checkpoint)
    policy = runner.get_inference_policy(device=env.unwrapped.device)
    robot = env.unwrapped.scene["robot"]
    with torch.inference_mode():  # reset 也要在推理模式里（与 eval_base_vel.py 相同），否则原地更新推理张量会报错
        if args.mode == "fixed":
            d = fixed_mode(env, policy, robot, env.unwrapped.command_manager.get_term("base_velocity").cfg.ranges)
        else:
            d = train_mode(env, policy, robot)
    if args.dump:
        np.savez_compressed(args.dump, **d)
        print(f"[diag] 逐步数据已存到 {args.dump}", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
