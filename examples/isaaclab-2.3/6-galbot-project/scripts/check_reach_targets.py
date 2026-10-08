# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""reach 的目标能不能到（6.4.1）。

按 Galbot-Reach-v0 的命令范围采样 N 个目标（位置在长方体内均匀采样，姿态固定），每台机器人对一个目标做
阻尼最小二乘的逆运动学（只动右臂，关节夹在限位内，只算运动学、不推进物理），统计收敛到误差阈值以内的比例。
加 --position_only 时只要求位置。

    python scripts/check_reach_targets.py --headless
    python scripts/check_reach_targets.py --headless --position_only
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="reach 目标的可达性")
parser.add_argument("--num_envs", type=int, default=1024)
parser.add_argument("--iters", type=int, default=300)
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--position_only", action="store_true")
parser.add_argument("--box", type=float, nargs=6, default=None, metavar=("X0", "X1", "Y0", "Y1", "Z0", "Z1"),
                    help="改用这个位置范围（相对根），不给时用任务的命令范围")
parser.add_argument("--restarts", type=int, default=0, help="对未收敛的目标，再从随机臂姿重新做 IK 的次数")
parser.add_argument("--pos_tol", type=float, default=0.01, help="位置误差阈值（m）")
parser.add_argument("--rot_tol", type=float, default=0.05, help="姿态误差阈值（rad）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils import configclass
from isaaclab.utils.math import combine_frame_transforms, compute_pose_error, quat_from_euler_xyz

from galbot_academy.assets.galbot import GALBOT_ONE_GOLF_CFG, REACH_ARM, REACH_EE_BODY, REACH_EE_OFFSET_POS, REACH_EE_OFFSET_ROT
from galbot_academy.tasks.manager_based.reach.reach_env_cfg import CommandsCfg


@configclass
class KinematicsSceneCfg(InteractiveSceneCfg):
    light = AssetBaseCfg(prim_path="/World/light", spawn=sim_utils.DomeLightCfg())
    robot = GALBOT_ONE_GOLF_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")


def skew(v: torch.Tensor) -> torch.Tensor:
    z = torch.zeros_like(v[:, 0])
    return torch.stack([torch.stack([z, -v[:, 2], v[:, 1]], -1), torch.stack([v[:, 2], z, -v[:, 0]], -1),
                        torch.stack([-v[:, 1], v[:, 0], z], -1)], 1)


def main() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=1 / 120, device=args.device))
    scene = InteractiveScene(KinematicsSceneCfg(num_envs=args.num_envs, env_spacing=3.0))
    sim.reset()
    robot = scene["robot"]
    n, dev = args.num_envs, robot.device
    arm = [i for i, name in enumerate(robot.joint_names) if name.startswith(f"{REACH_ARM}_arm_joint")]
    body = robot.body_names.index(REACH_EE_BODY)
    lo, hi = robot.data.soft_joint_pos_limits[:, arm, 0], robot.data.soft_joint_pos_limits[:, arm, 1]

    # 目标：与任务的命令范围相同（根坐标系）
    r = CommandsCfg().ee_pose.ranges
    if args.box is not None:
        r.pos_x, r.pos_y, r.pos_z = tuple(args.box[0:2]), tuple(args.box[2:4]), tuple(args.box[4:6])
    gen = torch.Generator(device=dev).manual_seed(args.seed)
    u = torch.rand((n, 3), generator=gen, device=dev)
    pos_b = torch.stack([r.pos_x[0] + (r.pos_x[1] - r.pos_x[0]) * u[:, 0], r.pos_y[0] + (r.pos_y[1] - r.pos_y[0]) * u[:, 1],
                         r.pos_z[0] + (r.pos_z[1] - r.pos_z[0]) * u[:, 2]], -1)
    rpy = torch.tensor([r.roll[0], r.pitch[0], r.yaw[0]], device=dev).expand(n, 3)
    quat_b = quat_from_euler_xyz(rpy[:, 0], rpy[:, 1], rpy[:, 2])
    tgt_p, tgt_q = combine_frame_transforms(robot.data.root_pos_w, robot.data.root_quat_w, pos_b, quat_b)

    off_p = torch.tensor(REACH_EE_OFFSET_POS, device=dev).expand(n, 3)
    off_q = torch.tensor(REACH_EE_OFFSET_ROT, device=dev).expand(n, 4)
    lam = 0.05

    def solve(q):
        for _ in range(args.iters):
            robot.write_joint_state_to_sim(q, torch.zeros_like(q))
            sim.forward()
            scene.update(0.0)
            lp, lq = robot.data.body_pos_w[:, body], robot.data.body_quat_w[:, body]
            tp, tq = combine_frame_transforms(lp, lq, off_p, off_q)
            e_p, e_r = compute_pose_error(tp, tq, tgt_p, tgt_q)  # 从当前到目标
            # 固定底座：雅可比的刚体维不含根，所以下标减 1；关节维与关节下标一致
            J = robot.root_physx_view.get_jacobians()[:, body - 1][:, :, arm]
            J_lin = J[:, :3] - skew(tp - lp) @ J[:, 3:]  # 把刚体原点的线速度换算到 TCP
            if args.position_only:
                Jt, e = J_lin, e_p
            else:
                Jt, e = torch.cat([J_lin, J[:, 3:]], 1), torch.cat([e_p, e_r], -1)
            A = Jt @ Jt.transpose(1, 2) + lam**2 * torch.eye(Jt.shape[1], device=dev)
            dq = (Jt.transpose(1, 2) @ torch.linalg.solve(A, e.unsqueeze(-1))).squeeze(-1)
            q[:, arm] = torch.clamp(q[:, arm] + dq.clamp(-0.2, 0.2), lo, hi)
        return q, e_p, e_r

    def converged(e_p, e_r):
        pe, re = e_p.norm(dim=-1), e_r.norm(dim=-1)
        return (pe < args.pos_tol) if args.position_only else (pe < args.pos_tol) & (re < args.rot_tol)

    q, e_p, e_r = solve(robot.data.default_joint_pos.clone())  # 从默认姿态出发
    ok = converged(e_p, e_r)
    ok_first = ok.clone()
    for _ in range(args.restarts):  # 只替换仍未收敛的那些
        q0 = robot.data.default_joint_pos.clone()
        q0[:, arm] = lo + (hi - lo) * torch.rand((n, len(arm)), generator=gen, device=dev)
        _, e_p2, e_r2 = solve(q0)
        better = ~ok & converged(e_p2, e_r2)
        e_p[better], e_r[better] = e_p2[better], e_r2[better]
        ok |= better
    pe, re = e_p.norm(dim=-1), e_r.norm(dim=-1)
    print(f"{n} 个目标（种子 {args.seed}），{'只要求位置' if args.position_only else '位置 + 固定姿态'}，IK {args.iters} 次迭代：")
    print(f"  收敛（位置 < {args.pos_tol} m" + ("" if args.position_only else f"，姿态 < {args.rot_tol} rad") + f"）：{ok.float().mean().item() * 100:.1f}%")
    print(f"  位置误差中位数 {pe.median().item():.4f} m，95% 分位 {pe.quantile(0.95).item():.4f} m；"
          f"姿态误差中位数 {re.median().item():.4f} rad，95% 分位 {re.quantile(0.95).item():.4f} rad")
    if args.restarts:
        print(f"  其中从默认姿态出发即收敛 {ok_first.float().mean().item() * 100:.1f}%，再随机重启 {args.restarts} 次后共 {ok.float().mean().item() * 100:.1f}%")
    for k, axis in enumerate("xyz"):  # 按坐标分 3 段看未收敛的比例
        edges = torch.quantile(pos_b[:, k], torch.tensor([0.0, 1 / 3, 2 / 3, 1.0], device=dev))
        parts = []
        for a, b in zip(edges[:-1].tolist(), edges[1:].tolist()):
            m = (pos_b[:, k] >= a) & (pos_b[:, k] <= b)
            parts.append(f"[{a:.2f},{b:.2f}] {(~ok[m]).float().mean().item() * 100:.0f}%")
        print(f"  未收敛比例按 {axis} 分段：" + "，".join(parts))
    bad = pos_b[~ok]
    if len(bad):
        print(f"  未收敛的目标（相对根）：x 均值 {bad[:, 0].mean().item():.2f}，y 均值 {bad[:, 1].mean().item():.2f}，z 均值 {bad[:, 2].mean().item():.2f}"
              f"（全部目标均值 {pos_b[:, 0].mean().item():.2f} / {pos_b[:, 1].mean().item():.2f} / {pos_b[:, 2].mean().item():.2f}）")

    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
