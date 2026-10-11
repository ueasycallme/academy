# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Lab 2.3.2（h5py，用 Isaac Lab 环境里的 Python 即可，不启动 Isaac Sim）
# 验证日期：2026-10-10
"""查看 Mimic 流水线各步的 HDF5（4.19）：回合数、成功标记、子任务边界、长度分布；可选比较两份标注。

用法::

    python inspect_mimic_data.py datasets/dataset.hdf5
    python inspect_mimic_data.py datasets/annotated_dataset.hdf5
    python inspect_mimic_data.py datasets/generated_dataset_small.hdf5
    python inspect_mimic_data.py datasets/annotated_dataset.hdf5 --compare datasets/annotated_gpu.hdf5
"""

import argparse

import h5py
import numpy as np


def boundaries(demo: h5py.Group) -> dict[str, int] | None:
    """每个子任务完成信号第一次变为 True 的步号（标注后才有）。"""
    key = "obs/datagen_info/subtask_term_signals"
    if key not in demo:
        return None
    return {n: int(np.argmax(demo[key][n][:])) for n in demo[key]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--compare", default=None, help="另一份标注文件：比较子任务边界与回放结束时方块的位置")
    args = parser.parse_args()

    data = h5py.File(args.file, "r")["data"]
    lens = [data[k]["actions"].shape[0] for k in data]
    ok = sum(bool(data[k].attrs.get("success", False)) for k in data)
    print(f"{args.file}：{len(data)} 个回合，成功 {ok}；长度 最短 {min(lens)} / 中位 {int(np.median(lens))} / 最长 {max(lens)} 步")
    print(f"  env_args={data.attrs.get('env_args')}")
    first = data[sorted(data)[0]]
    print(f"  {sorted(data)[0]} 的顶层组：{list(first.keys())}；obs：{list(first['obs'].keys())}")
    if "obs/datagen_info" in first:
        first["obs/datagen_info"].visititems(lambda n, o: print(f"    datagen_info/{n} {o.shape}") if isinstance(o, h5py.Dataset) else None)
    for k in data:
        b = boundaries(data[k])
        if b is not None:
            print(f"  {k}：{lens[list(data).index(k)]} 步，子任务完成于 {b}")

    if args.compare:
        other = h5py.File(args.compare, "r")["data"]
        for k in data:
            same = boundaries(data[k]) == boundaries(other[k])
            pa = data[k]["states/rigid_object/cube_3/root_pose"][-1, :3]
            pb = other[k]["states/rigid_object/cube_3/root_pose"][-1, :3]
            print(f"  {k}：边界相同 {same}；回放结束时 cube_3 位置差 {np.abs(pa - pb).max() * 1000:.2f} mm")


if __name__ == "__main__":
    main()
