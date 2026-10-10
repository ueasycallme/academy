# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：系统 ROS 2 Humble（/opt/ros/humble，Python 3.10），numpy 1.21.5，Pillow 9.0.1
# 验证日期：2026-10-10
"""从 /camera/rgb 收一帧 rgb8 图像存成 PNG（不依赖 cv_bridge）。

用法::

    python3 grab_frame.py out.png [topic]
"""

import sys

import numpy as np
import rclpy
from PIL import Image as PILImage
from sensor_msgs.msg import Image


def main():
    out = sys.argv[1]
    topic = sys.argv[2] if len(sys.argv) > 2 else "camera/rgb"
    rclpy.init()
    node = rclpy.create_node("grab_frame")
    got = []
    node.create_subscription(Image, topic, lambda msg: got.append(msg), 1)
    while not got:
        rclpy.spin_once(node, timeout_sec=1.0)
    msg = got[0]
    assert msg.encoding == "rgb8", msg.encoding
    img = np.frombuffer(bytes(msg.data), dtype=np.uint8).reshape(msg.height, msg.step)[:, : msg.width * 3]
    PILImage.fromarray(img.reshape(msg.height, msg.width, 3)).save(out)
    stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
    print(f"saved {out}: {msg.width}x{msg.height}, stamp {stamp:.3f} s")
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
