# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.10（系统 python3）/ 3.11（Isaac 环境）；不依赖 Isaac Sim
# 验证日期：2026-10-11
"""无 GPU：版本核对的比较规则（7.6）。"""

from check_versions import EXPECTED, compare


def test_prefix_match_accepts_build_suffixes():
    installed = dict(EXPECTED, isaacsim="5.1.0.0", torch="2.7.0+cu128")
    assert compare(EXPECTED, installed) == []


def test_reports_mismatch_and_missing():
    installed = dict(EXPECTED, isaaclab="0.54.3", **{"rsl-rl-lib": None})
    problems = compare(EXPECTED, installed)
    assert problems == ["isaaclab：0.54.3（期望 0.54.2）", "rsl-rl-lib：未安装（期望 3.1.2）"]


def test_prefix_is_not_a_loose_startswith():
    # 5.1.01 不能算 5.1.0
    assert compare({"isaacsim": "5.1.0"}, {"isaacsim": "5.1.01"}) == ["isaacsim：5.1.01（期望 5.1.0）"]
