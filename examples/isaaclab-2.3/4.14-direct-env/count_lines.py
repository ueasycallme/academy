# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab 2.3.2 源码（tag v2.3.2）
# 验证日期：2026-09-30
"""按"关注点"统计官方 Cartpole 两种写法的代码行数（不含空行、注释行与 docstring）。

不需要 Isaac Sim，普通 Python 3.10+ 即可::

    python count_lines.py --repo /path/to/IsaacLab     # 仓库需含 tag v2.3.2
"""

import argparse
import ast
import subprocess

TAG = "v2.3.2"
MANAGER = "source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/cartpole_env_cfg.py"
MANAGER_MDP = "source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/mdp/rewards.py"
DIRECT = "source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/cartpole_env.py"

# 关注点 → 该写法中对应的类名 / 函数名
MANAGER_MAP = {
    "场景": ["CartpoleSceneCfg"],
    "动作": ["ActionsCfg"],
    "观测": ["ObservationsCfg"],
    "重置": ["EventCfg"],
    "奖励": ["RewardsCfg", "joint_pos_target_l2"],
    "终止": ["TerminationsCfg"],
    "总配置": ["CartpoleEnvCfg"],
}
DIRECT_MAP = {
    "场景": ["_setup_scene"],
    "动作": ["_pre_physics_step", "_apply_action"],
    "观测": ["_get_observations"],
    "重置": ["_reset_idx"],
    "奖励": ["_get_rewards", "compute_rewards"],
    "终止": ["_get_dones"],
    "总配置": ["CartpoleEnvCfg", "__init__"],
}


def git_show(repo: str, path: str) -> str:
    return subprocess.run(["git", "-C", repo, "show", f"{TAG}:{path}"], check=True, capture_output=True, text=True).stdout


def code_lines(src: str) -> set[int]:
    """返回"代码行"的行号：非空、非纯注释、不属于 docstring。"""
    tree = ast.parse(src)
    doc = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list):
            # 类、函数、模块的 docstring，以及 configclass 字段后面的属性说明字符串
            for stmt in body:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                    doc.update(range(stmt.lineno, stmt.end_lineno + 1))
    lines = src.splitlines()
    return {i + 1 for i, l in enumerate(lines) if l.strip() and not l.strip().startswith("#")} - doc


def by_name(src: str) -> dict[str, tuple[int, int]]:
    """顶层类 / 函数，以及类里的方法 → (起始行, 结束行)，起始行含装饰器。"""
    out = {}
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            out.setdefault(node.name, (start, node.end_lineno))
    return out


def count(sources: list[str], mapping: dict[str, list[str]], total_label: str) -> dict[str, int]:
    result = {k: 0 for k in mapping}
    total = 0
    for src in sources:
        lines = code_lines(src)
        spans = by_name(src)
        total += len(lines)
        for key, names in mapping.items():
            for n in names:
                if n in spans:
                    a, b = spans[n]
                    result[key] += len([i for i in lines if a <= i <= b])
    result[total_label] = total
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="IsaacLab 仓库路径")
    args = parser.parse_args()
    m = count([git_show(args.repo, MANAGER), git_show(args.repo, MANAGER_MDP)], MANAGER_MAP, "文件合计")
    d = count([git_show(args.repo, DIRECT)], DIRECT_MAP, "文件合计")
    print(f"{'关注点':8s}{'manager-based':>14s}{'direct':>8s}")
    for key in list(MANAGER_MAP) + ["文件合计"]:
        print(f"{key:8s}{m[key]:>14d}{d[key]:>8d}")


if __name__ == "__main__":
    main()
