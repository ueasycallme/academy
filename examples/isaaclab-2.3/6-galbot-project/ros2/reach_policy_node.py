# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：系统 ROS 2 Humble（/opt/ros/humble，Python 3.10）+ onnxruntime 1.20.1 + numpy 1.26.4
# 验证日期：2026-10-10
"""reach 策略的 ROS 2 节点（6.7.2）：订阅观测，用 ONNX Runtime 推理，发布动作。

接口约定（与 scripts/run_ros2_sim.py 一致）：
- 观测 `/galbot/reach/obs`，`std_msgs/Float32MultiArray`：data[0] 是控制步序号，data[1:29] 是 28 维观测，
  顺序与训练时 ObservationManager 拼接的顺序相同（右臂关节位置相对量 7、右臂关节速度相对量 7、目标位姿 7、上一步动作 7）。
- 动作 `/galbot/reach/action`，`std_msgs/Float32MultiArray`：data[0] 原样回传步序号，data[1:8] 是右臂 7 个关节的动作
  （未缩放；仿真端的 JointPositionAction 按训练时的 scale 与默认姿态换算成关节目标）。

用法（系统 Python 或带 onnxruntime 的 venv，先 source /opt/ros/humble/setup.bash）::

    python reach_policy_node.py --ros-args -p onnx:=<运行目录>/exported/policy.onnx
"""

import numpy as np
import onnxruntime as ort
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Float32MultiArray

OBS_DIM, ACT_DIM = 28, 7
# 可靠传输、只保留最新几条：同步方式下每步只有一条观测在路上
QOS = QoSProfile(reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST, depth=10)


class ReachPolicyNode(Node):
    def __init__(self):
        super().__init__("reach_policy")
        path = self.declare_parameter("onnx", "").value
        self.session = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
        inp = self.session.get_inputs()[0]
        # play.py 导出的模型批大小固定为 1（6.6.1）；观测维度不对时直接报错，不要静默截断
        assert list(inp.shape) == [1, OBS_DIM], f"ONNX 输入形状 {inp.shape}，期望 [1, {OBS_DIM}]"
        self.input_name = inp.name
        self.pub = self.create_publisher(Float32MultiArray, "/galbot/reach/action", QOS)
        self.create_subscription(Float32MultiArray, "/galbot/reach/obs", self.on_obs, QOS)
        self.count = 0
        self.get_logger().info(f"loaded {path}: input {inp.name} {inp.shape}, onnxruntime {ort.__version__}")

    def on_obs(self, msg: Float32MultiArray):
        data = np.asarray(msg.data, dtype=np.float32)
        if data.size != 1 + OBS_DIM:
            self.get_logger().error(f"观测长度 {data.size}，期望 {1 + OBS_DIM}，丢弃")
            return
        act = self.session.run(None, {self.input_name: data[1:].reshape(1, OBS_DIM)})[0].reshape(ACT_DIM)
        out = Float32MultiArray()
        out.data = [float(data[0])] + act.astype(np.float32).tolist()
        self.pub.publish(out)
        self.count += 1
        if self.count % 3600 == 0:
            self.get_logger().info(f"{self.count} actions published")


def main():
    rclpy.init()
    node = ReachPolicyNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
