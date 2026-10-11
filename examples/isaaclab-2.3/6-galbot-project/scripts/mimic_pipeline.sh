#!/bin/bash
# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（isaaclab_mimic 1.0.16，robomimic 0.4.0）
# 验证日期：2026-10-11
# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04
#
# 6.4.7 的四步：标注 → 生成 → 训练 → 评估。每步都是 Isaac Lab 自带的脚本，经 run_isaaclab_script.py 运行（让它们认识本项目的任务）。
# 用法（在项目根目录）：
#   ISAACLAB=<Isaac Lab 克隆> bash scripts/mimic_pipeline.sh [步骤...]
#   步骤：annotate generate train play，缺省为全部。规模用环境变量调：
#   NUM_GEN（生成条数，默认 200）、GEN_ENVS（并行环境，默认 10）、EPOCHS（默认 200）、ROLLOUTS（评估回合，默认 100）、CKPT（评估用的检查点）
set -e
export PYTHONUNBUFFERED=1  # Kit 退出时不刷新 stdout 缓冲，不加会丢打印（4.19）
: "${ISAACLAB:?请把 ISAACLAB 设为 Isaac Lab 克隆的路径}"
RUN="python scripts/run_isaaclab_script.py"
M=$ISAACLAB/scripts/imitation_learning
NUM_GEN=${NUM_GEN:-200}; GEN_ENVS=${GEN_ENVS:-10}; EPOCHS=${EPOCHS:-200}; ROLLOUTS=${ROLLOUTS:-100}
STEPS=${*:-annotate generate train play}

for s in $STEPS; do
  case $s in
  annotate)  # 6.4.6 录的 10 条 → 加上子任务信号与位姿（--auto：信号来自环境的 subtask_terms）
    # 不加 --device cpu：示范是在 GPU 上录的，标注是开环重放，换到 CPU 上 10 条全部重放失败（6.4.7 坑）
    $RUN $M/isaaclab_mimic/annotate_demos.py --headless --auto \
      --task Galbot-PickPlace-IK-Rel-Mimic-v0 \
      --input_file ./datasets/galbot_pick_place.hdf5 --output_file ./datasets/galbot_pick_place_annotated.hdf5 ;;
  generate)
    $RUN $M/isaaclab_mimic/generate_dataset.py --headless --device cpu \
      --num_envs $GEN_ENVS --generation_num_trials $NUM_GEN \
      --input_file ./datasets/galbot_pick_place_annotated.hdf5 --output_file ./datasets/galbot_pick_place_generated.hdf5 ;;
  train)
    $RUN $M/robomimic/train.py --task Galbot-PickPlace-IK-Rel-v0 --algo bc \
      --dataset ./datasets/galbot_pick_place_generated.hdf5 --epochs $EPOCHS --log_dir robomimic \
      --name bc_rnn_$(date +%m%d_%H%M%S) ;;  # 实验名已存在时 robomimic 会在 stdin 上问"overwrite? (y/n)"，非交互运行直接 EOFError
  play)
    : "${CKPT:?请把 CKPT 设为 logs/robomimic/.../models/model_epoch_N.pth}"
    $RUN $M/robomimic/play.py --headless --task Galbot-PickPlace-IK-Rel-v0 \
      --checkpoint $CKPT --num_rollouts $ROLLOUTS --horizon 900 --seed 101 ;;
  *) echo "未知步骤 $s"; exit 1 ;;
  esac
done
