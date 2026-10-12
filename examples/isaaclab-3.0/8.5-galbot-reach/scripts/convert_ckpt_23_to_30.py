# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：rsl-rl-lib 3.1.2 的检查点（Isaac Lab 2.3.2）→ rsl-rl-lib 5.4.1（Isaac Lab v3.0.0-EA）
# 验证日期：2026-10-12
# GPU：不需要（只读写检查点文件）
"""把 2.3 主线的 rsl_rl 检查点改写成 3.0 的 rsl_rl 5.x 能加载的格式（8.10）。只改键名，不改数值。

rsl_rl 3.1.2 存一个 `model_state_dict`（`std`、`actor.*`、`critic.*`）；5.4.1 分开存 `actor_state_dict`
（`distribution.std_param`、`mlp.*`）与 `critic_state_dict`（`mlp.*`）。直接加载会报 `KeyError: 'actor_state_dict'`。
优化器状态不转换（评估不需要），加载时要用 eval_reach.py 的 --load_models_only。

    python scripts/convert_ckpt_23_to_30.py <2.3 运行>/model_999.pt model_999_as30.pt
"""

import sys

import torch

src, dst = sys.argv[1], sys.argv[2]
old = torch.load(src, map_location="cpu", weights_only=False)
m = old["model_state_dict"]
actor = {"distribution.std_param": m["std"], **{k.replace("actor.", "mlp.", 1): v for k, v in m.items() if k.startswith("actor.")}}
critic = {k.replace("critic.", "mlp.", 1): v for k, v in m.items() if k.startswith("critic.")}
unknown = [k for k in m if k != "std" and not k.startswith(("actor.", "critic."))]
if unknown:
    raise SystemExit(f"未知的键（例如观测归一化），本脚本不处理：{unknown}")
torch.save({"actor_state_dict": actor, "critic_state_dict": critic, "iter": old["iter"], "infos": old.get("infos")}, dst)
print(f"[8.10] {src} → {dst}：actor {len(actor)} 项，critic {len(critic)} 项；iter {old['iter']}；优化器状态未转换")
