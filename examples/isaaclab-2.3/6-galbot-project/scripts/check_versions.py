# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；不启动 Isaac Sim
# 验证日期：2026-10-11
"""核对当前 Python 环境里的关键包版本是否与本项目验证过的一致（7.6）。不一致时返回码 1。

只读包的元数据（importlib.metadata），不导入、不启动 Isaac Sim，几十毫秒跑完。团队里每人提交前、换机器后各跑一次：

    python scripts/check_versions.py
"""

import sys
from importlib.metadata import PackageNotFoundError, version

# 本项目验证过的版本（Isaac Lab v2.3.2 各包版本见各自的 config/extension.toml；rsl-rl-lib 由 isaaclab_rl 的 setup.py 钉死）
EXPECTED = {
    "isaacsim": "5.1.0",
    "isaaclab": "0.54.2",
    "isaaclab_tasks": "0.11.12",
    "isaaclab_rl": "0.4.7",
    "rsl-rl-lib": "3.1.2",
    "torch": "2.7.0",
}


def compare(expected: dict[str, str], installed: dict[str, str | None]) -> list[str]:
    """返回不一致的条目说明；版本号按前缀比较（isaacsim 的 5.1.0.0 算 5.1.0，torch 的 2.7.0+cu128 算 2.7.0）。"""
    problems = []
    for name, want in expected.items():
        got = installed.get(name)
        if got is None:
            problems.append(f"{name}：未安装（期望 {want}）")
        elif not (got == want or got.startswith(want + ".") or got.startswith(want + "+")):
            problems.append(f"{name}：{got}（期望 {want}）")
    return problems


def installed_versions(names) -> dict[str, str | None]:
    out = {}
    for name in names:
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            out[name] = None
    return out


def main() -> int:
    installed = installed_versions(EXPECTED)
    for name, got in installed.items():
        print(f"  {name:<16}{got or '-'}")
    problems = compare(EXPECTED, installed)
    if problems:
        print("[check_versions] 与本项目验证过的版本不一致：\n  " + "\n  ".join(problems))
        return 1
    print("[check_versions] 全部一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
