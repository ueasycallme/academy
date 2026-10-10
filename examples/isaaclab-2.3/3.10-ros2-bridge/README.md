# 3.10 ROS 2 Bridge：示例

对应页面：`docs/3-isaacsim/3.10-ros2-bridge.md`。

| 文件 | 在哪个 Python 里运行 | 作用 |
|---|---|---|
| `ros2_bridge_demo.py` | Isaac Sim 5.1（Python 3.11） | 加载 Galbot 固定底座版，用 `og.Controller` 搭 Action Graph：发布 `/clock`、`/joint_states`、`/tf`、`/camera/rgb`、`/camera/camera_info`，订阅 `/joint_command` |
| `sim_time_probe.py` | 系统 ROS 2 Humble（Python 3.10） | 对比 `use_sim_time` 开、关时节点的时间，统计 `/joint_states` |
| `grab_frame.py` | 系统 ROS 2 Humble | 从 `/camera/rgb` 收一帧，存成 PNG |

验证环境：Isaac Sim 5.1.0（pip）、`isaacsim.ros2.bridge` 4.12.4；Ubuntu 22.04，系统 ROS 2 Humble（`/opt/ros/humble`）；RTX 5070 12 GB，驱动 580.178.04。Galbot USD 用 6.1.2 的 `convert_galbot.py` 转换（`examples/isaaclab-2.3/6-galbot-project`）。

## 终端 1：Isaac Sim

两种方式选一种（页面表 1）。

自带库方式：Isaac Sim 里可以用 `rclpy`。开一个**没有** source 过系统 ROS 2 的终端：

```bash
export ROS_DISTRO=humble
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:<site-packages>/isaacsim/exts/isaacsim.ros2.bridge/humble/lib
python ros2_bridge_demo.py --usd <生成目录>/galbot_fixed_base/galbot.usd --seconds 240
```

系统库方式：只用 Action Graph。

```bash
source /opt/ros/humble/setup.bash
python ros2_bridge_demo.py --usd <生成目录>/galbot_fixed_base/galbot.usd --seconds 240
```

其他参数：`--gui` 打开窗口；`--no-camera` 不建相机；`--physics-only` 改用 `world.step(render=False)`，用于复现页面坑三，此时话题不发消息。

注意：重建的 5.1 环境第一次启动 Kit 时，要编译 RTX 管线，主机内存峰值约 11 GB，大约 40 s；之后启动约 13 s。

## 终端 2：系统 ROS 2

```bash
source /opt/ros/humble/setup.bash
ros2 topic list
ros2 topic echo --once /clock
ros2 topic hz /joint_states
python3 sim_time_probe.py --ros-args -p use_sim_time:=true      # Ctrl-C 结束
python3 grab_frame.py before.png
ros2 topic pub --once /joint_command sensor_msgs/msg/JointState \
    "{name: [left_arm_joint1, head_joint1], position: [1.0, 0.5]}"
python3 grab_frame.py after.png
```

预期：终端 1 每仿真秒打印一次 `left_arm_joint1`，发出指令后 2 s 仿真时间内（第二次打印时）到达 1.000 rad。本站实测的输出和频率见页面。
