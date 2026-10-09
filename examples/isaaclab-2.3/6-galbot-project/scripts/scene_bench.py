# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-09
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""搭起 reach 场景并测量（6.2.1；6.2.3 扩展了单因素开关、计时拆分与主机内存记录）。

生成 N 个环境，机器人保持默认姿态，在每个环境的 TCP 处和一个示例目标处各放一个坐标轴标记
（VisualizationMarkers，不参与物理）。打印环境原点、USD 中的环境 Prim 数、保持误差，
再计时若干物理步，报告每秒物理步数与每秒环境步数。显存请用外部工具按进程测量（CONVENTIONS 第 5 节）。

    python scripts/scene_bench.py --headless --num_envs 16
    python scripts/scene_bench.py --headless --num_envs 1024
    python scripts/scene_bench.py --headless --num_envs 16 --table      # 加桌面，看默认姿态是否受影响

6.2.3 新增：打印克隆用时（Cloner.clone 的累计）、首次 reset 用时、一个物理步里"写入 / 步进 / 更新"三段的耗时，
以及进程运行期间主机 MemAvailable 的最低值；单因素开关见下。--task_env 改为计时 Galbot-Reach-v0 的 env.step，
用来对照命令项的 debug_vis 开 / 关。

    python scripts/scene_bench.py --headless --num_envs 4096
    python scripts/scene_bench.py --headless --num_envs 4096 --no_self_collision
    python scripts/scene_bench.py --headless --num_envs 4096 --env_spacing 1.0
    python scripts/scene_bench.py --headless --num_envs 4096 --no_filter
    python scripts/scene_bench.py --headless --num_envs 4096 --no_replicate
    python scripts/scene_bench.py --headless --num_envs 4096 --table
    python scripts/scene_bench.py --headless --num_envs 1024 --task_env --debug_vis off
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="reach 场景与吞吐")
parser.add_argument("--num_envs", type=int, default=16)
parser.add_argument("--env_spacing", type=float, default=2.5)
parser.add_argument("--table", action="store_true", help="用带桌面的场景")
parser.add_argument("--solver_iters", type=int, nargs=2, default=None, metavar=("POS", "VEL"),
                    help="覆盖求解器的位置 / 速度迭代次数（6.1.6b）；默认沿用资产或配置中的值")
parser.add_argument("--steps", type=int, default=1000, help="计时的物理步数")
parser.add_argument("--no_replicate", action="store_true", help="replicate_physics=False（6.2.3）")
parser.add_argument("--no_filter", action="store_true", help="filter_collisions=False（6.2.3）")
parser.add_argument("--no_self_collision", action="store_true", help="关闭机器人自碰撞（6.2.3）")
parser.add_argument("--task_env", action="store_true", help="改为计时 Galbot-Reach-v0 的 env.step（6.2.3）")
parser.add_argument("--debug_vis", choices=["on", "off"], default="on", help="--task_env 时命令项的 debug_vis（6.2.3）")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import threading
import time

import torch
from isaacsim.core.cloner import Cloner

import isaaclab.sim as sim_utils
from isaaclab.markers import VisualizationMarkers
from isaaclab.markers.config import FRAME_MARKER_CFG
from isaaclab.scene import InteractiveScene
from isaaclab.utils.math import combine_frame_transforms

from galbot_academy.assets.galbot import REACH_EE_BODY, REACH_EE_OFFSET_POS, REACH_EE_OFFSET_ROT
from galbot_academy.scenes.reach import GalbotReachSceneCfg, GalbotReachTableSceneCfg


# 6.2.3：给 Cloner.clone 套计时器（InteractiveScene 整体克隆环境、spawner 逐个克隆资产都走它），累计即"克隆用时"
_clone_time = [0.0]
_orig_clone = Cloner.clone


def _timed_clone(self, *a, **k):
    t = time.perf_counter()
    try:
        return _orig_clone(self, *a, **k)
    finally:
        _clone_time[0] += time.perf_counter() - t


Cloner.clone = _timed_clone

# 6.2.3：后台线程每 0.2 s 读一次 /proc/meminfo，记录主机可用内存的最低值（整机口径，含其他进程）
_mem_min = [float("inf")]
_mem_stop = threading.Event()


def _mem_watch() -> None:
    while not _mem_stop.is_set():
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable"):
                    _mem_min[0] = min(_mem_min[0], int(line.split()[1]) / 1024 / 1024)
        _mem_stop.wait(0.2)


threading.Thread(target=_mem_watch, daemon=True).start()


def _rss_gib() -> float:
    """本进程当前的主机 RSS（GiB），读 /proc/self/status。"""
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS"):
                return int(line.split()[1]) / 1024 / 1024
    return float("nan")


_rss_start = _rss_gib()  # Isaac Sim 与扩展加载完、建场景之前


def task_env_bench() -> None:
    """6.2.3：Galbot-Reach-v0 的 env.step 计时，零动作；对照命令项 debug_vis 开 / 关。"""
    import gymnasium as gym

    import galbot_academy.tasks  # noqa: F401  注册任务
    from isaaclab_tasks.utils import parse_env_cfg

    cfg = parse_env_cfg("Galbot-Reach-v0", device=args.device, num_envs=args.num_envs)
    cfg.commands.ee_pose.debug_vis = args.debug_vis == "on"
    env = gym.make("Galbot-Reach-v0", cfg=cfg).unwrapped
    env.reset()
    act = torch.zeros(env.num_envs, env.action_manager.total_action_dim, device=env.device)
    for _ in range(50):
        env.step(act)
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    n_steps = 300
    for _ in range(n_steps):
        env.step(act)
    torch.cuda.synchronize()
    el = time.perf_counter() - t0
    print(f"[6.2.3] task_env debug_vis {args.debug_vis} num_envs {args.num_envs}：每个环境步 {el / n_steps * 1000:.2f} ms，"
          f"每秒环境步 {n_steps * args.num_envs / el:.0f}；MemAvailable 最低 {_mem_min[0]:.2f} GiB")
    env.close()


def main() -> None:
    dt = 1 / 120
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=dt, device=args.device))
    scene_cls = GalbotReachTableSceneCfg if args.table else GalbotReachSceneCfg
    t0 = time.perf_counter()
    scene_cfg = scene_cls(num_envs=args.num_envs, env_spacing=args.env_spacing)
    if args.solver_iters is not None:
        props = scene_cfg.robot.spawn.articulation_props
        props.solver_position_iteration_count, props.solver_velocity_iteration_count = args.solver_iters
    scene_cfg.replicate_physics = not args.no_replicate
    scene_cfg.filter_collisions = not args.no_filter
    if args.no_self_collision:
        scene_cfg.robot.spawn.articulation_props.enabled_self_collisions = False
    scene = InteractiveScene(scene_cfg)
    t_scene = time.perf_counter() - t0
    rss_scene = _rss_gib()
    t1 = time.perf_counter()
    sim.reset()
    t_reset = time.perf_counter() - t1
    rss_reset = _rss_gib()
    t_build = time.perf_counter() - t0
    robot = scene["robot"]
    d = robot.data

    origins = scene.env_origins
    stage = sim_utils.get_current_stage()
    env_prims = [p for p in stage.GetPrimAtPath("/World/envs").GetChildren()]
    iters = "沿用配置" if args.solver_iters is None else f"{args.solver_iters[0]} / {args.solver_iters[1]}"
    print(f"{scene_cls.__name__}：{args.num_envs} 个环境，env_spacing {args.env_spacing} m，求解器迭代 {iters}，构建 + reset {t_build:.1f} s")
    print(f"  环境原点（前 3 个与最后 1 个）：{[[round(x, 2) for x in o] for o in origins[:3].tolist()]} … "
          f"{[round(x, 2) for x in origins[-1].tolist()]}")
    print(f"  /World/envs 下的 Prim 数：{len(env_prims)}；scene 中的实体：{list(scene.keys())}")

    # 标记：TCP 处一个，前方 0.1 m 处一个示例目标；它们放在 /Visuals 下，不在 /World/envs 里，也没有物理属性
    frame_cfg = FRAME_MARKER_CFG.replace(prim_path="/Visuals/ee_and_goal")
    frame_cfg.markers["frame"].scale = (0.08, 0.08, 0.08)
    markers = VisualizationMarkers(frame_cfg)
    ee = robot.body_names.index(REACH_EE_BODY)
    n = args.num_envs
    off_p = torch.tensor(REACH_EE_OFFSET_POS, device=robot.device).repeat(n, 1)
    off_q = torch.tensor(REACH_EE_OFFSET_ROT, device=robot.device).repeat(n, 1)

    robot.write_joint_state_to_sim(d.default_joint_pos, d.default_joint_vel)
    robot.set_joint_position_target(d.default_joint_pos)

    def step() -> None:
        scene.write_data_to_sim()
        sim.step(render=False)
        scene.update(dt)

    for _ in range(round(2.0 / dt)):  # 保持 2 s
        step()
    tcp_p, tcp_q = combine_frame_transforms(d.body_pos_w[:, ee], d.body_quat_w[:, ee], off_p, off_q)
    goal_p = tcp_p + torch.tensor([0.1, 0.0, 0.0], device=robot.device)
    markers.visualize(torch.cat([tcp_p, goal_p]), torch.cat([tcp_q, tcp_q]))
    err = (d.joint_pos - d.default_joint_pos).abs().max().item()
    print(f"  保持默认姿态 2 s：最大关节误差 {err:.4f} rad，数值有限 {bool(torch.isfinite(d.joint_pos).all())}")
    print(f"  env_0 的 TCP（世界系）{[round(x, 3) for x in tcp_p[0].tolist()]}；标记 Prim 在 /Visuals 下，"
          f"共 {2 * n} 个实例")

    # 计时：只推进物理（不渲染），先热身 100 步
    for _ in range(100):
        step()
    torch.cuda.synchronize() if robot.device.startswith("cuda") else None
    t0 = time.perf_counter()
    for _ in range(args.steps):
        step()
    torch.cuda.synchronize() if robot.device.startswith("cuda") else None
    el = time.perf_counter() - t0
    print(f"  计时 {args.steps} 个物理步：{el:.2f} s，每秒物理步 {args.steps / el:.0f}，每秒环境步 {args.steps * n / el:.0f}")

    # 6.2.3：拆分计时。每段前后同步 GPU，所以三段之和会比上面的总耗时略大
    parts = [0.0, 0.0, 0.0]
    n_split = min(args.steps, 300)
    for _ in range(n_split):
        for i, fn in enumerate((scene.write_data_to_sim, lambda: sim.step(render=False), lambda: scene.update(dt))):
            torch.cuda.synchronize()
            ts = time.perf_counter()
            fn()
            torch.cuda.synchronize()
            parts[i] += time.perf_counter() - ts
    w, st, up = (x / n_split * 1000 for x in parts)
    print(f"[6.2.3] num_envs {n} replicate {scene_cfg.replicate_physics} filter {scene_cfg.filter_collisions} "
          f"self_collision {scene_cfg.robot.spawn.articulation_props.enabled_self_collisions} table {args.table} "
          f"spacing {args.env_spacing}：建场景 {t_scene:.2f} s（其中克隆 {_clone_time[0]:.2f} s），reset {t_reset:.2f} s；"
          f"每个物理步 {el / args.steps * 1000:.2f} ms（拆分：写入 {w:.2f} / 步进 {st:.2f} / 更新 {up:.2f} ms）；"
          f"MemAvailable 最低 {_mem_min[0]:.2f} GiB")
    print(f"[6.2.3] RSS（GiB）：启动后 {_rss_start:.2f}，建场景后 {rss_scene:.2f}，reset 后 {rss_reset:.2f}，计时结束 {_rss_gib():.2f}")

    sim.clear_all_callbacks()  # 退出三步：释放 SimulationContext → flush → close
    sim.clear_instance()


if __name__ == "__main__":
    task_env_bench() if args.task_env else main()
    sys.stdout.flush()
    simulation_app.close()
