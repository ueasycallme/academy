# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ isaacsim.ros2.bridge 4.12.4；外部节点用系统 ROS 2 Humble
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""用 og.Controller 搭一张 Action Graph：发布 /clock、/joint_states、/tf、相机图像与 camera_info，
并订阅 /joint_command 驱动 Galbot（固定底座版）。

用法（先在同一终端设置好 ROS 2 环境，见 README）::

    python ros2_bridge_demo.py --usd <galbot.usd> --seconds 60           # headless
    python ros2_bridge_demo.py --usd <galbot.usd> --seconds 60 --gui
    python ros2_bridge_demo.py --usd <galbot.usd> --no-camera            # 不建相机，省显存
"""

import argparse
import sys
import time

from isaacsim import SimulationApp

parser = argparse.ArgumentParser(description="ROS 2 Bridge 最小示例")
parser.add_argument("--usd", required=True, help="Galbot 固定底座版 USD（6.1.2 转换得到）")
parser.add_argument("--seconds", type=float, default=60.0, help="运行多少秒仿真时间")
parser.add_argument("--gui", action="store_true", help="打开 GUI 窗口（默认 headless）")
parser.add_argument("--no-camera", action="store_true", help="不建相机和相机话题")
parser.add_argument("--physics-only", action="store_true", help="用 world.step(render=False)（常见坑 3 的对照）")
args = parser.parse_args()
simulation_app = SimulationApp({"headless": not args.gui})

# 1. 启用扩展：Kit 启动之后、导入 isaacsim.ros2.* 之前
from isaacsim.core.utils.extensions import enable_extension

enable_extension("isaacsim.ros2.bridge")
simulation_app.update()

import omni.graph.core as og
from isaacsim.core.api import World
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.stage import add_reference_to_stage, get_current_stage
from pxr import Gf, UsdGeom, UsdPhysics

ROBOT = "/World/galbot"
CAMERA = "/World/camera"
GRAPH = "/World/ros2_graph"
PHYSICS_DT, RENDERING_DT = 1.0 / 120.0, 1.0 / 60.0


def find_articulation_root(stage, under: str) -> str:
    """转换器可能把 ArticulationRootAPI 放在根 prim 或某个连杆上，按 API 查找而不是写死路径。"""
    for prim in stage.Traverse():
        if str(prim.GetPath()).startswith(under) and prim.HasAPI(UsdPhysics.ArticulationRootAPI):
            return str(prim.GetPath())
    raise RuntimeError(f"{under} 下没有 ArticulationRootAPI")


def add_camera(stage) -> None:
    cam = UsdGeom.Camera.Define(stage, CAMERA)
    xf = UsdGeom.Xformable(cam)
    # 放在机器人前方 3 m、高 1.2 m，朝 -X 看（相机局部 -Z 是视线方向）
    m = Gf.Matrix4d().SetLookAt(Gf.Vec3d(3.0, 0.0, 1.2), Gf.Vec3d(0.0, 0.0, 0.8), Gf.Vec3d(0, 0, 1)).GetInverse()
    xf.AddTransformOp().Set(m)


def build_graph(robot_root: str, with_camera: bool) -> None:
    keys = og.Controller.Keys
    nodes = [
        ("tick", "omni.graph.action.OnPlaybackTick"),
        ("sim_time", "isaacsim.core.nodes.IsaacReadSimulationTime"),
        ("context", "isaacsim.ros2.bridge.ROS2Context"),
        ("pub_clock", "isaacsim.ros2.bridge.ROS2PublishClock"),
        ("pub_joint", "isaacsim.ros2.bridge.ROS2PublishJointState"),
        ("pub_tf", "isaacsim.ros2.bridge.ROS2PublishTransformTree"),
        ("sub_joint", "isaacsim.ros2.bridge.ROS2SubscribeJointState"),
        ("controller", "isaacsim.core.nodes.IsaacArticulationController"),
    ]
    connect = [
        ("tick.outputs:tick", "pub_clock.inputs:execIn"),
        ("tick.outputs:tick", "pub_joint.inputs:execIn"),
        ("tick.outputs:tick", "pub_tf.inputs:execIn"),
        ("tick.outputs:tick", "sub_joint.inputs:execIn"),
        ("tick.outputs:tick", "controller.inputs:execIn"),
        ("sim_time.outputs:simulationTime", "pub_clock.inputs:timeStamp"),
        ("sim_time.outputs:simulationTime", "pub_joint.inputs:timeStamp"),
        ("sim_time.outputs:simulationTime", "pub_tf.inputs:timeStamp"),
        ("context.outputs:context", "pub_clock.inputs:context"),
        ("context.outputs:context", "pub_joint.inputs:context"),
        ("context.outputs:context", "pub_tf.inputs:context"),
        ("context.outputs:context", "sub_joint.inputs:context"),
        ("sub_joint.outputs:jointNames", "controller.inputs:jointNames"),
        ("sub_joint.outputs:positionCommand", "controller.inputs:positionCommand"),
        ("sub_joint.outputs:velocityCommand", "controller.inputs:velocityCommand"),
        ("sub_joint.outputs:effortCommand", "controller.inputs:effortCommand"),
    ]
    values = [
        ("pub_clock.inputs:topicName", "clock"),
        ("pub_joint.inputs:topicName", "joint_states"),
        ("pub_joint.inputs:targetPrim", robot_root),
        ("pub_tf.inputs:topicName", "tf"),
        ("pub_tf.inputs:targetPrims", [robot_root]),
        ("sub_joint.inputs:topicName", "joint_command"),
        ("controller.inputs:robotPath", robot_root),
    ]
    if with_camera:
        nodes += [
            ("render_product", "isaacsim.core.nodes.IsaacCreateRenderProduct"),
            ("cam_rgb", "isaacsim.ros2.bridge.ROS2CameraHelper"),
            ("cam_info", "isaacsim.ros2.bridge.ROS2CameraInfoHelper"),
        ]
        connect += [
            ("tick.outputs:tick", "render_product.inputs:execIn"),
            ("render_product.outputs:execOut", "cam_rgb.inputs:execIn"),
            ("render_product.outputs:execOut", "cam_info.inputs:execIn"),
            ("render_product.outputs:renderProductPath", "cam_rgb.inputs:renderProductPath"),
            ("render_product.outputs:renderProductPath", "cam_info.inputs:renderProductPath"),
            ("context.outputs:context", "cam_rgb.inputs:context"),
            ("context.outputs:context", "cam_info.inputs:context"),
        ]
        values += [
            ("render_product.inputs:cameraPrim", [CAMERA]),
            ("render_product.inputs:width", 640),
            ("render_product.inputs:height", 480),
            ("cam_rgb.inputs:topicName", "camera/rgb"),
            ("cam_rgb.inputs:type", "rgb"),
            ("cam_rgb.inputs:frameId", "camera"),
            ("cam_info.inputs:topicName", "camera/camera_info"),
            ("cam_info.inputs:frameId", "camera"),
        ]
    og.Controller.edit(
        {"graph_path": GRAPH, "evaluator_name": "execution"},
        {keys.CREATE_NODES: nodes, keys.CONNECT: connect, keys.SET_VALUES: values},
    )


def main() -> None:
    world = World(stage_units_in_meters=1.0, physics_dt=PHYSICS_DT, rendering_dt=RENDERING_DT)
    world.scene.add_default_ground_plane()
    stage = get_current_stage()
    add_reference_to_stage(args.usd, ROBOT)
    robot_root = find_articulation_root(stage, ROBOT)
    if not args.no_camera:
        add_camera(stage)
    build_graph(robot_root, with_camera=not args.no_camera)
    robot = world.scene.add(SingleArticulation(prim_path=robot_root, name="galbot"))
    world.reset()
    print(f"articulation root: {robot_root}, dof = {robot.num_dof}", flush=True)

    names = robot.dof_names
    watch = names.index("left_arm_joint1") if "left_arm_joint1" in names else 0
    wall0, next_print, steps = time.perf_counter(), 0.0, 0
    while world.current_time < args.seconds:
        world.step(render=not args.physics_only)  # 带渲染：推进一个 rendering_dt = 2 个物理步（3.1"时间参数"）
        steps += 1
        if world.current_time >= next_print:  # 每仿真秒打印一次
            next_print += 1.0
            q = robot.get_joint_positions()
            print(
                f"sim {world.current_time:6.2f} s  wall {time.perf_counter() - wall0:6.2f} s  "
                f"{names[watch]} = {float(q[watch]):+.3f} rad",
                flush=True,
            )
    print(f"done: {steps} step() calls, sim {world.current_time:.2f} s, wall {time.perf_counter() - wall0:.2f} s", flush=True)
    world.clear_all_callbacks()
    world.clear_instance()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
