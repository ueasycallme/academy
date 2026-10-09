# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-09
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""检查腕部相机、FrameTransformer、指尖接触传感器（6.2.2）：读出数据、核对坐标系、测代价。不训练。

默认（验证模式）：lift 场景 + 三种传感器，机器人保持默认姿态。
1. 相机：打印位姿（与 link7 + URDF 偏移对照）与内参，保存 env_0 的 RGB 与深度图；把方块中心按内参投影到图像上，
   与图中红色像素的重心对照，两者对上说明相机朝向与坐标系约定没写反；
2. FrameTransformer：TCP 的世界坐标（与 6.2.1 对照）；方块在 TCP 系里的位置，与用世界位姿手算的结果对照；
3. 接触传感器：脚本化抓取（同 check_grasp：把方块钉在 TCP 处 → 闭合 → 松开方块只靠夹持 → 张开），
   每 0.1 s 打印两个指尖与方块的接触力。

    python scripts/check_sensors.py --headless --enable_cameras
    python scripts/check_sensors.py --headless --enable_cameras --out generated/sensors

代价模式（--bench）：只加一种传感器，按 lift 环境的节奏（4 个物理步 + 1 次渲染为一个环境步）计时，并读取传感器数据。
显存与主机内存请用外部工具按进程测量（CONVENTIONS 第 5 节）。

    python scripts/check_sensors.py --headless --bench none --num_envs 256
    python scripts/check_sensors.py --headless --bench frame --num_envs 256      # lift 自带的 ee_frame
    python scripts/check_sensors.py --headless --bench contact --num_envs 256
    python scripts/check_sensors.py --headless --enable_cameras --bench cam64 --num_envs 256
"""

import argparse
import os
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="检查腕部相机、FrameTransformer 与接触传感器")
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--resolution", type=int, default=128, help="验证模式下相机的分辨率（正方形）")
parser.add_argument("--out", default="generated/sensors", help="验证模式保存图像的目录")
parser.add_argument("--bench", choices=["none", "frame", "contact", "cam64", "cam128"], default=None,
                    help="代价模式：只加这一种传感器并计时")
parser.add_argument("--steps", type=int, default=300, help="代价模式计时的环境步数")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import time

import torch

import isaaclab.sim as sim_utils
from isaaclab.scene import InteractiveScene
from isaaclab.utils.math import combine_frame_transforms, matrix_from_quat, subtract_frame_transforms

from galbot_academy.assets.galbot import REACH_ARM, REACH_EE_BODY
from galbot_academy.scenes.sensors import WRIST_CAMERA_POS, WRIST_CAMERA_ROT, make_sensor_scene_cfg
from galbot_academy.tasks.manager_based.lift.lift_env_cfg import GRIPPER_CLOSED, GRIPPER_OPEN

PHYSICS_DT = 1 / 120  # 与 lift 环境相同（lift_env_cfg.py）
DECIMATION = 4


class Stepper:
    """按 ManagerBasedRLEnv.step 的顺序推进：每个物理步写入、步进、更新；每 DECIMATION 个物理步渲染一次（有相机时）。"""

    def __init__(self, sim, scene, render: bool):
        self.sim, self.scene, self.render = sim, scene, render

    def env_step(self) -> None:
        for k in range(DECIMATION):
            self.scene.write_data_to_sim()
            self.sim.step(render=False)
            if self.render and k == DECIMATION - 1:
                self.sim.render()
            self.scene.update(PHYSICS_DT)


def save_images(cam, out_dir: str) -> None:
    from PIL import Image

    os.makedirs(out_dir, exist_ok=True)
    rgb = cam.data.output["rgb"][0].cpu().numpy()
    Image.fromarray(rgb).save(os.path.join(out_dir, "wrist_rgb.png"))
    depth = cam.data.output["depth"][0, ..., 0]
    finite = torch.isfinite(depth)
    d = depth.clone()
    d[~finite] = d[finite].max()
    d = (255 * (d - d.min()) / (d.max() - d.min() + 1e-9)).to(torch.uint8).cpu().numpy()  # 近黑远白
    Image.fromarray(d).save(os.path.join(out_dir, "wrist_depth.png"))
    print(f"[CAM] 已保存 {out_dir}/wrist_rgb.png、wrist_depth.png；env_0 深度范围 "
          f"{depth[finite].min():.3f}–{depth[finite].max():.3f} m")


def verify() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=PHYSICS_DT, device=args.device))
    cfg = make_sensor_scene_cfg(args.num_envs, camera=args.resolution, tcp_to_cube=True, contact=True)
    # 默认 False：相机的 pos_w / quat_w_* 只在创建时读一次，之后不随手臂运动更新（图像本身不受影响）
    cfg.wrist_cam.update_latest_camera_pose = True
    scene = InteractiveScene(cfg)
    sim.reset()
    robot, obj, cam, ee, t2c = (scene[k] for k in ("robot", "object", "wrist_cam", "ee_frame", "tcp_to_cube"))
    cl, cr = scene["contact_l"], scene["contact_r"]
    n, dev = args.num_envs, robot.device
    stepper = Stepper(sim, scene, render=True)
    d = robot.data
    robot.write_joint_state_to_sim(d.default_joint_pos, d.default_joint_vel)
    target = d.default_joint_pos.clone()
    g = robot.find_joints(f"{REACH_ARM}_gripper_joint")[0][0]
    link7 = robot.find_bodies(REACH_EE_BODY)[0][0]

    def run(seconds: float, gripper_q: float, pin: bool) -> None:
        target[:, g] = gripper_q
        robot.set_joint_position_target(target)
        for _ in range(round(seconds / (PHYSICS_DT * DECIMATION))):
            if pin:
                obj.write_root_pose_to_sim(torch.cat([ee.data.target_pos_w[:, 0], ee.data.target_quat_w[:, 0]], -1))
                obj.write_root_velocity_to_sim(torch.zeros(n, 6, device=dev))
            stepper.env_step()

    # ---------- 1. 相机：手臂保持默认姿态 1 s；再把方块钉在相机系的已知点 (x 右 5 cm, y 下 5 cm, z 前 30 cm) ----------
    run(1.0, GRIPPER_OPEN, pin=False)
    p_expect, q_expect = combine_frame_transforms(
        d.body_pos_w[:, link7], d.body_quat_w[:, link7],
        torch.tensor(WRIST_CAMERA_POS, device=dev).repeat(n, 1), torch.tensor(WRIST_CAMERA_ROT, device=dev).repeat(n, 1))
    cd = cam.data
    print(f"[CAM] 分辨率 {cd.image_shape}，数据类型 {list(cd.output.keys())}")
    print(f"[CAM] env_0 相机位置（相对环境原点）{[round(x, 4) for x in (cd.pos_w[0] - scene.env_origins[0]).tolist()]}；"
          f"link7 + URDF 偏移算出的位置与之最大偏差（全部环境）{(cd.pos_w - p_expect).norm(dim=-1).max() * 1000:.3f} mm")
    q_dot = (cd.quat_w_ros * q_expect).sum(-1).abs()  # |<q1, q2>| = 1 表示同一个姿态
    print(f"[CAM] 姿态（ROS 约定）与 URDF 偏移的一致度 |<q1,q2>| 最小 {q_dot.min():.6f}")
    R = matrix_from_quat(cd.quat_w_ros[0])
    print(f"[CAM] env_0 光轴（相机 +Z）在世界系 {[round(x, 3) for x in R[:, 2].tolist()]}；图像上方（相机 -Y）在世界系 "
          f"{[round(x, 3) for x in (-R[:, 1]).tolist()]}")
    K = cd.intrinsic_matrices[0]
    print(f"[CAM] 内参 fx {K[0, 0]:.2f} fy {K[1, 1]:.2f} cx {K[0, 2]:.2f} cy {K[1, 2]:.2f}（像素）")
    p_cam = torch.tensor([0.05, 0.05, 0.30], device=dev).repeat(n, 1)
    unit_q = torch.tensor([1.0, 0.0, 0.0, 0.0], device=dev).repeat(n, 1)
    for _ in range(3):  # 钉住并渲染几步，让图像与位姿都刷新
        pos, _ = combine_frame_transforms(cd.pos_w, cd.quat_w_ros, p_cam)
        obj.write_root_pose_to_sim(torch.cat([pos, unit_q], -1))
        obj.write_root_velocity_to_sim(torch.zeros(n, 6, device=dev))
        stepper.env_step()
    cd = cam.data  # 要重新访问 cam.data 才会刷新；上面拿到的 cd 还是钉方块之前的数据
    cube_c, _ = subtract_frame_transforms(cd.pos_w, cd.quat_w_ros, obj.data.root_pos_w)
    z = cube_c[0, 2]
    u, v = (K[0, 0] * cube_c[0, 0] / z + K[0, 2]).item(), (K[1, 1] * cube_c[0, 1] / z + K[1, 2]).item()
    rgb = cd.output["rgb"][0].float()
    red = (rgb[..., 0] - rgb[..., 1:].max(dim=-1).values) > 50  # 方块是红色 (0.8, 0.2, 0.2)，光照下偏粉；只认"红明显多于绿、蓝"
    print(f"[CAM] 方块中心在相机系 {[round(x, 3) for x in cube_c[0].tolist()]} m，按内参投影到像素 (u, v) = ({u:.1f}, {v:.1f})")
    if red.any():
        vv, uu = torch.nonzero(red, as_tuple=True)
        print(f"[CAM] 图中红色像素 {int(red.sum())} 个，重心 (u, v) = ({uu.float().mean():.1f}, {vv.float().mean():.1f})")
    else:
        print("[CAM] 图中没有红色像素：方块不在视野里")
    save_images(cam, args.out)

    # ---------- 2. FrameTransformer ----------
    tcp_root = ee.data.target_pos_source[0, 0]  # ee_frame 的源是机器人根
    print(f"[FT] ee_frame：env_0 TCP 相对机器人根 {[round(x, 3) for x in tcp_root.tolist()]} m")
    cube_tcp_hand, _ = subtract_frame_transforms(
        t2c.data.source_pos_w, t2c.data.source_quat_w, obj.data.root_pos_w)
    print(f"[FT] tcp_to_cube：方块在 TCP 系 {[round(x, 3) for x in t2c.data.target_pos_source[0, 0].tolist()]} m；"
          f"用世界位姿手算 {[round(x, 3) for x in cube_tcp_hand[0].tolist()]} m；"
          f"源位置与 ee_frame 的 TCP 相差 {(t2c.data.source_pos_w - ee.data.target_pos_w[:, 0]).norm(dim=-1).max() * 1000:.3f} mm")

    # ---------- 3. 接触传感器：脚本化抓取 ----------
    def forces():
        # force_matrix_w：(N, 1 个指尖, 1 个过滤对象, 3)；net_forces_w：(N, 1, 3)，与所有物体的合力
        fl = cl.data.force_matrix_w[:, 0, 0].norm(dim=-1)
        fr = cr.data.force_matrix_w[:, 0, 0].norm(dim=-1)
        nl = cl.data.net_forces_w[:, 0].norm(dim=-1)
        return fl, fr, nl

    print("[CONTACT] 阶段 | 时间 s | 夹爪角 rad | 左指尖-方块 N | 右指尖-方块 N | 左指尖合力 N（env_0；括号内为全部环境最大值）")
    phases = [("张开、钉住方块", 1.0, GRIPPER_OPEN, True), ("闭合、钉住方块", 2.0, GRIPPER_CLOSED, True),
              ("松开方块、只靠夹持", 1.5, GRIPPER_CLOSED, False), ("张开", 2.5, GRIPPER_OPEN, False)]
    t, summary = 0.0, []
    for name, dur, q, pin in phases:
        fmax = torch.zeros(n, device=dev)
        for k in range(round(dur / 0.1)):
            run(0.1, q, pin)
            t += 0.1
            fl, fr, nl = forces()
            fmax = torch.maximum(fmax, torch.maximum(fl, fr))
            if k % 5 == 4 or k == 0:
                print(f"[CONTACT] {name} | {t:4.1f} | {d.joint_pos[0, g]:.3f} | {fl[0]:7.2f} ({fl.max():.2f}) | "
                      f"{fr[0]:7.2f} ({fr.max():.2f}) | {nl[0]:7.2f}")
        fl, fr, _ = forces()
        summary.append(f"{name}：阶段末左/右 {fl.mean():.2f}/{fr.mean():.2f} N（环境平均），阶段内最大 {fmax.max():.2f} N")
    for s in summary:
        print(f"[CONTACT] {s}")
    fz = {side: robot.data.body_pos_w[:, robot.find_bodies(f"{REACH_ARM}_gripper_{side}_finger_link")[0][0], 2] for side in "lr"}
    print(f"[CONTACT] 张开后：方块高度 {obj.data.root_pos_w[:, 2].mean():.3f} m（桌面 0.975），"
          f"左/右指尖刚体原点高度 {fz['l'].mean():.3f}/{fz['r'].mean():.3f} m，方块重力 {obj.data.default_mass[0].sum() * 9.81:.2f} N")
    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


def bench() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=PHYSICS_DT, device=args.device))
    kind = args.bench
    t0 = time.perf_counter()
    cfg = make_sensor_scene_cfg(args.num_envs, camera={"cam64": 64, "cam128": 128}.get(kind), contact=kind == "contact")
    if kind != "frame":
        cfg.ee_frame = None  # lift 场景自带 ee_frame；只有 frame 这一行保留它
    scene = InteractiveScene(cfg)
    sim.reset()
    t_build = time.perf_counter() - t0
    robot = scene["robot"]
    robot.write_joint_state_to_sim(robot.data.default_joint_pos, robot.data.default_joint_vel)
    robot.set_joint_position_target(robot.data.default_joint_pos)
    stepper = Stepper(sim, scene, render=kind.startswith("cam"))

    def read() -> None:
        # 传感器数据是惰性计算的：访问 .data 才真正读取。训练时观测项每步都会访问，这里同样每步读一次
        if kind == "frame":
            scene["ee_frame"].data.target_pos_source
        elif kind == "contact":
            scene["contact_l"].data.force_matrix_w, scene["contact_r"].data.force_matrix_w
        elif kind.startswith("cam"):
            scene["wrist_cam"].data.output["rgb"]

    for _ in range(50):  # 热身
        stepper.env_step()
        read()
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(args.steps):
        stepper.env_step()
        read()
    torch.cuda.synchronize()
    el = time.perf_counter() - t0
    print(f"[BENCH] {kind} num_envs {args.num_envs}：构建 + reset {t_build:.1f} s；{args.steps} 个环境步 {el:.2f} s，"
          f"每环境步 {el / args.steps * 1000:.2f} ms，每秒环境步 {args.steps * args.num_envs / el:.0f}")
    sim.clear_all_callbacks()
    sim.clear_instance()


if __name__ == "__main__":
    bench() if args.bench else verify()
    sys.stdout.flush()
    simulation_app.close()
