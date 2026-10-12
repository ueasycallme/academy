# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11（物理参数扫描选项为 6.4.5 调参轮所加，2026-10-12）
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""轮式 Galbot 被动滚子空转的探针（6.4.5，方法同 6.3.1）。

每个环境一台轮式 Galbot（浮动根），初始朝向随机。先静置 --static_s 秒（主动轮目标速度 0），
再按 omni_base.body_to_wheel 给出的轮速直行 --drive_s 秒（底盘坐标系 vx = --vx）。记录：
- 滚子转速：静置末 1 s 内被动滚子关节 |速度| 的最大值；
- 底盘漂移：静置期间根的水平位移与偏航变化；
- 直行：末 1 s 底盘坐标系下的平均速度（vx、vy、wz），与指令比；
- 每个物理步的墙上时间。

对策（--variant）：
- base：沿用 USD 里的滚子驱动（刚度 0、阻尼 0.1，6.1.2）；
- damp：滚子阻尼改为 --damping；
- friction：滚子关节静摩擦系数改为 --friction；
- limit：滚子速度上限改为 --vlimit（rad/s）；
- lock：滚子位置锁死（高刚度），相当于一个不能侧滑的普通轮子，失去全向性，只作对照。

物理参数扫描（6.4.5 调参轮，与 --variant 组合使用，每次只改一项）：--dt、--solver_pos、--contact_offset / --rest_offset（滚子碰撞体）。
行驶阶段另记：倾角超过 0.5 rad 的台数、底盘水平速度超过 --jump_speed 的台数（速度跳变：主动轮带不到这么快）、根状态出现非有限值的台数，以及三者任一的台数。

    python scripts/probe_rollers.py --headless --num_envs 256 --vx 0 --vy 0.5 --drive_s 10 --solver_pos 32

    python scripts/probe_rollers.py --headless --variant base
    python scripts/probe_rollers.py --headless --variant damp --damping 1.0
"""

import argparse
import math
import sys
import time

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="被动滚子空转的探针（6.4.5）")
parser.add_argument("--variant", choices=["base", "damp", "friction", "limit", "lock"], default="base")
parser.add_argument("--damping", type=float, default=1.0)
parser.add_argument("--friction", type=float, default=0.05)
parser.add_argument("--vlimit", type=float, default=20.0)
parser.add_argument("--num_envs", type=int, default=10)
parser.add_argument("--static_s", type=float, default=3.0)
parser.add_argument("--drive_s", type=float, default=3.0)
parser.add_argument("--vx", type=float, default=0.3)
parser.add_argument("--vy", type=float, default=0.0)
parser.add_argument("--wz", type=float, default=0.0)
parser.add_argument("--seed", type=int, default=0)
# 物理参数扫描（6.4.5 调参轮）：每次只改一项，默认值即现配置
parser.add_argument("--dt", type=float, default=1.0 / 120.0, help="物理步长（s）")
parser.add_argument("--solver_pos", type=int, default=None, help="Articulation 求解器位置迭代次数（默认沿用资产配置 16）")
parser.add_argument("--contact_offset", type=float, default=None, help="滚子碰撞体的 contactOffset（m），默认不改")
parser.add_argument("--rest_offset", type=float, default=None, help="滚子碰撞体的 restOffset（m），默认不改")
parser.add_argument("--jump_speed", type=float, default=1.5,
                    help="底盘水平速度超过它算一次速度跳变（m/s）。主动轮 6 rad/s 只能带到约 0.9 m/s")
parser.add_argument("--roller_pairs", choices=["keep", "remove"], default="keep",
                    help="remove：在场景里清掉资产写入的滚子过滤对（它们都写在滚子 prim 上），作对照")
parser.add_argument("--self_collision", choices=["on", "off"], default="on",
                    help="整机自碰撞。滚子的碰撞球（半径 8 cm、离轮轴 2.5 cm）同一轮内彼此重叠，开着自碰撞时会互相顶")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch  # noqa: E402

import isaaclab.sim as sim_utils  # noqa: E402
import isaaclab.utils.math as math_utils  # noqa: E402
from isaaclab.actuators import ImplicitActuatorCfg  # noqa: E402
from isaaclab.assets import ArticulationCfg, AssetBaseCfg  # noqa: E402
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg  # noqa: E402
from isaaclab.utils import configclass  # noqa: E402

from galbot_academy.assets.galbot import GALBOT_ONE_GOLF_WHEELED_CFG  # noqa: E402
from galbot_academy.assets.omni_base import WHEEL_JOINTS, body_to_wheel  # noqa: E402

DT = args.dt
ROLLERS = "wheel_[1-4]_passive_.*"


def robot_cfg() -> ArticulationCfg:
    rollers = {
        "base": ImplicitActuatorCfg(joint_names_expr=[ROLLERS], stiffness=None, damping=None),
        "damp": ImplicitActuatorCfg(joint_names_expr=[ROLLERS], stiffness=0.0, damping=args.damping),
        "friction": ImplicitActuatorCfg(joint_names_expr=[ROLLERS], stiffness=None, damping=None, friction=args.friction),
        "limit": ImplicitActuatorCfg(joint_names_expr=[ROLLERS], stiffness=None, damping=None, velocity_limit_sim=args.vlimit),
        "lock": ImplicitActuatorCfg(joint_names_expr=[ROLLERS], stiffness=1.0e4, damping=10.0),
    }[args.variant]
    cfg = GALBOT_ONE_GOLF_WHEELED_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    cfg.actuators = {**cfg.actuators, "rollers": rollers}
    if args.solver_pos is not None:
        cfg.spawn = cfg.spawn.replace(
            articulation_props=cfg.spawn.articulation_props.replace(solver_position_iteration_count=args.solver_pos))
    if args.self_collision == "off":
        cfg.spawn = cfg.spawn.replace(
            articulation_props=cfg.spawn.articulation_props.replace(enabled_self_collisions=False))
    return cfg


@configclass
class SceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(prim_path="/World/ground", spawn=sim_utils.GroundPlaneCfg())
    robot: ArticulationCfg = robot_cfg()


def report_geometry(stage) -> None:
    """读回 env_0 一个滚子的碰撞体：类型、半径、球心相对所属轮心的距离，以及该滚子上写了几对过滤对。"""
    from pxr import Gf, Usd, UsdGeom, UsdPhysics

    root = "/World/envs/env_0/Robot"
    roller = stage.GetPrimAtPath(f"{root}/wheel_1_passive_0")
    wheel = stage.GetPrimAtPath(f"{root}/wheel_1")
    cache = UsdGeom.XformCache()
    for prim in Usd.PrimRange(roller, Usd.TraverseInstanceProxies()):
        if prim.HasAPI(UsdPhysics.CollisionAPI) and prim.IsA(UsdGeom.Sphere):
            r = UsdGeom.Sphere(prim).GetRadiusAttr().Get()
            scale = Gf.Transform(cache.GetLocalToWorldTransform(prim)).GetScale()
            c = cache.GetLocalToWorldTransform(prim).ExtractTranslation()
            w = cache.GetLocalToWorldTransform(wheel).ExtractTranslation()
            pairs = len(UsdPhysics.FilteredPairsAPI(roller).GetFilteredPairsRel().GetTargets()) if roller.HasAPI(UsdPhysics.FilteredPairsAPI) else 0
            print(f"[6.4.5] 滚子碰撞体 {prim.GetPath().name}：球，半径 {r * scale[0]:.4f} m，球心离轮心 {(c - w).GetLength():.4f} m；"
                  f"wheel_1_passive_0 上的过滤对 {pairs} 个", flush=True)
            return
    print("[6.4.5] 没找到滚子的球形碰撞体", flush=True)


def set_roller_offsets(stage) -> int:
    """改所有滚子碰撞体的 contactOffset / restOffset。碰撞体在实例内部（6.1.4），先把实例 prim 设为非实例才能写。"""
    from pxr import PhysxSchema, Usd, UsdPhysics

    rollers = [p for p in stage.Traverse() if "_passive_" in p.GetName() and p.GetPath().pathString.count("/") == 5]
    for roller in rollers:
        for prim in Usd.PrimRange(roller, Usd.TraverseInstanceProxies()):
            if prim.IsInstance():
                stage.GetPrimAtPath(prim.GetPath()).SetInstanceable(False)
    n = 0
    for roller in rollers:
        for prim in Usd.PrimRange(roller):
            if prim.HasAPI(UsdPhysics.CollisionAPI):
                api = PhysxSchema.PhysxCollisionAPI.Apply(prim)
                if n == 0:
                    print(f"[6.4.5] 滚子碰撞体原值 contactOffset {api.GetContactOffsetAttr().Get()}、restOffset {api.GetRestOffsetAttr().Get()}", flush=True)
                if args.contact_offset is not None:
                    api.CreateContactOffsetAttr().Set(args.contact_offset)
                if args.rest_offset is not None:
                    api.CreateRestOffsetAttr().Set(args.rest_offset)
                n += 1
    return n


def main() -> None:
    torch.manual_seed(args.seed)
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=DT, device=args.device))
    scene = InteractiveScene(SceneCfg(num_envs=args.num_envs, env_spacing=3.0))
    report_geometry(sim.stage)
    if args.contact_offset is not None or args.rest_offset is not None:
        print(f"[6.4.5] 改了 {set_roller_offsets(sim.stage)} 个滚子碰撞体的 offset（contact {args.contact_offset}，rest {args.rest_offset}）", flush=True)
    if args.roller_pairs == "remove":
        from pxr import UsdPhysics

        n = 0
        for prim in sim.stage.Traverse():
            if "_passive_" in prim.GetName() and prim.HasAPI(UsdPhysics.FilteredPairsAPI):
                UsdPhysics.FilteredPairsAPI(prim).GetFilteredPairsRel().SetTargets([])  # 显式空列表才能盖过资产里的值（6.1.4）
                n += 1
        print(f"[6.4.5] 清掉了 {n} 个滚子 prim 上的过滤对", flush=True)
    sim.reset()
    robot = scene["robot"]
    d = robot.data
    wheel_ids, _ = robot.find_joints(WHEEL_JOINTS, preserve_order=True)
    roller_ids, _ = robot.find_joints([ROLLERS])
    print(f"[6.4.5] 主动轮 力矩上限 {d.joint_effort_limits[0, wheel_ids].tolist()}，速度上限 {d.joint_vel_limits[0, wheel_ids].tolist()}，"
          f"阻尼 {robot.root_physx_view.get_dof_dampings()[0, wheel_ids].tolist()}；滚子 力矩上限 {d.joint_effort_limits[0, roller_ids[0]].item()}，"
          f"阻尼 {robot.root_physx_view.get_dof_dampings()[0, roller_ids[0]].item()}，质量 {robot.root_physx_view.get_masses()[0, robot.find_bodies('wheel_1_passive_0')[0][0]].item():.4f} kg", flush=True)
    # 初始：默认关节姿态，朝向随机（绕 z）
    root = d.default_root_state.clone()
    root[:, :3] += scene.env_origins
    yaw = (torch.rand(args.num_envs, device=sim.device) * 2 - 1) * math.pi
    root[:, 3:7] = math_utils.quat_from_euler_xyz(torch.zeros_like(yaw), torch.zeros_like(yaw), yaw)
    robot.write_root_state_to_sim(root)
    robot.write_joint_state_to_sim(d.default_joint_pos, d.default_joint_vel)
    robot.set_joint_position_target(d.default_joint_pos)

    def run(seconds: float, wheel_target: list[float]):
        """走 seconds 秒；返回 (末 1 s 滚子 |速度| 最大值, 末 1 s 底盘坐标系平均速度 [vx, vy, wz], 每步 ms)。"""
        vel = torch.zeros(args.num_envs, robot.num_joints, device=sim.device)
        vel[:, wheel_ids] = torch.tensor(wheel_target, device=sim.device)
        robot.set_joint_velocity_target(vel)
        n, last = round(seconds / DT), round(1.0 / DT)
        roller_max = torch.zeros(args.num_envs, device=sim.device)
        tilt_max = torch.zeros(args.num_envs, device=sim.device)
        speed_max = torch.zeros(args.num_envs, device=sim.device)
        bad = torch.zeros(args.num_envs, dtype=torch.bool, device=sim.device)  # 根状态出现过非有限值
        tip_t = torch.full((args.num_envs,), float("nan"), device=sim.device)  # 倾角第一次超过 0.5 rad 的时刻（s）
        p_start = d.root_pos_w[:, :2].clone()
        tip_dist = torch.full((args.num_envs,), float("nan"), device=sim.device)  # 那一刻离出发点的水平距离（m）
        twist = torch.zeros(args.num_envs, 3, device=sim.device)
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        for k in range(n):
            scene.write_data_to_sim()
            sim.step(render=False)
            scene.update(DT)
            tilt_max = torch.maximum(tilt_max, torch.acos((-d.projected_gravity_b[:, 2]).clamp(-1.0, 1.0)))  # 底盘倾角
            speed_max = torch.maximum(speed_max, d.root_lin_vel_w[:, :2].norm(dim=1))
            bad |= ~torch.isfinite(d.root_state_w).all(dim=1)
            new_tip = torch.isnan(tip_t) & (tilt_max > 0.5)
            tip_t[new_tip] = (k + 1) * DT
            tip_dist[new_tip] = (d.root_pos_w[new_tip, :2] - p_start[new_tip]).norm(dim=1)
            if k >= n - last:
                roller_max = torch.maximum(roller_max, d.joint_vel[:, roller_ids].abs().max(dim=1).values)
                twist += torch.cat([d.root_lin_vel_b[:, :2], d.root_ang_vel_b[:, 2:3]], dim=1) / last
        torch.cuda.synchronize()
        run.tilt, run.speed, run.bad, run.tip_t, run.tip_dist = tilt_max, speed_max, bad, tip_t, tip_dist
        return roller_max, twist, (time.perf_counter() - t0) / n * 1000

    p0, yaw0 = d.root_pos_w[:, :2].clone(), math_utils.euler_xyz_from_quat(d.root_quat_w)[2].clone()
    r_static, _, ms = run(args.static_s, [0.0] * 4)
    drift = (d.root_pos_w[:, :2] - p0).norm(dim=1)
    dyaw = math_utils.wrap_to_pi(math_utils.euler_xyz_from_quat(d.root_quat_w)[2] - yaw0).abs()
    finite = bool(torch.isfinite(d.joint_pos).all())
    target = body_to_wheel(args.vx, args.vy, args.wz)
    r_drive, twist, ms2 = run(args.drive_s, target)
    med = lambda x: x.nanmedian().item()  # noqa: E731  有发散的台时，中位数只算有限值
    print(f"[6.4.5] variant {args.variant}（damping {args.damping}，friction {args.friction}，vlimit {args.vlimit}，自碰撞 {args.self_collision}，滚子过滤对 {args.roller_pairs}），"
          f"{args.num_envs} 台，数值有限 {finite}", flush=True)
    print(f"[6.4.5] 静置 {args.static_s:g} s：滚子 |速度| 中位 {med(r_static):.1f}、最大 {r_static.max().item():.1f} rad/s；"
          f"漂移 中位 {med(drift) * 100:.2f}、最大 {drift.max().item() * 100:.2f} cm；偏航变化最大 {math.degrees(dyaw.max().item()):.2f}°；"
          f"每物理步 {ms:.2f} ms", flush=True)
    print(f"[6.4.5] 直行 指令 vx {args.vx} vy {args.vy} wz {args.wz}（轮速 {[round(w, 2) for w in target]} rad/s）："
          f"实际 vx 中位 {med(twist[:, 0]):.3f}、vy {med(twist[:, 1]):.3f} m/s、wz {med(twist[:, 2]):.3f} rad/s；"
          f"滚子 |速度| 中位 {med(r_drive):.1f} rad/s；底盘最大倾角 {math.degrees(run.tilt.nan_to_num(0.0).max().item()):.1f}°（超过 0.5 rad 的 {int((run.tilt > 0.5).sum())} 台）；水平速度超过 {args.jump_speed:g} m/s 的 {int((run.speed > args.jump_speed).sum())} 台；根状态发散（非有限）的 {int(run.bad.sum())} 台；三者任一的 {int(((run.tilt > 0.5) | (run.speed > args.jump_speed) | run.bad).sum())} / {args.num_envs} 台；每物理步 {ms2:.2f} ms", flush=True)
    tt, td = run.tip_t[~torch.isnan(run.tip_t)], run.tip_dist[~torch.isnan(run.tip_t)]
    if tt.numel():
        edges = torch.linspace(0, args.drive_s, 6, device=sim.device)
        counts = [int(((tt > a) & (tt <= b)).sum()) for a, b in zip(edges[:-1], edges[1:])]
        print(f"[6.4.5] 行驶中倾角越过 0.5 rad 的时刻：中位 {tt.median().item():.2f} s，按 {args.drive_s / 5:g} s 分段 {counts}；"
              f"越过时离出发点 中位 {td.median().item():.2f}、最小 {td.min().item():.2f}、最大 {td.max().item():.2f} m", flush=True)
    sim.clear_all_callbacks()  # 退出三步：不先释放 SimulationContext，close() 会卡住（本站实测）
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
