---
title: Isaac Academy
updated: 2026-09-30
---

# Isaac Academy

Isaac Academy 是 Isaac Sim / Isaac Lab 的中文学习网站，定位是官方文档之上的"导读层"：讲清体系框架、核心概念和工程落地。解释是原创的，API 细节与参数说明链接到官方文档和源码，不搬运原文。

- **主线版本**：Isaac Sim 5.1.0 + Isaac Lab 2.3.2。
- **前沿专栏**：Isaac Sim 6.1 + Isaac Lab 3.0.0-EA，内容可能随版本变动。
- **主线机器人**：[Galbot One Golf](https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description)，从资产导入走到策略部署。
- **读者起点**：会 Python，没有接触过 Isaac / USD，没有强化学习基础。

## 与 isaac.kiloong.com 的关系

| 站点 | 内容 | 用法 |
|---|---|---|
| academy.kiloong.com（本站） | 原创导读：体系地图、概念解释、主线项目实操 | 先在这里建立整体理解 |
| [isaac.kiloong.com](https://isaac.kiloong.com) | 官方文档的中文翻译 | 需要查某个 API 或选项的完整说明时，从本站"延伸阅读"跳过去 |

本站的断言以英文官方文档、源码与 release notes 为准；中文翻译站只作延伸阅读，不作来源。

## 从哪里开始

先读 [Isaac 体系一页看懂](0-map/0.1-overview.md)，它是全景地图的入口，也列出了之后该读哪些页。

(build-progress)=
## 建设进度

本站按大纲分批编写。下表是各部分已完成的页数；未完成的页面也能打开，里面写着计划内容与现在可以先读的页面。

<!-- progress:begin -->
| 部分 | P1 已完成 / 总数 | P2 | P3 |
|---|---|---|---|
| 第 0 部分 · 全景地图（招牌章） | 8 / 8 | — | — |
| 第 1 部分 · 环境与版本 | 5 / 5 | 1 / 4 | — |
| 第 2 部分 · 地基：USD 与 Omniverse Kit | 3 / 3 | 4 / 4 | 0 / 1 |
| 第 3 部分 · Isaac Sim 核心 | 6 / 6 | 0 / 3 | 0 / 2 |
| 第 4 部分 · Isaac Lab 核心 | 15 / 15 | 1 / 4 | 0 / 1 |
| 第 5 部分 · RL 入门（只讲够用的） | 6 / 6 | 2 / 2 | — |
| 第 6 部分 · 主线项目：Galbot One Golf 全流程 | 12 / 12 | 1 / 13 | 0 / 3 |
| 第 7 部分 · 工程基础设施专题 | 0 / 2 | 0 / 1 | 0 / 3 |
| 第 8 部分 · 3.0 前沿（基于 EA 版，内容可能变动） | 0 / 3 | 0 / 3 | — |
| 第 9 部分 · 源码导读 | — | 0 / 5 | — |
| 附录 | 0 / 4 | 0 / 1 | — |
| **合计** | **55 / 64** | **9 / 40** | **0 / 10** |

*由 `tools/gen_placeholders.py` 统计，生成于 2026-10-09。P1 是黄金路径与核心概念，最先编写；P2 是第二阶段；P3 是长期补充。未完成的页面在目录里标有"（待写）"。*
<!-- progress:end -->

<!-- toctree:begin -->
```{toctree}
:hidden:
:caption: 第 0 部分 · 全景地图

0-map/0.1-overview
0-map/0.2-layers
0-map/0.3-lineage
0-map/0.4-isaac-names
0-map/0.5-sim-lab-boundary
0-map/0.6-one-step
0-map/0.7-learning-paths
0-map/0.8-glossary
```

```{toctree}
:hidden:
:caption: 第 1 部分 · 环境与版本

1-env/1.1-compat-matrix
1-env/1.2-version-decision
1-env/1.3-hardware
1-env/1.4-install-51-232
1-env/1.5-install-61-30
1-env/1.6-container
1-env/1.7-install-methods
1-env/1.8-dev-tools
1-env/1.9-install-troubleshooting
```

```{toctree}
:hidden:
:caption: 第 2 部分 · 地基：USD 与 Omniverse Kit

2-usd-kit/2.1-why-usd
2-usd-kit/2.2-usd-concepts
2-usd-kit/2.3-layers-composition
2-usd-kit/2.4-physics-schema
2-usd-kit/2.5-usd-python
2-usd-kit/2.6-what-is-kit
2-usd-kit/2.7-extensions
2-usd-kit/2.8-nucleus
```

```{toctree}
:hidden:
:caption: 第 3 部分 · Isaac Sim 核心

3-isaacsim/3.1-sim-loop
3-isaacsim/3.2-simulation-app
3-isaacsim/3.3-rigid-collision
3-isaacsim/3.4-articulation
3-isaacsim/3.5-urdf-mjcf-import
3-isaacsim/3.6-sensors
3-isaacsim/3.7-cloner
3-isaacsim/3.8-rendering
3-isaacsim/3.9-replicator
3-isaacsim/3.10-ros2-bridge
3-isaacsim/3.11-api-map
```

```{toctree}
:hidden:
:caption: 第 4 部分 · Isaac Lab 核心

4-isaaclab/4.1-why-isaac-lab
4-isaaclab/4.2-repo-map
4-isaaclab/4.3-configclass
4-isaaclab/4.4-simulation-context
4-isaaclab/4.5-interactive-scene
4-isaaclab/4.6-assets
4-isaaclab/4.7-actuators
4-isaaclab/4.8-sensors
4-isaaclab/4.9-manager-based-env
4-isaaclab/4.10-observation-action
4-isaaclab/4.11-reward-termination-curriculum
4-isaaclab/4.12-event-randomization
4-isaaclab/4.13-command-manager
4-isaaclab/4.14-direct-env
4-isaaclab/4.15-task-registration
4-isaaclab/4.16-rl-wrappers
4-isaaclab/4.17-multi-agent
4-isaaclab/4.18-extension-template
4-isaaclab/4.19-mimic
4-isaaclab/4.20-teleop-devices
```

```{toctree}
:hidden:
:caption: 第 5 部分 · RL 入门

5-rl/5.1-mdp
5-rl/5.2-policy-value
5-rl/5.3-ppo
5-rl/5.4-parallel-envs
5-rl/5.5-reward-design
5-rl/5.6-observation-design
5-rl/5.7-il-vs-rl
5-rl/5.8-training-debug
```

```{toctree}
:hidden:
:caption: 第 6 部分 · 主线项目：Galbot One Golf 全流程

6-galbot/1-asset/index
6-galbot/2-scene/index
6-galbot/3-sim-align/index
6-galbot/4-task/index
6-galbot/5-train/index
6-galbot/6-eval/index
6-galbot/7-deploy/index
```

```{toctree}
:hidden:
:caption: 第 7 部分 · 工程基础设施专题

7-infra/7.1-headless-remote
7-infra/7.2-profiling
7-infra/7.3-debugging
7-infra/7.4-testing-ci
7-infra/7.5-data-management
7-infra/7.6-team-conventions
```

```{toctree}
:hidden:
:caption: 第 8 部分 · 3.0 前沿

8-frontier/8.1-what-changed
8-frontier/8.2-multi-backend
8-frontier/8.3-newton
8-frontier/8.4-migration-23-30
8-frontier/8.5-galbot-reach-30
8-frontier/8.6-version-tracking
```

```{toctree}
:hidden:
:caption: 第 9 部分 · 源码导读

9-source/9.1-rl-env-step
9-source/9.2-scene-cloning
9-source/9.3-articulation-data
9-source/9.4-train-script
9-source/9.5-franka-lift
```

```{toctree}
:hidden:
:caption: 附录

appendix/A.1-api-cheatsheet
appendix/A.2-error-index
appendix/A.3-official-resources
appendix/A.4-community-projects
appendix/A.5-changelog
```
