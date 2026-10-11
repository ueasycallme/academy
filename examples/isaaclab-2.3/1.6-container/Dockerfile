# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
#
# 未验证（本机无 Docker）：按 Isaac Sim 5.1.0 容器文档与 Isaac Lab v2.3.2 docker/Dockerfile.base 写成，只做过人工核对（1.6）。
# 在官方 Isaac Sim 镜像上装 Isaac Lab 2.3.2（只带 rsl_rl）与本站主线项目 galbot_academy。
# 构建上下文是 examples/isaaclab-2.3/（见 compose.yaml 的 build.context）。

ARG ISAACSIM_VERSION=5.1.0
FROM nvcr.io/nvidia/isaac-sim:${ISAACSIM_VERSION}

SHELL ["/bin/bash", "-c"]
# 与 Isaac Lab 的 Dockerfile.base 一样以 root 安装与运行；Isaac Sim 文档的 docker run 用的是 1234 用户（1.6 坑一）
USER root
ENV ACCEPT_EULA=Y \
    OMNI_KIT_ALLOW_ROOT=1 \
    DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    ISAACLAB_PATH=/workspace/isaaclab \
    GALBOT_GENERATED_DIR=/workspace/generated

# 1. 系统依赖：与 Dockerfile.base 相同的几个包（编译扩展、克隆仓库）
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake git libglib2.0-0 ncurses-term wget && \
    rm -rf /var/lib/apt/lists/*

# 2. Isaac Lab 2.3.2：按 tag 克隆，并把镜像里的 Isaac Sim 链到 _isaac_sim（isaaclab.sh 靠它找 Python）
RUN git clone --depth 1 --branch v2.3.2 https://github.com/isaac-sim/IsaacLab.git ${ISAACLAB_PATH} && \
    ln -sf /isaac-sim ${ISAACLAB_PATH}/_isaac_sim
RUN ${ISAACLAB_PATH}/isaaclab.sh --install rsl_rl

# 3. 本站主线项目：只拷源码与脚本；生成的 USD 与训练日志放到卷里（compose.yaml）
COPY 6-galbot-project/source /workspace/galbot-project/source
COPY 6-galbot-project/scripts /workspace/galbot-project/scripts
RUN /isaac-sim/python.sh -m pip install -e /workspace/galbot-project/source/galbot_academy

# 4. Galbot 描述仓库：按项目固定的 commit 克隆（Apache-2.0，6.1.1）。USD 要用 GPU 转换，构建阶段没有 GPU，留到运行时
RUN bash /workspace/galbot-project/scripts/fetch_galbot.sh

WORKDIR /workspace/galbot-project
ENTRYPOINT ["bash"]
