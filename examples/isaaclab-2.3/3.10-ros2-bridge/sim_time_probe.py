# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：系统 ROS 2 Humble（/opt/ros/humble，Python 3.10）；对端 Isaac Sim 5.1.0 + isaacsim.ros2.bridge 4.12.4
# 验证日期：2026-10-10
"""外部 ROS 2 节点：对比 use_sim_time 开/关时节点"现在几点"，并统计 /joint_states 的到达频率。

用法（系统 Python，先 source /opt/ros/humble/setup.bash）::

    python3 sim_time_probe.py                                   # use_sim_time 默认 False
    python3 sim_time_probe.py --ros-args -p use_sim_time:=true
"""

import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState


class Probe(Node):
    def __init__(self):
        super().__init__("sim_time_probe")
        self.count, self.first_stamp, self.last_stamp = 0, None, None
        self.wall0 = time.monotonic()
        self.create_subscription(JointState, "joint_states", self.on_joint_state, 10)
        self.create_timer(2.0, self.report, clock=rclpy.clock.Clock())  # 墙钟定时器：不受 use_sim_time 影响

    def on_joint_state(self, msg: JointState):
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.first_stamp = stamp if self.first_stamp is None else self.first_stamp
        self.last_stamp = stamp
        self.count += 1

    def report(self):
        now = self.get_clock().now().nanoseconds * 1e-9
        wall = time.monotonic() - self.wall0
        use_sim = self.get_parameter("use_sim_time").value
        span = (self.last_stamp - self.first_stamp) if self.count > 1 else 0.0
        self.get_logger().info(
            f"use_sim_time={use_sim} node_now={now:.3f} s | wall {wall:.1f} s: "
            f"{self.count} joint_states, stamp span {span:.2f} s"
        )


def main():
    rclpy.init()
    node = Probe()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
