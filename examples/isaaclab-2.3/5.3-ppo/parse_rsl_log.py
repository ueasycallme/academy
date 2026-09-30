# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：rsl-rl-lib 3.1.2 的终端输出格式（Isaac Lab 2.3.2 的 rsl_rl/train.py）
# 验证日期：2026-09-30
"""从 RSL-RL 训练的终端输出中抽取指定迭代的指标，并找出平均回合长度第一次达到阈值的迭代。

不需要 Isaac Sim，普通 Python 3.10+ 即可::

    python parse_rsl_log.py train.log --iters 0 10 30 50 100 149 --target_len 299
"""

import argparse
import re

KEYS = {
    "Mean reward": "reward",
    "Mean episode length": "len",
    "Mean action noise std": "std",
    "Episode_Termination/time_out": "time_out",
    "Episode_Termination/cart_out_of_bounds": "out_of_bounds",
}


def parse(path: str) -> list[dict]:
    text = re.sub(r"\x1b\[[0-9;]*m", "", open(path, encoding="utf-8", errors="replace").read())
    rows = []
    for block in re.split(r"\n\s*Learning iteration ", text)[1:]:
        row = {"it": int(block.split("/")[0])}
        for key, name in KEYS.items():
            m = re.search(re.escape(key) + r":\s+([-\d.]+)", block)
            row[name] = float(m.group(1)) if m else None
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", help="保存下来的训练终端输出")
    parser.add_argument("--iters", type=int, nargs="*", default=[0, 10, 30, 50, 100, 149])
    parser.add_argument("--target_len", type=float, default=299.0)
    args = parser.parse_args()
    rows = parse(args.log)
    print(f"共 {len(rows)} 次迭代")
    print(" 迭代 | Mean reward | Mean episode length | noise std | time_out / out_of_bounds")
    for r in rows:
        if r["it"] in args.iters:
            print(f"{r['it']:5d} | {r['reward']:11.2f} | {r['len']:19.2f} | {r['std']:9.2f} | {r['time_out']:.2f} / {r['out_of_bounds']:.2f}")
    first = next((r["it"] for r in rows if r["len"] is not None and r["len"] >= args.target_len), None)
    print(f"平均回合长度第一次 ≥ {args.target_len} 的迭代：{first}")


if __name__ == "__main__":
    main()
