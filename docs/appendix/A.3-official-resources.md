---
title: 官方资源导航（文档、论坛、GitHub、论文）
updated: 2026-10-09
sources_checked: 2026-10-09
---

# 官方资源导航（文档、论坛、GitHub、论文）

**怎么用这一页**：遇到本站没讲到、或想看原文的内容，按下表找官方入口。表按 [0.2 分层依赖图](../0-map/0.2-layers.md) 自上而下分组；每行写了"什么时候来这里"和本站对应的页面。表中链接均在 2026-10-09 确认可以访问。

## 官方入口

**Isaac Lab**

| 资源 | 链接 | 什么时候来这里 | 本站对应 |
|---|---|---|---|
| 文档（v2.3.2） | <https://isaac-sim.github.io/IsaacLab/v2.3.2/index.html> | 查本站主线版本的 API、教程 | [4.1](../4-isaaclab/4.1-why-isaac-lab.md)、[4.2](../4-isaaclab/4.2-repo-map.md) |
| 文档（main / 3.0 EA） | <https://isaac-sim.github.io/IsaacLab/main/index.html>、<https://isaac-sim.github.io/IsaacLab/v3.0.0-EA/index.html> | 看最新开发版、3.0 | [8.1](../8-frontier/8.1-what-changed.md) |
| GitHub | <https://github.com/isaac-sim/IsaacLab> | 读源码、对 tag 取 permalink | [4.2](../4-isaaclab/4.2-repo-map.md) |
| Releases | <https://github.com/isaac-sim/IsaacLab/releases> | 看版本变化与已知问题 | [8.6](../8-frontier/8.6-version-tracking.md) |
| Discussions | <https://github.com/isaac-sim/IsaacLab/discussions> | 用法类问题、经验交流 | — |
| 论文 | Mittal et al., Orbit: A Unified Simulation Framework for Interactive Robot Learning Environments, arXiv:2301.04195 <https://arxiv.org/abs/2301.04195> | 引用 Isaac Lab 的前身 Orbit | [0.3](../0-map/0.3-lineage.md) |

**Isaac Sim**

| 资源 | 链接 | 什么时候来这里 | 本站对应 |
|---|---|---|---|
| 文档（5.1.0） | <https://docs.isaacsim.omniverse.nvidia.com/5.1.0/index.html> | 查本站主线版本的安装、GUI、Python API | [1.4](../1-env/1.4-install-51-232.md)、第 3 部分 |
| 文档（6.1.0） | <https://docs.isaacsim.omniverse.nvidia.com/6.1.0/index.html> | 配合 Isaac Lab 3.0 | [8.1](../8-frontier/8.1-what-changed.md) |
| Release Notes（5.1.0） | <https://docs.isaacsim.omniverse.nvidia.com/5.1.0/overview/release_notes.html> | 查已知问题、弃用说明 | [1.1](../1-env/1.1-compat-matrix.md) |
| 下载页（含 WebRTC 客户端） | <https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/download.html> | 下载二进制包、livestream 客户端 | [1.7](../1-env/1.7-install-methods.md)、[7.1](../7-infra/7.1-headless-remote.md) |
| GitHub | <https://github.com/isaac-sim/IsaacSim> | 读 Isaac Sim 的扩展源码 | [2.6](../2-usd-kit/2.6-what-is-kit.md) |
| 论坛（Isaac Sim 板块） | <https://forums.developer.nvidia.com/c/omniverse/simulation/69> | Isaac Sim 本身的问题 | [1.9](../1-env/1.9-install-troubleshooting.md) |

**Omniverse Kit 与 USD**

| 资源 | 链接 | 什么时候来这里 | 本站对应 |
|---|---|---|---|
| Kit 手册 | <https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/index.html> | 体验文件、扩展、设置 | [2.6](../2-usd-kit/2.6-what-is-kit.md)、[2.7](../2-usd-kit/2.7-extensions.md) |
| OpenUSD 官方文档 | <https://openusd.org/release/index.html> | USD 概念、合成规则、API | [2.1](../2-usd-kit/2.1-why-usd.md)–[2.3](../2-usd-kit/2.3-layers-composition.md) |
| usd-core（PyPI） | <https://pypi.org/project/usd-core/> | 不装 Isaac Sim，只用 USD 的 Python 库 | [2.5](../2-usd-kit/2.5-usd-python.md) |

**物理引擎**

| 资源 | 链接 | 什么时候来这里 | 本站对应 |
|---|---|---|---|
| PhysX GitHub | <https://github.com/NVIDIA-Omniverse/PhysX> | PhysX SDK 源码与版本 | [3.3](../3-isaacsim/3.3-rigid-collision.md)、[3.4](../3-isaacsim/3.4-articulation.md) |
| PhysX SDK 文档 | <https://nvidia-omniverse.github.io/PhysX/physx/5.6.1/index.html> | 求解器、关节、接触的原理 | 同上（链接为 5.6.1 版；Isaac Sim 5.1 内置的 SDK 具体版本本站未核对） |
| Newton GitHub / 文档 | <https://github.com/newton-physics/newton>、<https://newton-physics.github.io/newton/> | Isaac Lab 3.0 的 Newton 后端 | [8.1](../8-frontier/8.1-what-changed.md)、[8.3](../8-frontier/8.3-newton.md) |
| Warp GitHub / 文档 | <https://github.com/NVIDIA/warp>、<https://nvidia.github.io/warp/> | Warp 内核、3.0 的数据类型 | [0.4](../0-map/0.4-isaac-names.md) |

**RL 库**

| 资源 | 链接 | 什么时候来这里 | 本站对应 |
|---|---|---|---|
| rsl_rl | <https://github.com/leggedrobotics/rsl_rl> | 本站主线用的 PPO 实现 | [5.3](../5-rl/5.3-ppo.md)、[6.5.1](../6-galbot/5-train/6.5.1-train-reach-rsl-rl.md) |
| skrl | <https://github.com/Toni-SM/skrl>、<https://skrl.readthedocs.io/en/latest/> | 换用 skrl 时 | [4.16](../4-isaaclab/4.16-rl-wrappers.md) |
| rl_games | <https://github.com/Denys88/rl_games> | 换用 rl_games 时 | [4.16](../4-isaaclab/4.16-rl-wrappers.md) |
| Stable-Baselines3 | <https://github.com/DLR-RM/stable-baselines3>、<https://stable-baselines3.readthedocs.io/en/master/> | 换用 SB3 时 | [4.16](../4-isaaclab/4.16-rl-wrappers.md) |

**主线机器人**

| 资源 | 链接 | 什么时候来这里 | 本站对应 |
|---|---|---|---|
| Galbot One Golf 描述仓库 | <https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description> | URDF、USD、网格（本站固定在 commit 2d496b0） | [6.1.1](../6-galbot/1-asset/6.1.1-galbot-repo.md) |

## 本站与官方的关系

本站是官方文档之上的"导读层"：讲清体系框架、核心概念与工程落地，解释为原创，细节链接到官方文档与源码，不搬运原文。版本以 Isaac Sim 5.1.0 + Isaac Lab 2.3.2 为准，3.0 见第 8 部分。

中文翻译站 <https://isaac.kiloong.com/> 是官方文档的中文版，可以作延伸阅读。它译自最新版，内容可能与 5.1.0 / 2.3.2 不一致；涉及具体参数、API 时，以对应版本的英文原文为准。

## 提问与求助

| 问题在哪一层 | 去哪里问 |
|---|---|
| Isaac Sim 本身（安装、GUI、PhysX、渲染） | NVIDIA 开发者论坛的 Isaac Sim 板块 |
| Isaac Lab 的 bug | Isaac Lab GitHub Issues，按 bug 模板填写 |
| Isaac Lab 的用法 | Isaac Lab GitHub Discussions |

Isaac Lab 的 bug 模板（v2.3.2）要求：重现步骤、Isaac Lab 的 commit、Isaac Sim 版本、操作系统、GPU、CUDA 与驱动版本，并勾选"已搜索过没有相同的 issue""问题不在 Isaac Sim 本身"两项[^bug-tpl]。提问前的自查清单与信息收集见 [1.9 的"如何提问"](../1-env/1.9-install-troubleshooting.md)，这里不重复。

## 怎么看文档的版本号

- **Isaac Lab 文档**：版本写在 URL 的第一段路径里，如 `…/IsaacLab/v2.3.2/…`、`…/IsaacLab/main/…`。页面上也有版本切换菜单。搜索引擎给出的链接常常是 `main`，要换成 `v2.3.2` 再看。
- **Isaac Sim 文档**：版本也在 URL 里，如 `docs.isaacsim.omniverse.nvidia.com/5.1.0/…`。把 `5.1.0` 换成 `6.1.0`，就是另一个版本的同一页（如果该页存在）。
- 本站引用官方文档时，链接都带版本号；引用源码时，都用带 tag 的 permalink。

## 维护规则

新增一行时写明四栏：资源名、链接、什么时候来这里、本站对应页面（没有就写"—"）。新增或改动链接后，用 `curl -L` 确认能访问，把页首的"确认可以访问"日期改为当天。官方入口改版、地址变化时，由发现的会话报给设计会话，开微任务更新；链接失效又找不到替代时，保留这一行并注明"失效于某日"，不直接删除。

## 延伸阅读

- 版本与兼容关系：[1.1 兼容矩阵](../1-env/1.1-compat-matrix.md)；3.0 的版本追踪：[8.6](../8-frontier/8.6-version-tracking.md)

## 版本说明

本页链接的版本以 Isaac Sim 5.1.0 + Isaac Lab 2.3.2 为主，3.0 相关入口另行标注。

[^bug-tpl]: Isaac Lab `.github/ISSUE_TEMPLATE/bug.md`（tag v2.3.2）<https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/.github/ISSUE_TEMPLATE/bug.md>
