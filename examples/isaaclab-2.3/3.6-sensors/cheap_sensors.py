# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""三种不走渲染的传感器：RayCaster、Imu、ContactSensor（3.6）。

每个环境一个从 2 m 落下的方块，三种传感器都装在方块上：
- RayCaster：向下的 11×11 网格射线（间距 0.1 m），只对地面这一个网格求交；
- Imu：方块质心处；
- ContactSensor：方块的接触合力。

脚本做三件事：
1. 打印各传感器 data 的字段形状与 update_period；
2. 自由落体检查：方块下落时，理想 IMU 的线加速度读数应为 0（重力偏置 +9.81 抵消下落的 −9.81）。
   分别"每个物理步读一次"和"每 4 个物理步读一次"（相当于 decimation 4 的环境每个控制步读一次观测），对比读数；
3. 计时：方块落地静止后，每个物理步只读其中一种传感器的 data，与"不读"对比，三轮交替，报每步多花的时间。
   加 --no_sensors 时不建传感器，作为对照。

    python cheap_sensors.py --headless                      # 1024 个环境
    python cheap_sensors.py --headless --no_sensors         # 对照
    python cheap_sensors.py --headless --imu_history 1      # Imu 每个物理步都更新，看自由落体读数
"""

import argparse
import sys
import time

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="RayCaster / Imu / ContactSensor 的形状、时序与代价")
parser.add_argument("--num_envs", type=int, default=1024)
parser.add_argument("--steps", type=int, default=300, help="计时时每轮的物理步数")
parser.add_argument("--no_sensors", action="store_true", help="不建传感器（对照）")
parser.add_argument("--imu_history", type=int, default=0, help="Imu 的 history_length；> 0 时每个物理步都更新（对照自由落体读数）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg, RigidObjectCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg, ImuCfg, RayCasterCfg, patterns
from isaaclab.utils import configclass

DT = 1.0 / 120.0


@configclass
class SceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(prim_path="/World/ground", spawn=sim_utils.GroundPlaneCfg())
    light = AssetBaseCfg(prim_path="/World/light", spawn=sim_utils.DomeLightCfg(intensity=2000.0))
    cube = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Cube",
        spawn=sim_utils.CuboidCfg(
            size=(0.1, 0.1, 0.1),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(),
            mass_props=sim_utils.MassPropertiesCfg(mass=0.2),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            activate_contact_sensors=True,
        ),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0.0, 0.0, 2.0)),
    )
    height_scan: RayCasterCfg | None = RayCasterCfg(
        prim_path="{ENV_REGEX_NS}/Cube",
        mesh_prim_paths=["/World/ground"],  # 只能一个网格，且按静态网格处理（ray_caster.py L164–L167）
        pattern_cfg=patterns.GridPatternCfg(resolution=0.1, size=(1.0, 1.0)),
        ray_alignment="yaw",
    )
    imu: ImuCfg | None = ImuCfg(prim_path="{ENV_REGEX_NS}/Cube")
    contact: ContactSensorCfg | None = ContactSensorCfg(prim_path="{ENV_REGEX_NS}/Cube")


def step(scene, sim):
    scene.write_data_to_sim()
    sim.step(render=False)
    scene.update(DT)


def drop(scene, sim):
    """方块回到 2 m 高处、速度清零，并重置传感器。"""
    cube = scene["cube"]
    state = cube.data.default_root_state.clone()
    state[:, :3] += scene.env_origins
    cube.write_root_state_to_sim(state)
    scene.reset()


def free_fall(scene, sim, read_every: int) -> list[float]:
    """下落 48 个物理步（0.4 s，方块还在空中），每 read_every 步读一次 IMU，返回 env_0 的 z 向线加速度读数。"""
    drop(scene, sim)
    out = []
    for k in range(1, 49):
        step(scene, sim)
        if k % read_every == 0:
            out.append(scene["imu"].data.lin_acc_b[0, 2].item())
    return out


def timed(scene, sim, read) -> float:
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(args.steps):
        step(scene, sim)
        if read is not None:
            read()
    torch.cuda.synchronize()
    return (time.perf_counter() - t0) / args.steps * 1000


def main() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=DT, device=args.device))
    cfg = SceneCfg(num_envs=args.num_envs, env_spacing=2.0)
    if args.no_sensors:
        cfg.height_scan = cfg.imu = cfg.contact = None
    else:
        cfg.imu.history_length = args.imu_history
    scene = InteractiveScene(cfg)
    sim.reset()
    names = [] if args.no_sensors else ["height_scan", "imu", "contact"]

    # 1. 形状与更新周期
    for _ in range(2):
        step(scene, sim)
    for n in names:
        s = scene[n]
        fields = {k: tuple(v.shape) for k, v in vars(s.data).items() if isinstance(v, torch.Tensor)}
        print(f"[3.6] {type(s).__name__}：update_period {s.cfg.update_period}；" + "，".join(f"{k} {v}" for k, v in fields.items()), flush=True)

    # 2. 自由落体：理想读数为 0
    if not args.no_sensors:
        for every in (1, 4):
            r = free_fall(scene, sim, every)
            print(f"[3.6] 自由落体，每 {every} 个物理步读一次 IMU：lin_acc_b z 的读数（m/s²）"
                  f"第 1 次 {r[0]:+.2f}，其余 {min(r[1:]):+.2f} … {max(r[1:]):+.2f}（{len(r) - 1} 次）", flush=True)

    # 3. 计时：落地静止后
    drop(scene, sim)
    for _ in range(240):
        step(scene, sim)
    readers = {"不读": None}
    for n in names:
        readers[f"读 {n}"] = (lambda n=n: scene[n].data)
    res = {k: [] for k in readers}
    for _ in range(3):
        for k, fn in readers.items():
            res[k].append(timed(scene, sim, fn))
    base = sorted(res["不读"])[1]
    for k, v in res.items():
        med = sorted(v)[1]
        print(f"[3.6] num_envs {args.num_envs}，{k}：每个物理步 {med:.3f} ms（3 轮 {min(v):.3f}–{max(v):.3f}），"
              f"比不读多 {med - base:+.3f} ms", flush=True)
    if "contact" in names:
        print(f"[3.6] 静止后 env_0 接触合力 Fz {scene['contact'].data.net_forces_w[0, 0, 2].item():.3f} N（0.2 kg × 9.81 = 1.962）；"
              f"射线命中点高度 {scene['height_scan'].data.ray_hits_w[0, :, 2].mean().item():.4f} m；"
              f"IMU lin_acc_b z {scene['imu'].data.lin_acc_b[0, 2].item():+.2f} m/s²", flush=True)

    sim.clear_all_callbacks()
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
