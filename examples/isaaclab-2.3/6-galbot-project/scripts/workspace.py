# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-08
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""reach 手臂的可达范围（6.2.1）。

其余关节保持默认姿态，reach 手臂的 7 个关节在限位内均匀采样，正运动学得到 TCP 位置（相对机器人根），统计：
- TCP 的包围盒与分位数，以及 5 cm 体素的占据情况；
- 一个"每格都有足够样本"的长方体作为 6.4.1 目标采样范围的建议；
- 所有刚体离根的最大水平距离，用来定 env_spacing。

不放地面、关掉自碰撞（只算运动学），每批 N 台机器人各取一组姿态，写入后调用一次 sim.forward() 更新连杆位姿。

    python scripts/workspace.py --headless
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="手臂可达范围")
parser.add_argument("--num_envs", type=int, default=1024)
parser.add_argument("--batches", type=int, default=16, help="采样批数，总样本数 = num_envs × batches")
parser.add_argument("--seed", type=int, default=0)
parser.add_argument("--voxel", type=float, default=0.05, help="体素边长（m）")
parser.add_argument("--min_count", type=int, default=20, help="建议范围内每个体素至少要有的样本数")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils import configclass
from isaaclab.utils.math import combine_frame_transforms

from galbot_academy.assets.galbot import (
    GALBOT_ONE_GOLF_CFG,
    REACH_ARM,
    REACH_EE_BODY,
    REACH_EE_OFFSET_POS,
    REACH_EE_OFFSET_ROT,
)


@configclass
class KinematicsSceneCfg(InteractiveSceneCfg):
    """只有机器人：不放地面，关掉自碰撞（这里只算运动学）。"""

    light = AssetBaseCfg(prim_path="/World/light", spawn=sim_utils.DomeLightCfg())
    robot = GALBOT_ONE_GOLF_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Robot",
        spawn=GALBOT_ONE_GOLF_CFG.spawn.replace(
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(enabled_self_collisions=False)
        ),
    )


def main() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=1 / 120, device=args.device))
    scene = InteractiveScene(KinematicsSceneCfg(num_envs=args.num_envs, env_spacing=3.0))
    sim.reset()
    robot = scene["robot"]
    names = robot.joint_names
    arm = [i for i, n in enumerate(names) if n.startswith(f"{REACH_ARM}_arm_joint")]
    ee = robot.body_names.index(REACH_EE_BODY)
    lo, hi = robot.data.soft_joint_pos_limits[0, arm, 0], robot.data.soft_joint_pos_limits[0, arm, 1]
    gen = torch.Generator(device=robot.device).manual_seed(args.seed)
    off_p = torch.tensor(REACH_EE_OFFSET_POS, device=robot.device).repeat(args.num_envs, 1)
    off_q = torch.tensor(REACH_EE_OFFSET_ROT, device=robot.device).repeat(args.num_envs, 1)

    tcp, reach_xy = [], []
    for b in range(args.batches + 1):
        q = robot.data.default_joint_pos.clone()
        if b > 0:  # 第 0 批是默认姿态
            q[:, arm] = lo + (hi - lo) * torch.rand((args.num_envs, len(arm)), generator=gen, device=robot.device)
        robot.write_joint_state_to_sim(q, torch.zeros_like(q))
        sim.forward()  # 只更新运动学，不推进时间
        scene.update(0.0)
        root = robot.data.root_pos_w
        p, _ = combine_frame_transforms(robot.data.body_pos_w[:, ee], robot.data.body_quat_w[:, ee], off_p, off_q)
        if b == 0:
            print(f"默认姿态下 TCP 相对根：{[round(x, 3) for x in (p[0] - root[0]).tolist()]} m")
            continue
        tcp.append(p - root)
        reach_xy.append((robot.data.body_pos_w[..., :2] - root[:, None, :2]).norm(dim=-1).max(dim=1).values)
    tcp = torch.cat(tcp)
    n = len(tcp)
    qs = torch.tensor([0.05, 0.5, 0.95], device=tcp.device)
    print(f"\n样本 {n} 个（{REACH_ARM} 臂 7 个关节在限位内均匀采样，种子 {args.seed}）。TCP 相对根（m）：")
    for k, axis in enumerate("xyz"):
        v = tcp[:, k]
        p5, p50, p95 = torch.quantile(v, qs).tolist()
        print(f"  {axis}: 最小 {v.min().item():+.3f}  5% {p5:+.3f}  中位 {p50:+.3f}  95% {p95:+.3f}  最大 {v.max().item():+.3f}")
    print(f"  TCP 离根的水平距离：最大 {tcp[:, :2].norm(dim=-1).max().item():.3f} m")
    print(f"所有刚体离根的最大水平距离：{torch.cat(reach_xy).max().item():.3f} m（定 env_spacing 用）")

    # 体素占据：在机器人前方（x > 0.2）找一个每格样本数都 ≥ min_count 的长方体
    vox = torch.floor(tcp / args.voxel).long()
    keys, counts = torch.unique(vox, dim=0, return_counts=True)
    occ = {tuple(k.tolist()): c.item() for k, c in zip(keys, counts)}
    print(f"\n{args.voxel * 100:.0f} cm 体素：被占据 {len(occ)} 个，样本数中位数 {counts.float().median().item():.0f}")

    def box_ok(x0, x1, y0, y1, z0, z1) -> bool:
        v = args.voxel
        for ix in range(round(x0 / v), round(x1 / v)):
            for iy in range(round(y0 / v), round(y1 / v)):
                for iz in range(round(z0 / v), round(z1 / v)):
                    if occ.get((ix, iy, iz), 0) < args.min_count:
                        return False
        return True

    # 候选：以默认 TCP 附近为中心，逐步扩大各边，直到不再满足
    best = None
    for dx in [0.1, 0.15, 0.2, 0.25, 0.3]:
        for dy in [0.1, 0.15, 0.2, 0.25, 0.3]:
            for dz in [0.1, 0.15, 0.2, 0.25, 0.3]:
                for cx in [0.4, 0.45, 0.5, 0.55]:
                    for cy in [-0.4, -0.3, -0.2, -0.1]:
                        for cz in [1.0, 1.1, 1.2, 1.3]:
                            b = (cx - dx, cx + dx, cy - dy, cy + dy, cz - dz, cz + dz)
                            if box_ok(*b):
                                vol = 8 * dx * dy * dz
                                if best is None or vol > best[0]:
                                    best = (vol, b)
    if best:
        b = best[1]
        print(f"建议的目标采样范围（每个 {args.voxel * 100:.0f} cm 体素至少 {args.min_count} 个样本）："
              f"x [{b[0]:.2f}, {b[1]:.2f}]，y [{b[2]:.2f}, {b[3]:.2f}]，z [{b[4]:.2f}, {b[5]:.2f}] m（相对根）")

    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
