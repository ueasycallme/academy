#!/bin/bash
# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（isaaclab_mimic 1.0.16，robomimic 0.4.0）
# 验证日期：2026-10-10
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
#
# Mimic 最小流程（4.19）：官方 10 条示范 → 自动标注 → 生成 10 条 → BC 训练 5 个 epoch。
# 用法：在 Isaac Lab 仓库根目录下执行  bash <本文件路径>
# 依赖：已激活装好 Isaac Lab 的 Python 环境（python 指向它）；当前目录是 Isaac Lab 克隆。
set -e
export PYTHONUNBUFFERED=1  # Kit 退出时不刷新 stdout 缓冲，不加这一行会看不到标注与生成的打印
mkdir -p datasets

# 0) 官方提供的 10 条人类示范（Isaac-Stack-Cube-Franka-IK-Rel-v0，约 3 MB）
[ -f datasets/dataset.hdf5 ] || curl -fL -o datasets/dataset.hdf5 \
  https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/IsaacLab/Mimic/franka_stack_datasets/dataset.hdf5

# 1) 标注：在 Mimic 版任务里回放每条示范，自动记下子任务完成信号与物体 / 末端位姿
python scripts/imitation_learning/isaaclab_mimic/annotate_demos.py --headless --device cpu \
  --task Isaac-Stack-Cube-Franka-IK-Rel-Mimic-v0 --auto \
  --input_file ./datasets/dataset.hdf5 --output_file ./datasets/annotated_dataset.hdf5

# 2) 生成：10 个并行环境，直到得到 10 条成功的示范
python scripts/imitation_learning/isaaclab_mimic/generate_dataset.py --headless --device cpu \
  --num_envs 10 --generation_num_trials 10 \
  --input_file ./datasets/annotated_dataset.hdf5 --output_file ./datasets/generated_dataset_small.hdf5

# 3) 训练：robomimic BC-RNN，只跑 5 个 epoch 验证流程（默认 2000）
python scripts/imitation_learning/robomimic/train.py \
  --task Isaac-Stack-Cube-Franka-IK-Rel-v0 --algo bc \
  --dataset ./datasets/generated_dataset_small.hdf5 --epochs 5
