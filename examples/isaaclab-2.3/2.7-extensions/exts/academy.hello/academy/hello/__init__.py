# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
# Kit 在 [[python.module]] 列出的模块里找 omni.ext.IExt 的子类，所以要在这里把它导入进来
from .extension import HelloExtension, greet  # noqa: F401
