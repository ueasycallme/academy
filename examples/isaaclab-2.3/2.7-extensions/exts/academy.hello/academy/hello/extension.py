# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）
# 验证日期：2026-10-08
"""最小扩展：启用时 on_startup，停用时 on_shutdown，各打印一行。"""

import carb
import omni.ext


def greet() -> str:
    """扩展对外提供的一个普通函数：启用之后，别的代码可以 import academy.hello 来调用它。"""
    return "hello from academy.hello"


class HelloExtension(omni.ext.IExt):
    def on_startup(self, ext_id: str) -> None:
        carb.log_warn(f"[academy.hello] on_startup：{ext_id}")  # 用 warn 级别，默认日志设置下也能看到
        print(f"[academy.hello] on_startup：{ext_id}", flush=True)

    def on_shutdown(self) -> None:
        print("[academy.hello] on_shutdown", flush=True)
