# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.10（系统 python3，pytest 6.2.5）/ 3.10（CI，pytest 8.3.3）/ 3.11（Isaac 环境，pytest 9.1.1）；不依赖 Isaac Sim
# 验证日期：2026-10-11
"""无 GPU：评估报告的统计（6.6.2）。"""

import csv

import pytest

eval_report = pytest.importorskip("eval_report")  # 需要 numpy 与 matplotlib


def test_wilson_matches_6_6_2():
    # 6.6.2 表 3 第一行：768 个样本里 621 个 < 5 cm → 80.9%（77.9–83.5）
    lo, hi = eval_report.wilson(621, 768)
    assert (round(lo * 100, 1), round(hi * 100, 1)) == (77.9, 83.5)


def test_reach_table_from_fixed_csv(tmp_path, capsys):
    rows = [{"seed": 0, "task": "t", "widen": 0, "env": i, "segment": 1, "target_x": 0.4, "target_y": -0.3,
             "target_z": 1.3, "pos_err": e, "rot_err": 0.05, "moved": 0.1} for i, e in enumerate([0.01, 0.03, 0.08, 0.02])]
    path = tmp_path / "eval.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    eval_report.reach_tables(eval_report.load([str(path)]), "fixture")
    out = capsys.readouterr().out
    assert "4 个样本" in out and "中位数 2.50 cm" in out and "75.0%" in out
