# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
"""比对 reach 的 Manager 版与 Direct 版是否语义等价（6.4.4）。

一个进程里只能有一个 Isaac Lab 环境，所以分两步：
1. record：建一个环境，用同一种子 reset，喂一串固定的动作（numpy 种子固定），把初始观测、每步观测、奖励、超时存成 .npz；
2. diff：读两个 .npz，按观测分块（关节位置 / 关节速度 / 目标位姿 / 上一步动作）和奖励报最大绝对差，以及第一次超过阈值的步。

    python scripts/compare_direct_manager.py record --headless --task Galbot-Reach-v0 --out m.npz
    python scripts/compare_direct_manager.py record --headless --task Galbot-Reach-Direct-v0 --out d.npz
    python scripts/compare_direct_manager.py diff m.npz d.npz
    python scripts/compare_direct_manager.py lines          # 按管理器统计两版的代码行数，不需要 Isaac Sim

默认 400 步：覆盖两次命令重采样（第 121、242 步）和一次超时重置（第 360 步）。
--perturb 只对 Direct 版生效，用来复现页面上的坑：
- cmd_in_rewards：把命令的定时更新挪到算奖励时（重置之前）；
- reset_order：重置时在关节扰动之前先采一次命令（随机数的消耗顺序与 Manager 版不同）。
"""

import argparse
import sys

parser = argparse.ArgumentParser(description="比对 reach 的 Manager 版与 Direct 版")
sub = parser.add_subparsers(dest="mode", required=True)
rec = sub.add_parser("record")
rec.add_argument("--task", required=True)
rec.add_argument("--out", required=True)
rec.add_argument("--num_envs", type=int, default=64)
rec.add_argument("--steps", type=int, default=400)
rec.add_argument("--seed", type=int, default=0)
rec.add_argument("--perturb", choices=["none", "cmd_in_rewards", "reset_order"], default="none")
dif = sub.add_parser("diff")
dif.add_argument("a")
dif.add_argument("b")
dif.add_argument("--atol", type=float, default=1e-5, help="判为一致的最大绝对差")
sub.add_parser("lines")
BLOCKS = {"关节位置": slice(0, 7), "关节速度": slice(7, 14), "目标位姿": slice(14, 21), "上一步动作": slice(21, 28)}


def diff(args) -> None:
    import numpy as np

    a, b = np.load(args.a), np.load(args.b)
    print(f"[compare] {a['task']} vs {b['task']}：{a['obs'].shape[1]} 个环境 × {a['obs'].shape[0] - 1} 步")
    for name, s in BLOCKS.items():
        d = np.abs(a["obs"][..., s] - b["obs"][..., s]).max(axis=(1, 2))  # 每步（含初始观测）的最大差
        bad = np.nonzero(d > args.atol)[0]
        first = f"第一次超过 {args.atol:g}：第 {bad[0]} 步" if len(bad) else f"全程 ≤ {args.atol:g}"
        print(f"[compare] 观测·{name}：初始 {d[0]:.3g}，全程最大 {d.max():.3g}；{first}")
    d = np.abs(a["rew"] - b["rew"]).max(axis=1)
    bad = np.nonzero(d > args.atol)[0]
    first = f"第一次超过 {args.atol:g}：第 {bad[0] + 1} 步" if len(bad) else f"全程 ≤ {args.atol:g}"
    print(f"[compare] 奖励：全程最大 {d.max():.3g}（奖励量级 {np.abs(a['rew']).mean():.3g}）；{first}")
    print(f"[compare] 超时：{'一致' if (a['timeout'] == b['timeout']).all() else '不一致'}，"
          f"发生在第 {sorted(set(np.nonzero(a['timeout'])[0] + 1))} 步")


def record(args) -> None:
    from isaaclab.app import AppLauncher

    simulation_app = AppLauncher(args).app

    import gymnasium as gym
    import numpy as np
    import torch

    import galbot_academy.tasks  # noqa: F401
    from isaaclab_tasks.utils import parse_env_cfg

    cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    cfg.seed = args.seed
    env = gym.make(args.task, cfg=cfg).unwrapped
    if args.perturb != "none":
        assert hasattr(env, "_reset_robot"), "--perturb 只用于 Direct 版"
        perturb(env, args.perturb)
    rng = np.random.default_rng(args.seed)
    actions = rng.normal(0.0, 0.5, size=(args.steps, args.num_envs, 7)).astype(np.float32)  # 与策略输出量级相近
    obs_l, rew_l, to_l = [], [], []
    with torch.inference_mode():
        obs, _ = env.reset(seed=args.seed)
        obs_l.append(obs["policy"].cpu().numpy())
        for k in range(args.steps):
            obs, rew, _, time_out, _ = env.step(torch.from_numpy(actions[k]).to(env.device))
            obs_l.append(obs["policy"].cpu().numpy())
            rew_l.append(rew.cpu().numpy())
            to_l.append(time_out.cpu().numpy())
    np.savez(args.out, task=f"{args.task}{'' if args.perturb == 'none' else '+' + args.perturb}",
             obs=np.stack(obs_l), rew=np.stack(rew_l), timeout=np.stack(to_l))
    print(f"[compare] 已保存 {args.out}：obs {np.stack(obs_l).shape}，rew {np.stack(rew_l).shape}", flush=True)
    env.close()
    simulation_app.close()


def perturb(env, kind: str) -> None:
    """在 Direct 版实例上换掉一个方法，复现常见写法错误（只用于演示坑）。"""
    import types

    if kind == "cmd_in_rewards":
        get_rewards, get_obs = type(env)._get_rewards, type(env)._get_observations

        def _get_rewards(self):
            self._update_command(self.step_dt)  # 错误位置：在重置之前
            return get_rewards(self)

        def _get_observations(self):
            self._command_step = self.common_step_counter  # 让原来的更新不再发生
            return get_obs(self)

        env._get_rewards = types.MethodType(_get_rewards, env)
        env._get_observations = types.MethodType(_get_observations, env)
    elif kind == "reset_order":
        reset_robot = type(env)._reset_robot

        def _reset_robot(self, env_ids):
            self._resample_command(env_ids)  # 错误：在关节扰动之前先采一次命令，随机数的消耗顺序与 Manager 版不同
            reset_robot(self, env_ids)

        env._reset_robot = types.MethodType(_reset_robot, env)

# lines：管理器 → 两版各自的类 / 函数 / 方法名（4.14 表 3 的数法：不含空行、注释与 docstring）
TASKS = __import__("pathlib").Path(__file__).resolve().parent.parent / "source/galbot_academy/galbot_academy/tasks"
MANAGER_FILES = ["manager_based/reach/reach_env_cfg.py", "manager_based/reach/mdp/commands.py", "manager_based/reach/mdp/rewards.py"]
DIRECT_FILES = ["direct/reach/reach_env_cfg.py", "direct/reach/reach_env.py"]
LINE_MAP = [  # (管理器, Manager 版里的名字, Direct 版里的名字)
    ("ActionManager", ["ActionsCfg"], ["_pre_physics_step", "_apply_action"]),
    ("ObservationManager", ["ObservationsCfg"], ["_get_observations"]),
    ("CommandManager", ["CommandsCfg", "TcpPoseCommand", "TcpPoseCommandCfg"], ["_update_command", "_resample_command", "_command_w"]),
    ("RewardManager", ["RewardsCfg", "_command_w", "_tcp", "tcp_position_error", "tcp_position_error_tanh", "tcp_orientation_error"],
     ["_get_rewards", "REWARD_TERMS"]),
    ("TerminationManager", ["TerminationsCfg"], ["_get_dones"]),
    ("EventManager", ["EventCfg"], ["_reset_robot"]),
    ("CurriculumManager", ["CurriculumCfg"], []),
    ("重置流程", [], ["_reset_idx"]),
    ("总配置与初始化", ["GalbotReachEnvCfg"], ["GalbotReachDirectEnvCfg", "__init__"]),
]


def lines(_args) -> None:
    import ast

    def spans(src):
        tree, doc, out = ast.parse(src), set(), {}
        for node in ast.walk(tree):
            for stmt in getattr(node, "body", []) if isinstance(getattr(node, "body", None), list) else []:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                    doc.update(range(stmt.lineno, stmt.end_lineno + 1))
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                out.setdefault(node.name, (min([node.lineno] + [d.lineno for d in node.decorator_list]), node.end_lineno))
            elif isinstance(node, ast.Assign) and node.col_offset == 0 and isinstance(node.targets[0], ast.Name):
                out.setdefault(node.targets[0].id, (node.lineno, node.end_lineno))
        code = {i + 1 for i, line in enumerate(src.splitlines()) if line.strip() and not line.strip().startswith("#")} - doc
        return code, out

    def count(files, col):
        total, res = 0, {}
        for f in files:
            code, sp = spans((TASKS / f).read_text())
            total += len(code)
            for row in LINE_MAP:
                for n in row[col]:
                    if n in sp:
                        a, b = sp[n]
                        res[row[0]] = res.get(row[0], 0) + len([i for i in code if a <= i <= b])
        return res, total

    m, mt = count(MANAGER_FILES, 1)
    d, dt = count(DIRECT_FILES, 2)
    print(f"[compare] {'管理器':20s}{'Manager 版':>10s}{'Direct 版':>10s}")
    for row in LINE_MAP:
        print(f"[compare] {row[0]:20s}{m.get(row[0], 0):>10d}{d.get(row[0], 0):>10d}")
    print(f"[compare] {'文件合计（含 import）':20s}{mt:>10d}{dt:>10d}")


if __name__ == "__main__":
    if "record" in sys.argv[1:2]:
        from isaaclab.app import AppLauncher

        AppLauncher.add_app_launcher_args(rec)
    args = parser.parse_args()
    {"record": record, "diff": diff, "lines": lines}[args.mode](args)
