#!/usr/bin/env bash
# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 验证版本：nvcr.io/nvidia/isaac-sim:5.1.0 镜像 + Isaac Lab 2.3.2；Docker 29.9.1、Compose v5.6.0、NVIDIA Container Toolkit 1.20.1
# 验证日期：2026-10-20
# GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04
# 在本目录运行：构建镜像 → 转换 Galbot USD → 冒烟训练 → 把日志拷到宿主（1.6）。
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PY=/isaac-sim/python.sh

docker compose build
# 第一次运行要转换 USD（需要 GPU）；结果在 galbot-generated 卷里，之后不用再转
docker compose run --rm galbot -c "$PY scripts/convert_galbot.py --headless"
# 冒烟：10 次迭代
docker compose run --rm galbot -c "$PY scripts/rsl_rl/train.py --task Galbot-Reach-v0 --headless --num_envs 64 --max_iterations 10"
# 日志在命名卷里；用一个临时容器拷出来，并把属主改成本目录的属主。
# 不用 $(id -g)：刚加入 docker 组、用 sg docker 执行时，它取到的是 docker 组（1.6 本站实测记录）
mkdir -p artifacts
docker compose run --rm -v "$PWD/artifacts:/out" galbot -c "cp -r logs /out/ && chown -R $(stat -c %u:%g .) /out"
echo "日志已拷到 $PWD/artifacts/logs"
