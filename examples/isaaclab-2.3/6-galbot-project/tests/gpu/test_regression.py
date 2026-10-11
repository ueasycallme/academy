# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）；pytest 9.1.1
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""有 GPU：训练回归的确定性口径（7.4）。同机器、同版本、同种子，短训几次迭代后的权重应逐位相同
（6.4.4 / 6.5.1 的证据），与记录的指纹比。区间口径在 tests/regression/。标 slow，`pytest -m "not slow"` 可跳过。
"""

import hashlib
import json
import os
from pathlib import Path

import pytest
import torch

from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from isaaclab_tasks.utils import load_cfg_from_registry
from rsl_rl.runners import OnPolicyRunner

pytestmark = [pytest.mark.gpu, pytest.mark.slow]
GOLDEN = Path(__file__).parent / "golden_ppo.json"


def test_ppo_deterministic(make_env, tmp_path):
    """种子 42、256 个环境、3 次迭代。GALBOT_RECORD_GOLDEN=1 时记录指纹，否则与记录比。"""
    agent = load_cfg_from_registry("Galbot-Reach-v0", "rsl_rl_cfg_entry_point")
    agent.seed = 42
    env = RslRlVecEnvWrapper(make_env("Galbot-Reach-v0", num_envs=256, seed=agent.seed))
    runner = OnPolicyRunner(env, agent.to_dict(), log_dir=str(tmp_path), device="cuda:0")  # learn() 要写代码快照，log_dir 不能为 None
    runner.learn(num_learning_iterations=3)
    h = hashlib.sha256()
    for k, v in sorted(runner.alg.policy.state_dict().items()):
        h.update(k.encode())
        h.update(v.detach().cpu().contiguous().numpy().tobytes())
    key = f"torch {torch.__version__} / {torch.cuda.get_device_name(0)}"
    if os.environ.get("GALBOT_RECORD_GOLDEN") == "1":
        GOLDEN.write_text(json.dumps({"key": key, "sha256": h.hexdigest()}, indent=2) + "\n")
        pytest.skip("已记录指纹")
    golden = json.loads(GOLDEN.read_text())
    if golden["key"] != key:
        pytest.skip(f"指纹在 {golden['key']} 上记录，当前是 {key}：换了机器或版本，逐位比较不适用，改用区间口径")
    assert h.hexdigest() == golden["sha256"]

