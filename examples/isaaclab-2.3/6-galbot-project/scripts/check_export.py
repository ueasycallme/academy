# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab 2.3.2（rsl_rl 3.1.2）导出的文件；只需 PyTorch 与 onnx，不需要 Isaac Sim 与 GPU
# 验证日期：2026-10-09
"""核对 play.py 导出的策略（6.6.1）：exported/policy.pt（TorchScript）与检查点里的 actor 输出是否一致，
exported/policy.onnx 结构是否合法、输入输出维度是否对。

    python scripts/check_export.py logs/rsl_rl/galbot_reach/<运行>/model_999.pt

本项目训练时没有开观测归一化，所以导出的网络就是 actor 本身（ELU 激活的 MLP）。
"""

import argparse
import os

import onnx
import torch

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("checkpoint")
args = parser.parse_args()

state = torch.load(args.checkpoint, map_location="cpu", weights_only=False)["model_state_dict"]
# 从检查点按层重建 actor：actor.0 / actor.2 / actor.4 是线性层，中间是 ELU（agent 配置 activation="elu"）
layers = sorted({int(k.split(".")[1]) for k in state if k.startswith("actor.")})
actor = torch.nn.Sequential()
for i, idx in enumerate(layers):
    w, b = state[f"actor.{idx}.weight"], state[f"actor.{idx}.bias"]
    lin = torch.nn.Linear(w.shape[1], w.shape[0])
    lin.load_state_dict({"weight": w, "bias": b})
    actor.append(lin)
    if i < len(layers) - 1:
        actor.append(torch.nn.ELU())
n_obs, n_act = state[f"actor.{layers[0]}.weight"].shape[1], state[f"actor.{layers[-1]}.weight"].shape[0]
print(f"检查点：actor {len(layers)} 个线性层，观测 {n_obs} 维 → 动作 {n_act} 维；另有 critic 与 std，导出时不带")

export_dir = os.path.join(os.path.dirname(args.checkpoint), "exported")
jit_path, onnx_path = os.path.join(export_dir, "policy.pt"), os.path.join(export_dir, "policy.onnx")
for p in (jit_path, onnx_path):
    print(f"{os.path.relpath(p, os.path.dirname(args.checkpoint))}：{os.path.getsize(p) / 1024:.1f} KB")

torch.manual_seed(0)
obs = torch.randn(256, n_obs)
jit = torch.jit.load(jit_path, map_location="cpu")
with torch.no_grad():
    diff = (jit(obs) - actor(obs)).abs().max().item()
print(f"TorchScript 与检查点 actor 的输出最大差：{diff:.2e}（256 个随机观测）")

model = onnx.load(onnx_path)
onnx.checker.check_model(model)
dims = lambda v: [d.dim_value or d.dim_param for d in v.type.tensor_type.shape.dim]
print(f"ONNX 结构检查通过；输入 {[(i.name, dims(i)) for i in model.graph.input]}，输出 {[(o.name, dims(o)) for o in model.graph.output]}")
