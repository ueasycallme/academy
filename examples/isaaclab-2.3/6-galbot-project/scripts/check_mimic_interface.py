# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；Galbot 描述仓库 commit 2d496b0
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""检查 pick-place 的 Mimic 接口（6.4.6）：在 Galbot-PickPlace-IK-Rel-Mimic-v0 里开环重放录下的示范。

做的事与 annotate_demos.py 的自动标注相同（4.19"四步流水线"）：从每条示范的初始状态出发，原样重放动作。
每一步额外检查：
- action_to_target_eef_pose 与 target_eef_pose_to_action 互为逆：动作 → 目标位姿 → 动作，差多少；
- get_object_poses 给出方块与放置点；get_subtask_term_signals 的 grasp 第一次为 True 在第几步；
最后看重放结束时 success 是否成立（开环重放能否复现示范）。

annotate_demos.py 只认 Isaac Lab 自带的任务（2.3.2 没有 --external_callback，4.19 版本说明），
所以本项目的 Mimic 标注与生成放在 6.4.7 用自己的入口脚本做；这里只验证接口。

    python scripts/check_mimic_interface.py --headless --dataset_file ./datasets/galbot_pick_place.hdf5
"""

import argparse
import sys

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="检查 pick-place 的 Mimic 接口")
parser.add_argument("--dataset_file", default="./datasets/galbot_pick_place.hdf5")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

import gymnasium as gym
import torch

from isaaclab.utils.datasets import HDF5DatasetFileHandler

import galbot_academy.tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

TASK = "Galbot-PickPlace-IK-Rel-Mimic-v0"


def main() -> None:
    handler = HDF5DatasetFileHandler()
    handler.open(args.dataset_file)
    names = list(handler.get_episode_names())
    env_cfg = parse_env_cfg(TASK, device=args.device, num_envs=1)
    success_term = env_cfg.terminations.success
    env_cfg.terminations.success = None
    env_cfg.terminations.time_out = None
    env = gym.make(TASK, cfg=env_cfg).unwrapped
    eef = next(iter(env.cfg.subtask_configs))
    print(f"[mimic] {TASK}：{len(names)} 条示范；末端 {eef!r}；子任务 "
          f"{[(c.object_ref, c.subtask_term_signal) for c in env.cfg.subtask_configs[eef]]}", flush=True)
    n_ok = 0
    with torch.inference_mode():
        for name in names:
            ep = handler.load_episode(name, env.device)
            actions = ep.data["actions"]
            env.sim.reset()
            env.reset_to(ep.data["initial_state"], None, is_relative=True)
            first_grasp, max_rt = None, 0.0
            for k, a in enumerate(actions):
                a = a[None]
                # 往返：动作 → 目标位姿 → 动作（不加噪声），比较前 6 维
                tgt = env.action_to_target_eef_pose(a)
                # 前者给的是批量 (N, 4, 4)；后者按单个环境取 (4, 4)，与 Mimic 生成时的调用方式一致
                back = env.target_eef_pose_to_action({eef: tgt[eef][0]}, {eef: a[0, 6:]}, None, env_id=0)
                max_rt = max(max_rt, (back[:6] - a[0, :6]).abs().max().item())
                env.step(a)
                if first_grasp is None and bool(env.get_subtask_term_signals()["grasp"][0]):
                    first_grasp = k
            objs = env.get_object_poses()
            ok = bool(success_term.func(env, **success_term.params)[0])
            n_ok += ok
            print(f"[mimic] {name}：{len(actions)} 步；grasp 首次为真在第 {first_grasp} 步；重放结束 success={ok}；"
                  f"动作往返最大差 {max_rt:.2e}；物体 {sorted(objs)}", flush=True)
    print(f"[mimic] 开环重放后仍然成功：{n_ok} / {len(names)}", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    simulation_app.close()
