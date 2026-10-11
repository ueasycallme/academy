# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab 2.3.2（rsl_rl 3.1.2）；torch 2.7.0、onnx 1.23.2、onnxruntime 1.20.1；不需要 Isaac Sim 与 GPU
# 验证日期：2026-10-11
"""从 rsl_rl 检查点导出部署件（6.7.1）：不启动 Isaac Sim，复用 Isaac Lab 自带的导出器。

play.py 导出时要先建环境（6.6.1）。这里只读检查点和同目录的 params/agent.yaml，按 agent 配置重建 rsl_rl 的 ActorCritic，
再交给 isaaclab_rl/rsl_rl/exporter.py 里与 play.py 相同的两个导出类。默认导出结果与 play.py 一致（批大小固定为 1）；
--dynamic-batch 让 ONNX 的第 0 维可变（6.7.2 坑三）。

    python scripts/export_policy.py logs/rsl_rl/galbot_reach/<运行>/model_999.pt --dynamic-batch
    # 写到 <运行>/deploy/：policy.pt、policy.onnx
"""

import argparse
import importlib.util
import os

import torch
import yaml
from rsl_rl.modules import ActorCritic
from rsl_rl.utils import resolve_obs_groups
from tensordict import TensorDict


def load_exporter():
    """按文件路径加载 isaaclab_rl/rsl_rl/exporter.py：它只依赖 torch。

    直接 `import isaaclab_rl.rsl_rl` 会连带导入 isaaclab，需要先启动 Kit（pxr 等模块），离线导出用不着。
    """
    pkg = importlib.util.find_spec("isaaclab_rl").submodule_search_locations[0]
    spec = importlib.util.spec_from_file_location("isaaclab_rsl_rl_exporter", os.path.join(pkg, "rsl_rl", "exporter.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_policy(checkpoint: str) -> ActorCritic:
    """按 params/agent.yaml 重建 ActorCritic，再载入检查点参数（与 OnPolicyRunner.load 载入的是同一份 state_dict）。"""
    run_dir = os.path.dirname(checkpoint)
    with open(os.path.join(run_dir, "params", "agent.yaml")) as f:
        agent = yaml.unsafe_load(f)  # dump_yaml 写出的文件里有 Python 对象标签
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)["model_state_dict"]
    n_obs = state["actor.0.weight"].shape[1]
    n_act = state["std"].shape[0]
    # 只用观测的形状来建网络；critic 缺省时用 policy 组（4.16 表 3）
    obs = TensorDict({"policy": torch.zeros(1, n_obs)}, batch_size=[1])
    obs_groups = resolve_obs_groups(obs, dict(agent.get("obs_groups") or {}), ["critic"])
    cfg = {k: v for k, v in agent["policy"].items() if k != "class_name"}
    policy = ActorCritic(obs, obs_groups, n_act, **cfg)
    policy.load_state_dict(state)
    policy.eval()
    return policy


def main() -> None:
    parser = argparse.ArgumentParser(description="从 rsl_rl 检查点导出 TorchScript 与 ONNX")
    parser.add_argument("checkpoint")
    parser.add_argument("--out_dir", default=None, help="默认 <运行目录>/deploy")
    parser.add_argument("--dynamic-batch", action="store_true", help="ONNX 的批维度可变（输入名 obs、输出名 actions 的第 0 维）")
    parser.add_argument("--opset", type=int, default=18, help="ONNX opset；18 与 Isaac Lab 2.3.2 的导出器相同")
    args = parser.parse_args()

    exporter = load_exporter()
    policy = load_policy(args.checkpoint)
    normalizer = policy.actor_obs_normalizer  # 没开观测归一化时是 Identity，导出后等于什么都不做（与 play.py 相同）
    out_dir = args.out_dir or os.path.join(os.path.dirname(args.checkpoint), "deploy")

    exporter.export_policy_as_jit(policy, normalizer=normalizer, path=out_dir, filename="policy.pt")

    onnx_exporter = exporter._OnnxPolicyExporter(policy, normalizer)
    onnx_exporter.to("cpu").eval()
    obs = torch.zeros(1, onnx_exporter.actor[0].in_features)
    # 与 exporter.py L206–L216 相同，只是 opset 与 dynamic_axes 可选
    torch.onnx.export(
        onnx_exporter,
        obs,
        os.path.join(out_dir, "policy.onnx"),
        export_params=True,
        opset_version=args.opset,
        input_names=["obs"],
        output_names=["actions"],
        dynamic_axes={"obs": {0: "batch"}, "actions": {0: "batch"}} if args.dynamic_batch else {},
    )
    print(f"[export] {args.checkpoint}")
    print(f"[export] 观测 {obs.shape[1]} 维 → 动作 {policy.actor[-1].out_features} 维；归一化：{type(normalizer).__name__}")
    print(f"[export] 写到 {out_dir}：policy.pt、policy.onnx（opset {args.opset}，批维度{'可变' if args.dynamic_batch else '固定为 1'}）")


if __name__ == "__main__":
    main()
