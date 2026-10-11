# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""生成随策略一起交付的接口说明 policy_spec.json（6.7.1）。

观测顺序与维度、动作对应的关节与换算、控制频率都从建好的环境里读出（建 1 个环境，不跑仿真步），
不从源码里手抄；归一化是否已折进模型看 params/agent.yaml。机器人侧照这份文件拼观测、换算动作（6.7.2 坑一的教训）。

    python scripts/make_policy_spec.py --headless --checkpoint logs/rsl_rl/galbot_reach/<运行>/model_999.pt
    # 写到 <运行>/deploy/policy_spec.json；deploy/ 里的模型先用 export_policy.py 导出
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="生成 policy_spec.json")
parser.add_argument("--task", default="Galbot-Reach-Play-v0")
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--deploy_dir", default=None, help="默认 <运行目录>/deploy")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import datetime
import hashlib
import json
import os

import gymnasium as gym
import onnx
import yaml

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

import galbot_academy.tasks  # noqa: F401

DESCRIPTIONS = {  # 观测项的含义；键是 ObservationsCfg 里的项名（reach_env_cfg.py）
    "joint_pos": "关节位置 − 默认位置（rad）",
    "joint_vel": "关节速度 − 默认速度（rad/s）",
    "pose_command": "目标 TCP 位姿：位置 xyz（m）+ 四元数 wxyz，机器人根坐标系",
    "actions": "上一步策略输出的动作（未缩放）",
}


def sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main() -> None:
    run_dir = os.path.dirname(os.path.abspath(args.checkpoint))
    deploy = args.deploy_dir or os.path.join(run_dir, "deploy")
    onnx_path = os.path.join(deploy, "policy.onnx")
    with open(os.path.join(run_dir, "params", "agent.yaml")) as f:
        agent = yaml.unsafe_load(f)

    env = gym.make(args.task, cfg=parse_env_cfg(args.task, device=args.device, num_envs=1)).unwrapped
    om, am = env.observation_manager, env.action_manager
    robot = env.scene["robot"]

    # 观测：按 ObservationManager 拼接的顺序（4.10），每项给出在 28 维向量里的起止下标
    obs, start = [], 0
    term_cfgs = dict(zip(om.active_terms["policy"], om._group_obs_term_cfgs["policy"]))
    for name, dims in zip(om.active_terms["policy"], om.group_obs_term_dim["policy"]):
        dim = int(dims[0])
        cfg = term_cfgs[name]
        asset = cfg.params.get("asset_cfg")
        item = {"name": name, "start": start, "dim": dim, "description": DESCRIPTIONS.get(name, "")}
        if asset is not None:
            item["joint_names"] = [robot.joint_names[i] for i in asset.joint_ids]
        item["scale"], item["clip"] = cfg.scale, cfg.clip  # None 表示不缩放、不裁剪
        obs.append(item)
        start += dim

    # 动作：本任务只有一个动作项（右臂关节位置）
    (term_name,) = am.active_terms
    term = am.get_term(term_name)
    joint_ids = term._joint_ids
    action = {
        "dim": am.total_action_dim,
        "term": term_name,
        "type": type(term).__name__,
        "joint_names": list(term._joint_names),
        "scale": float(term._scale) if isinstance(term._scale, float) else term._scale.tolist(),
        "offset": term._offset[0].tolist(),  # use_default_offset=True 时就是默认关节位置
        "formula": "joint_position_target = offset + scale * action",
        "clip": agent.get("clip_actions"),  # 训练时适配层的裁剪（4.16）；None 表示不裁剪
    }
    model = onnx.load(onnx_path)
    dims = lambda v: [d.dim_value or d.dim_param for d in v.type.tensor_type.shape.dim]  # noqa: E731
    spec = {
        "task": args.task,
        "created": datetime.date.today().isoformat(),
        "checkpoint": {"file": os.path.relpath(args.checkpoint, run_dir), "run": os.path.basename(run_dir), "sha256": sha256(args.checkpoint)},
        "model": {
            "onnx": {"file": "policy.onnx", "sha256": sha256(onnx_path), "opset": model.opset_import[0].version,
                     "input": {"name": model.graph.input[0].name, "shape": dims(model.graph.input[0]), "dtype": "float32"},
                     "output": {"name": model.graph.output[0].name, "shape": dims(model.graph.output[0]), "dtype": "float32"}},
            "torchscript": {"file": "policy.pt", "sha256": sha256(os.path.join(deploy, "policy.pt"))},
            # 开了观测归一化时，导出器把它和 actor 一起打包（6.6.1），机器人侧不能再归一化一次
            "obs_normalization_in_model": bool(agent["policy"].get("actor_obs_normalization", False)),
        },
        "observation": {"dim": start, "terms": obs},
        "action": action,
        "control": {"physics_dt": env.physics_dt, "decimation": env.cfg.decimation, "step_dt": env.step_dt,
                    "frequency_hz": round(1.0 / env.step_dt, 3)},
        "robot": {"default_joint_pos": dict(zip([robot.joint_names[i] for i in joint_ids],
                                                robot.data.default_joint_pos[0, joint_ids].tolist()))},
    }
    path = os.path.join(deploy, "policy_spec.json")
    with open(path, "w") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    terms = ", ".join(f"{o['name']} {o['dim']}" for o in obs)
    print(f"[spec] 写到 {path}：观测 {start} 维（{terms}），"
          f"动作 {action['dim']} 维，控制 {spec['control']['frequency_hz']} Hz", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
