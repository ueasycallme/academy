# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.10（系统 python3，pytest 6.2.5）/ 3.10（CI，pytest 8.3.3）/ 3.11（Isaac 环境，pytest 9.1.1）；不依赖 Isaac Sim
# 验证日期：2026-10-11
"""无 GPU：部署接口核对（6.7.1）与 sim2real 越限统计（6.7.3）。"""

import hashlib
import json
import subprocess
import sys

import numpy as np
import pytest

import policy_spec

TERMS = [("joint_pos", 7), ("joint_vel", 7), ("pose_command", 7), ("actions", 7)]


def make_spec(path, onnx_bytes: bytes, terms=TERMS, obs_dim=28) -> None:
    start, items = 0, []
    for name, dim in terms:
        items.append({"name": name, "start": start, "dim": dim})
        start += dim
    spec = {
        "model": {"onnx": {"sha256": hashlib.sha256(onnx_bytes).hexdigest()}, "obs_normalization_in_model": False},
        "observation": {"dim": obs_dim, "terms": items},
        "action": {"dim": 7, "formula": "target = offset + scale * action", "scale": 0.5, "clip": None,
                   "joint_names": [f"right_arm_joint{i}" for i in range(1, 8)], "offset": [0.0] * 7},
        "control": {"frequency_hz": 30.0, "physics_dt": 1 / 120, "decimation": 4},
    }
    path.write_text(json.dumps(spec))


@pytest.fixture
def onnx(tmp_path):
    p = tmp_path / "policy.onnx"
    p.write_bytes(b"not really onnx")  # check_spec 只算 sha256，不解析模型
    return p


def test_policy_spec_ok(tmp_path, onnx):
    make_spec(tmp_path / "spec.json", onnx.read_bytes())
    assert policy_spec.check_spec(str(tmp_path / "spec.json"), str(onnx))["action"]["dim"] == 7


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"terms": [TERMS[1], TERMS[0], *TERMS[2:]]}, "观测顺序"),  # 对调两块观测（6.7.2 坑一）
        ({"obs_dim": 27}, "维度"),
    ],
)
def test_policy_spec_rejects(tmp_path, onnx, kwargs, message):
    make_spec(tmp_path / "spec.json", onnx.read_bytes(), **kwargs)
    with pytest.raises(ValueError, match=message):
        policy_spec.check_spec(str(tmp_path / "spec.json"), str(onnx))


def test_policy_spec_rejects_other_model(tmp_path, onnx):
    make_spec(tmp_path / "spec.json", b"another model")
    with pytest.raises(ValueError, match="sha256"):
        policy_spec.check_spec(str(tmp_path / "spec.json"), str(onnx))


def test_input_shape():
    policy_spec.check_input_shape([1, 28])
    policy_spec.check_input_shape(["batch", 28])
    with pytest.raises(ValueError):
        policy_spec.check_input_shape([1, 27])


def test_sim2real_report_counts_violations(tmp_path, onnx):
    """一个关节、一步越过 URDF 上限：报告应当数出 1 个环境步。断言输出内容，不只看返回码（7.4 坑一）。"""
    make_spec(tmp_path / "spec.json", onnx.read_bytes())
    joints = "".join(
        f'<joint name="right_arm_joint{i}" type="revolute"><limit lower="-1" upper="1" velocity="1.5" effort="60"/></joint>'
        for i in range(1, 8)
    )
    (tmp_path / "robot.urdf").write_text(f'<robot name="r">{joints}</robot>')
    actions = np.zeros((5, 2, 7), dtype=np.float32)
    actions[3, 1, 6] = 4.0  # 目标 = 0 + 0.5 × 4 = 2 rad > 上限 1
    np.savez(tmp_path / "traj.npz", actions=actions)
    out = subprocess.run(
        [sys.executable, str(policy_spec.__file__).replace("ros2/policy_spec.py", "scripts/sim2real_report.py"),
         "--spec", str(tmp_path / "spec.json"), "--urdf", str(tmp_path / "robot.urdf"), "--traj", str(tmp_path / "traj.npz")],
        capture_output=True, text=True, check=True,
    ).stdout
    assert "按步 1 / 10（10.0%）" in out
    assert "right_arm_joint7：越限 1 个环境步、1 个环境，最大超出 1.000 rad" in out
