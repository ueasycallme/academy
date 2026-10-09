# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-09
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""给 Cartpole 场景加三种传感器，打印各自 data 的字段形状与每步耗时（4.8）。

- ContactSensor：装在一个从 1 m 落下的小方块上（方块要开 activate_contact_sensors），记录落地后的力与空中时间；
- FrameTransformer：源是小车 cart，目标是杆 pole 上偏移 0.5 m 的点；
- TiledCamera：每个环境一台 64×64 相机，RGB + 深度。需要 --enable_cameras；加 --no_camera 时不建相机，
  加 --camera_type camera 时改用逐台渲染的 Camera（对照）。

用法::

    python sensors_demo.py --headless --enable_cameras                       # 4 个环境，64×64
    python sensors_demo.py --headless --enable_cameras --num_envs 64 --res 128
    python sensors_demo.py --headless --no_camera                            # 对照：不建相机
"""

import argparse
import sys
import time

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Isaac Lab 传感器演示")
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--res", type=int, default=64, help="相机分辨率（正方形，像素）")
parser.add_argument("--no_camera", action="store_true", help="不建相机，作为耗时对照")
parser.add_argument("--camera_type", choices=["tiled", "camera"], default="tiled", help="TiledCamera 或逐台渲染的 Camera")
parser.add_argument("--steps", type=int, default=240, help="仿真步数（物理步 1/120 s）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.sensors import CameraCfg, ContactSensorCfg, FrameTransformerCfg, TiledCameraCfg
from isaaclab.sensors.frame_transformer import OffsetCfg
from isaaclab.utils import configclass
from isaaclab_assets.robots.cartpole import CARTPOLE_CFG


@configclass
class SensorSceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(prim_path="/World/ground", spawn=sim_utils.GroundPlaneCfg())
    light = AssetBaseCfg(prim_path="/World/light", spawn=sim_utils.DomeLightCfg(intensity=2000.0))
    robot: ArticulationCfg = CARTPOLE_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    cube = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Cube",
        spawn=sim_utils.CuboidCfg(
            size=(0.1, 0.1, 0.1),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(),
            mass_props=sim_utils.MassPropertiesCfg(mass=0.2),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            activate_contact_sensors=True,  # 不开它，ContactSensor 初始化时会报 RuntimeError
        ),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(1.0, 1.0, 1.0)),
    )
    # 接触传感器：prim_path 指向要测的刚体；track_air_time 才能读空中 / 接触时间；history_length 保留最近 3 个物理步的力
    contact = ContactSensorCfg(prim_path="{ENV_REGEX_NS}/Cube", track_air_time=True, history_length=3)
    # 坐标变换：源是 cart，目标是 pole 上沿 z 偏移 0.5 m 的点（两者都必须是刚体）
    pole_tip = FrameTransformerCfg(
        prim_path="{ENV_REGEX_NS}/Robot/cart",
        target_frames=[
            FrameTransformerCfg.FrameCfg(prim_path="{ENV_REGEX_NS}/Robot/pole", name="pole_tip", offset=OffsetCfg(pos=(0.0, 0.0, 0.5)))
        ],
    )
    camera: TiledCameraCfg | CameraCfg | None = None


def main() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=1.0 / 120.0, device=args.device))
    sim.set_camera_view((3.0, 3.0, 3.0), (0.0, 0.0, 0.5))
    cfg = SensorSceneCfg(num_envs=args.num_envs, env_spacing=4.0)
    if not args.no_camera:
        # 每个环境一台相机，放在 Cartpole 正前方 3 m、高 1.5 m，朝向小车（ROS 约定的四元数 w, x, y, z）
        cam_cls = TiledCameraCfg if args.camera_type == "tiled" else CameraCfg
        cfg.camera = cam_cls(
            prim_path="{ENV_REGEX_NS}/Camera",
            offset=cam_cls.OffsetCfg(pos=(-3.0, 0.0, 1.5), rot=(0.5, -0.5, 0.5, -0.5), convention="ros"),
            data_types=["rgb", "distance_to_camera"],
            spawn=sim_utils.PinholeCameraCfg(focal_length=24.0, clipping_range=(0.1, 20.0)),
            width=args.res,
            height=args.res,
        )
    scene = InteractiveScene(cfg)
    sim.reset()

    render = not args.no_camera
    t0 = time.perf_counter()
    for _ in range(args.steps):
        scene.write_data_to_sim()
        sim.step(render=render)  # 相机的图像来自渲染，只有渲染的步才会有新图像
        scene.update(sim.get_physics_dt())
    torch.cuda.synchronize()
    dt_ms = (time.perf_counter() - t0) / args.steps * 1000
    print(f"[INFO] num_envs={args.num_envs} camera={'off' if args.no_camera else f'{args.camera_type} {args.res}x{args.res}'}：每个物理步（含渲染）{dt_ms:.2f} ms")

    c = scene["contact"].data
    print(f"[INFO] ContactSensor: net_forces_w {tuple(c.net_forces_w.shape)}，net_forces_w_history {tuple(c.net_forces_w_history.shape)}，"
          f"current_air_time {tuple(c.current_air_time.shape)}")
    print(f"[INFO]   方块静止后的法向力 Fz = {c.net_forces_w[0, 0, 2].item():.3f} N（重力 0.2 kg × 9.81 = 1.962 N），"
          f"上次空中时间 {c.last_air_time[0, 0].item():.3f} s，当前接触时间 {c.current_contact_time[0, 0].item():.3f} s")
    f = scene["pole_tip"].data
    print(f"[INFO] FrameTransformer: target_pos_source {tuple(f.target_pos_source.shape)}，target_pos_w {tuple(f.target_pos_w.shape)}，"
          f"target_frame_names {f.target_frame_names}；env_0 杆上点相对小车 {[round(v, 3) for v in f.target_pos_source[0, 0].tolist()]}")
    if not args.no_camera:
        cam = scene["camera"].data
        print(f"[INFO] {type(scene['camera']).__name__}: " + "，".join(f"{k} {tuple(v.shape)} {v.dtype}" for k, v in cam.output.items())
              + f"，intrinsic_matrices {tuple(cam.intrinsic_matrices.shape)}")
        depth = cam.output["distance_to_camera"]
        print(f"[INFO]   env_0 深度范围 {depth[0].min().item():.2f}–{depth[0][torch.isfinite(depth[0])].max().item():.2f} m")

    # 退出三步：释放 SimulationContext → flush → close
    sim.clear_all_callbacks()
    sim.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
