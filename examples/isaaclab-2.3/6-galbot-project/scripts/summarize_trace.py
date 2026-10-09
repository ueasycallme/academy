# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Python 3.11（只用标准库，不需要 Isaac Sim）；trace 由 Isaac Sim 5.1.0 的 carb.profiler-cpu 生成
# 验证日期：2026-10-10
"""汇总 Kit CPU profiler 写出的 Chrome trace（JSON），按区段名累计耗时（7.2）。

trace 的生成方法见 7.2：训练命令后加 --kit_args，打开 cpu 后端并让它写成未压缩的 JSON。
区段是嵌套的，所以各行的"累计"是含子区段的总时间，不能相加。

    python scripts/summarize_trace.py generated/profile/kit_trace.json --top 20
    python scripts/summarize_trace.py generated/profile/kit_trace.json --grep physx
"""

import argparse
import collections
import json

parser = argparse.ArgumentParser()
parser.add_argument("trace", help="Chrome trace JSON（compressProfile=0）")
parser.add_argument("--top", type=int, default=20)
parser.add_argument("--grep", default=None, help="只看名字里含这个字符串的区段（不区分大小写）")
args = parser.parse_args()

with open(args.trace) as f:
    events = json.load(f)
threads = {e["tid"]: e["args"]["name"] for e in events if e.get("ph") == "M" and e.get("name") == "thread_name"}
total = collections.defaultdict(float)  # 区段名 → 累计时长（μs）
count = collections.Counter()
thread_of = {}
t_min, t_max = float("inf"), 0.0
for e in events:
    if e.get("ph") != "X":
        continue
    name = e["name"]
    if args.grep and args.grep.lower() not in name.lower():
        continue
    total[name] += e["dur"]
    count[name] += 1
    thread_of.setdefault(name, threads.get(e["tid"], str(e["tid"])))
    t_min, t_max = min(t_min, e["ts"]), max(t_max, e["ts"] + e["dur"])

print(f"[INFO] {len(events)} 个事件，覆盖 {(t_max - t_min) / 1e6:.1f} s；按累计耗时排序的前 {args.top} 个区段：")
print(f"{'累计 s':>9} {'次数':>8} {'平均 ms':>9}  区段（线程）")
for name, us in sorted(total.items(), key=lambda kv: -kv[1])[: args.top]:
    print(f"{us / 1e6:9.2f} {count[name]:8d} {us / count[name] / 1e3:9.3f}  {name[:70]}（{thread_of[name][:30]}）")
