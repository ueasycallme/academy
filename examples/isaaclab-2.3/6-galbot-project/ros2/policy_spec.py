# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.10（系统 ROS 2 Humble 一侧）+ onnxruntime 1.20.1；不依赖 rclpy
# 验证日期：2026-10-11
"""读取并核对 policy_spec.json（6.7.1）。策略节点启动时调用；不依赖 rclpy，可以单独测试：

    python policy_spec.py <deploy>/policy.onnx <deploy>/policy_spec.json
"""

import hashlib
import json
import sys

import onnxruntime as ort

OBS_DIM, ACT_DIM = 28, 7
# 策略节点按这个顺序拼观测（与仿真端 run_ros2_sim.py 一致）；policy_spec.json 里的顺序必须相同
OBS_TERMS = ["joint_pos", "joint_vel", "pose_command", "actions"]


def check_input_shape(shape: list) -> None:
    """play.py 导出的模型批大小固定为 1（6.6.1）；export_policy.py --dynamic-batch 导出的第 0 维是名字 "batch"。"""
    if shape[0] not in (1, "batch") or list(shape[1:]) != [OBS_DIM]:
        raise ValueError(f"ONNX 输入形状 {shape}，期望 [1 或 batch, {OBS_DIM}]")


def check_spec(spec_path: str, onnx_path: str) -> dict:
    """核对说明文件属于这个模型，且观测顺序、维度与节点的拼法一致；返回解析后的 spec。"""
    with open(spec_path) as f:
        spec = json.load(f)
    with open(onnx_path, "rb") as f:
        if spec["model"]["onnx"]["sha256"] != hashlib.sha256(f.read()).hexdigest():
            raise ValueError("policy_spec.json 与这个 ONNX 文件不配套（sha256 不同）")
    names = [t["name"] for t in spec["observation"]["terms"]]
    if names != OBS_TERMS:
        raise ValueError(f"观测顺序 {names}，节点按 {OBS_TERMS} 拼接")
    if spec["observation"]["dim"] != OBS_DIM or spec["action"]["dim"] != ACT_DIM:
        raise ValueError(f"维度 {spec['observation']['dim']} → {spec['action']['dim']}，节点按 {OBS_DIM} → {ACT_DIM}")
    return spec


if __name__ == "__main__":
    onnx_path, spec_path = sys.argv[1], sys.argv[2]
    try:
        check_input_shape(ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"]).get_inputs()[0].shape)
        spec = check_spec(spec_path, onnx_path)
        terms = [(t["name"], t["start"], t["dim"]) for t in spec["observation"]["terms"]]
        print(f"spec ok: {terms}, action {spec['action']['dim']} @ {spec['control']['frequency_hz']} Hz")
    except ValueError as e:
        print(f"拒绝：{e}")
        sys.exit(1)
