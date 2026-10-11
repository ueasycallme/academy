# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2
# 验证日期：2026-10-11
"""让 Isaac Lab 自带的脚本认识本项目的任务（6.4.7）：原样运行官方脚本，只在它启动 Kit 之后顺带导入 galbot_academy.tasks。

annotate_demos.py、generate_dataset.py、robomimic/train.py、robomimic/play.py 都只导入官方的任务包，
不认识 Galbot-PickPlace-IK-Rel-*。Isaac Lab 3.0 为此加了 --external_callback（4.19 版本说明），2.3.2 没有。
我们的任务模块又必须在 Kit 启动之后才能导入（它们 import 了 isaaclab.sim 等），不能在调用官方脚本之前先导入。
这几个脚本都先创建 AppLauncher 再做别的事，所以这里把 AppLauncher.__init__ 包一层：Kit 起来之后立刻导入本项目的任务包。
官方脚本本身一行不改。

    python scripts/run_isaaclab_script.py <IsaacLab>/scripts/imitation_learning/isaaclab_mimic/annotate_demos.py --headless ...
"""

import importlib
import runpy
import sys

from isaaclab.app import AppLauncher

_original_init = AppLauncher.__init__


def _init_then_register(self, *args, **kwargs):
    _original_init(self, *args, **kwargs)
    importlib.import_module("galbot_academy.tasks")
    print("[run_isaaclab_script] 已注册 galbot_academy.tasks", flush=True)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    script = sys.argv[1]
    sys.argv = sys.argv[1:]  # 官方脚本看到的 argv[0] 是它自己
    AppLauncher.__init__ = _init_then_register  # 官方脚本 `from isaaclab.app import AppLauncher` 拿到的是同一个类
    runpy.run_path(script, run_name="__main__")


if __name__ == "__main__":
    main()
