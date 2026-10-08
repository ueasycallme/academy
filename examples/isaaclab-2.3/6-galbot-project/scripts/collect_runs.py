# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab 2.3.2（rsl_rl 3.1.2）的训练日志；只需 PyYAML 与 tensorboard，不需要 Isaac Sim 与 GPU
# 验证日期：2026-10-08
"""把若干次训练汇成一张表（6.5.3）：每个运行相对基线改了哪些配置项、种子、迭代数、训练日志里的末段指标。

    python scripts/collect_runs.py logs/rsl_rl/galbot_reach --base <基线运行目录名> [--filter hp_]

改动来自 params/agent.yaml 与 params/env.yaml 的逐项比较（命令行覆盖已体现在其中）；
末段指标取 TensorBoard 中 Metrics/ee_pose/position_error 最后 20 次的平均（重置时刻的值，见 4.13），
它只用于粗看，正式结论仍用 eval_reach.py 的评估。
"""

import argparse
import glob
import os

import yaml


class _Loader(yaml.SafeLoader):
    """dump_yaml 写出的 yaml 里有 !!python/tuple 与 slice 两种标签；安全地读成 tuple 与字符串，不执行任何代码。"""


_Loader.add_constructor("tag:yaml.org,2002:python/tuple", lambda l, n: tuple(l.construct_sequence(n)))
_Loader.add_multi_constructor("tag:yaml.org,2002:python/object/apply:builtins.slice", lambda l, s, n: "slice")

IGNORED = {"log_dir", "run_name", "experiment_name"}  # 每次都不同、不算"改动"的项


def flatten(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flatten(v, f"{prefix}{k}."))
    else:
        out[prefix[:-1]] = d
    return out


def load_params(run):
    flat = {}
    for name in ("agent", "env"):
        with open(os.path.join(run, "params", f"{name}.yaml")) as f:
            flat.update({f"{name}.{k}": v for k, v in flatten(yaml.load(f, Loader=_Loader)).items()})
    return flat


def shortest_new_prefix(key, other):
    """key 在 other 中不存在。返回 key 在 other 中"不存在或原本是单个值"的最短前缀。
    例：基线里 observations.policy.joint_pos.noise 为 None，本次是一整块噪声配置，返回该前缀，而不是更短的 observations.policy。"""
    parts = key.split(".")
    other_prefixes = {".".join(k.split(".")[:i]) for k in other for i in range(1, k.count(".") + 2)}
    for i in range(2, len(parts) + 1):
        prefix = ".".join(parts[:i])
        if prefix not in other_prefixes or prefix in other:  # 另一边没有这个前缀，或那里是单个值（如 None）
            return prefix
    return key


def tail_metric(run, tag="Metrics/ee_pose/position_error", n=20):
    from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

    events = sorted(glob.glob(os.path.join(run, "events.out.tfevents.*")))
    if not events:
        return float("nan")
    ea = EventAccumulator(events[-1], size_guidance={"scalars": 0})
    ea.Reload()
    if tag not in ea.Tags()["scalars"]:
        return float("nan")
    vals = [p.value for p in ea.Scalars(tag)][-n:]
    return sum(vals) / len(vals)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("log_root", help="如 logs/rsl_rl/galbot_reach")
    parser.add_argument("--base", required=True, help="基线运行的目录名")
    parser.add_argument("--filter", default="", help="只列目录名含此字符串的运行")
    args = parser.parse_args()

    runs = sorted(d for d in glob.glob(os.path.join(args.log_root, "*")) if os.path.isdir(os.path.join(d, "params")))
    runs = [r for r in runs if args.filter in os.path.basename(r)]
    base = load_params(os.path.join(args.log_root, args.base))

    print("| 运行 | 种子 | 迭代 | 检查点数 | 相对基线的改动 | 末段位置误差 |")
    print("|---|---|---|---|---|---|")
    for run in runs:
        p = load_params(run)
        diff = []
        for k in sorted(set(p) | set(base)):
            if p.get(k) == base.get(k) or k.rsplit(".", 1)[-1] in IGNORED:
                continue
            if k in p and k in base:
                diff.append(f"{k.split('.', 1)[1]}={p[k]}")
            else:  # 只在一边出现：报告另一边不存在的最短前缀，即真正新增 / 删除的那一块
                other = base if k in p else p
                block = shortest_new_prefix(k, other)
                diff.append(f"{'+' if k in p else '-'}{block.split('.', 1)[1]}")
        diff = list(dict.fromkeys(diff))  # agent.seed 与 env.seed 等重复项只留一个
        n_ckpt = len(glob.glob(os.path.join(run, "model_*.pt")))
        print(f"| {os.path.basename(run)} | {p.get('agent.seed')} | {p.get('agent.max_iterations')} | {n_ckpt} | "
              f"{'；'.join(diff) or '无'} | {tail_metric(run) * 100:.2f} cm |")


if __name__ == "__main__":
    main()
