---
title: 社区项目与论文代码索引（标注版本）
verified: "各仓库 2026-10-11 的默认分支；GitHub API 的 license 与 pushed_at"
updated: 2026-10-11
sources_checked: 2026-10-11
---

# 社区项目与论文代码索引（标注版本）

**怎么用这一页**：想找"别人用 Isaac Lab 做过什么"时，先在这里按方向查，再看"声明的版本"一列，判断它和你的环境差多远。官方仓库与文档入口见 [A.3](A.3-official-resources.md)，本页不重复。本页只记录项目自己声明的版本，不评价好坏，也不排名。

**收录标准**：开源且有许可；README 或依赖文件里能查到 Isaac Sim / Isaac Lab 的版本；2025 年以来有推送。无许可的不收；有许可但查不到版本的，只在文末列名，不列链接。

**各列含义**：

- "声明的版本"一律照抄对方的写法；
- "依据"指出在对方仓库的哪个文件、第几行，badge 指 README 顶部的版本徽章；
- "最近推送"取 GitHub API 的 `pushed_at`，含非默认分支的推送；
- "许可"以仓库的 LICENSE 文件为准。

所有条目最后核对于 2026-10-11，当天链接可访问。

## 腿式与人形运动

| 项目 | 声明的版本 | 依据 | 最近推送 | 许可 | 看什么 | 本站相关页 |
|---|---|---|---|---|---|---|
| [robot_lab](https://github.com/fan-ziqi/robot_lab) | Isaac Sim 5.1.0 / Isaac Lab 2.3.2 | README L3–L4 badge | 2026-10 | Apache-2.0 | 机器人的 RL 扩展库，基于 Isaac Lab | — |
| [unitree_rl_lab](https://github.com/unitreerobotics/unitree_rl_lab) | Isaac Sim 5.1.0 / Isaac Lab 2.3.0 | README L3–L4 badge | 2026-05 | Apache-2.0 | 宇树机器人的 RL 训练与部署 | — |
| [Isaac-RL-Two-wheel-Legged-Bot](https://github.com/jaykorea/Isaac-RL-Two-wheel-Legged-Bot) | Isaac Sim 4.5 / Isaac Lab 2.0.0 | README L3–L4 badge | 2026-03 | MIT | 轮腿机器人的 RL 训练 | — |
| [holosoma](https://github.com/amazon-far/holosoma) | Isaac Sim 5.1.0 / Isaac Lab 2.3.2 | `docker/isaacsim.Dockerfile` L2 | 2026-10 | Apache-2.0 | 人形训练与部署框架，多仿真器（含 Isaac Sim） | — |
| [GR00T-WholeBodyControl](https://github.com/NVlabs/GR00T-WholeBodyControl) | Isaac Lab 2.3.2 | README L13 badge | 2026-09 | 代码 Apache-2.0；模型权重另有许可 | 人形全身控制器的开发与部署平台 | — |
| [ProtoMotions](https://github.com/NVlabs/ProtoMotions) | Isaac Lab 3.0 | README L11 badge | 2026-09 | Apache-2.0 | 仿真数字人与人形机器人的训练框架 | [8.4](../8-frontier/8.4-migration-23-30.md) |
| [HumanoidVerse](https://github.com/LeCAR-Lab/HumanoidVerse) | Isaac Sim 4.2.0 | README L13 badge | 2025-06 | MIT | 仿真器、任务、算法分离的多仿真器人形框架 | — |

*表 1：腿式与人形运动。*

## 操作与抓取

| 项目 | 声明的版本 | 依据 | 最近推送 | 许可 | 看什么 | 本站相关页 |
|---|---|---|---|---|---|---|
| [isaacLab.manipulation](https://github.com/NathanWu7/isaacLab.manipulation) | Isaac Sim 4.5.0 / Isaac Lab 2.0.2 | README L3–L4 badge | 2025-06 | MIT | 独立于 Isaac Lab 仓库的操作任务模板 | [4.18](../4-isaaclab/4.18-extension-template.md) |
| [MetaIsaacGrasp](https://github.com/YitianShi/MetaIsaacGrasp) | Isaac Lab 2.0 / Isaac Sim 4.5.0 | README L1、L13 | 2025-06 | MIT | 抓取学习的数据生成与测试台 | — |
| [trash-collection-isaaclab](https://github.com/iit-DLSLab/trash-collection-isaaclab) | Isaac Lab v2.3.2（badge 的替代文字写 v2.3.0） | README L2 badge | 2026-08 | BSD-3-Clause | 四足机器人的移动操作：依次训练行走与末端到位两个策略 | — |

*表 2：操作与抓取。*

## 移动与导航

| 项目 | 声明的版本 | 依据 | 最近推送 | 许可 | 看什么 | 本站相关页 |
|---|---|---|---|---|---|---|
| [go2_omniverse](https://github.com/abizovnuralem/go2_omniverse) | 两条路线：Isaac Sim 2023.1.1 + Orbit 0.3.0；Isaac Sim 5.0 + IsaacLab 0.54.3（pip 包版本号） | README L168、L172 | 2026-07 | BSD-2-Clause | Go2 / G1 在 Isaac Lab 中接 ROS 2 | [6.7.2](../6-galbot/7-deploy/6.7.2-ros2-closed-loop.md) |

*表 3：移动与导航（导航方向的论文代码见表 7）。*

## 遥操作与数据采集

| 项目 | 声明的版本 | 依据 | 最近推送 | 许可 | 看什么 | 本站相关页 |
|---|---|---|---|---|---|---|
| [leisaac](https://github.com/LightwheelAI/leisaac) | Isaac Sim 5.1.0 / `isaaclab==2.3.0` | `source/leisaac/pyproject.toml` L19、L41 | 2026-04 | Apache-2.0 | 用 LeRobot 的 SO101 主臂在 Isaac Lab 里遥操作、采数据 | [4.20](../4-isaaclab/4.20-teleop-devices.md) |
| [unitree_sim_isaaclab](https://github.com/unitreerobotics/unitree_sim_isaaclab) | Isaac Sim 4.5.0 / 5.x.0；RTX 50 系列用 5.0.0 | README L15、L127 | 2026-03 | Apache-2.0 | 宇树机器人仿真环境，收发与真机相同的 DDS 话题 | — |
| [locomanipulation-teleop-isaaclab](https://github.com/iit-DLSLab/locomanipulation-teleop-isaaclab) | Isaac Lab v3.0.0（badge 的替代文字写 v3.3.0） | README L2 badge | 2026-10 | BSD-3-Clause | Go2 加 AgileX Piper 机械臂的遥操作，Direct 环境 | [4.14](../4-isaaclab/4.14-direct-env.md) |

*表 4：遥操作与数据采集。*

## sim2real 与部署

| 项目 | 声明的版本 | 依据 | 最近推送 | 许可 | 看什么 | 本站相关页 |
|---|---|---|---|---|---|---|
| [kinova_isaaclab_sim2real](https://github.com/louislelay/kinova_isaaclab_sim2real) | Isaac Sim 4.5.0 | `source/gen3/setup.py` L41 | 2025-07 | MIT | Kinova Gen3 在 Isaac Lab 训练、经 ROS 2 部署；部署端不需要 Isaac | [6.7.3](../6-galbot/7-deploy/6.7.3-sim2real-checklist.md) |

*表 5：sim2real 与部署（表 1 的 unitree_rl_lab、holosoma 也含部署）。*

## 工具与扩展

下面三个库的版本由 Isaac Lab 一侧固定，所以依据写的是 Isaac Lab v2.3.2 的依赖文件。

| 项目 | Isaac Lab 2.3.2 要求的版本 | 依据 | 最近推送 | 许可 | 看什么 | 本站相关页 |
|---|---|---|---|---|---|---|
| [rsl_rl](https://github.com/leggedrobotics/rsl_rl) | `rsl-rl-lib==3.1.2`（上游 main 已是 5.5.1） | Isaac Lab `isaaclab_rl/setup.py` L49[^rl] | 2026-10 | BSD-3-Clause | PPO 等算法，本站主线用它训练 | [6.5.1](../6-galbot/5-train/6.5.1-train-reach-rsl-rl.md)、[4.16](../4-isaaclab/4.16-rl-wrappers.md) |
| [skrl](https://github.com/Toni-SM/skrl) | `skrl>=1.4.3` | 同上 L44[^rl] | 2026-10 | MIT | 支持 PyTorch / JAX 的模块化 RL 库 | [4.16](../4-isaaclab/4.16-rl-wrappers.md) |
| [robomimic](https://github.com/ARISE-Initiative/robomimic) | v0.4.0 | Isaac Lab `isaaclab_mimic/setup.py` L32[^mimic] | 2026-08 | MIT | 从示范学习的框架，本站 BC 训练用它 | [6.4.7](../6-galbot/4-task/6.4.7-mimic.md) |

*表 6：工具与扩展。*

## 论文配套代码

| 项目 | 声明的版本 | 依据 | 最近推送 | 许可 | 看什么 | 本站相关页 |
|---|---|---|---|---|---|---|
| [whole_body_tracking](https://github.com/HybridRobotics/whole_body_tracking) | Isaac Sim 4.5.0 / Isaac Lab 2.1.0 | README L3–L4 badge、L32 | 2026-07 | MIT | BeyondMimic 的动作跟踪训练代码 | — |
| [ASAP](https://github.com/LeCAR-Lab/ASAP) | Isaac Sim 4.2.0（另支持 IsaacGym、Genesis） | README L20 badge | 2026-01 | MIT | 对齐仿真与真机物理的人形全身技能（RSS 2025） | — |
| [HOVER](https://github.com/NVlabs/HOVER) | Isaac Sim 4.5.0 / Isaac Lab 2.0.0 | README L3–L4 badge、L52 | 2025-07 | Apache-2.0 | 人形机器人的通用全身控制器 | — |
| [IsaacLabEureka](https://github.com/NVlabs/IsaacLabEureka) | Isaac Sim 5.1.0 / Isaac Lab 2.3.0 | README L3–L4 badge | 2025-10 | Apache-2.0 | 用大模型自动设计奖励函数（Eureka）的 Isaac Lab 实现；仓库已从 isaac-sim 组织移到 NVlabs | [5.5](../5-rl/5.5-reward-design.md) |
| [viplanner](https://github.com/leggedrobotics/viplanner) | Isaac Sim 4.2.0 + Isaac Lab 1.2.0（指定 commit） | `omniverse/README.md` L32 | 2025-11 | BSD-3-Clause | 视觉语义局部导航规划器 | — |
| [NavRL](https://github.com/Zhefan-Xu/NavRL) | Isaac Sim 2023.1.0-hotfix.1 | README L69 | 2025-07 | MIT | 无人机在动态环境中的安全导航（RA-L 2025） | — |

*表 7：论文配套代码。*

## 版本不明

以下项目有许可，但本站核对时在 README 里没有找到 Isaac Sim / Isaac Lab 的版本声明（依赖文件未逐个查），只列名：rl_sar（fan-ziqi）、xr_teleoperate（unitreerobotics，仿真模式依赖 unitree_sim_isaaclab）、isaaclab_ur_reach_sim2real（louislelay）、RoboVerse（RoboVerseOrg）、rl_games 上游（Denys88；Isaac Lab 2.3.2 用的是 isaac-sim 组织下的分支[^rl]）。

## 怎么判断一个项目还能不能跑

1. **先看声明的版本，对照兼容关系。** 和你的版本差一个大版本，就要做迁移，而不是"装上试试"。版本对应见 [1.1](../1-env/1.1-compat-matrix.md)。
2. **看 import 判断年代。** `omni.isaac.lab` 是 1.x 的写法，2.0 起改成 `isaaclab`，在 2.x 上直接报 `ModuleNotFoundError`（[0.3"看 import 判年代"](../0-map/0.3-lineage.md#看-import-判年代)）。2.x 到 3.0 的改动逐项见 [8.1](../8-frontier/8.1-what-changed.md) 与 [8.4 迁移清单](../8-frontier/8.4-migration-23-30.md)。
3. **看 issue 和 README 里的兼容说明。** 有的项目会把跨版本遇到的问题写出来，那就是最直接的迁移清单。

两个真实例子：

- 表 7 的视觉导航规划器写明用 Isaac Sim 4.2.0 + Isaac Lab 1.2.0 测试，还给了 commit。它的扩展代码按 1.x 写，要在主线 5.1 + 2.3.2 上跑，先过第 2 步的改名。只看"Isaac Lab"四个字，会以为装上就能用。
- 表 3 的 Go2 项目在 README 里列了升到 Isaac Sim 5.x 时做的修改：ROS 2 桥的库换了位置，关节数据从 Warp 数组转 NumPy 后才能索引。版本升级时，这类"启动就失败"的问题往往不在 Isaac Lab 的迁移清单里，而在 Isaac Sim 扩展的变动里。

另外，版本声明本身也可能不一致：表 2、表 4 中有两个仓库，徽章图片上的版本和替代文字写的不同。以依赖文件或安装说明为准，查不到就当"版本不明"。

## 维护规则

与 A.3 同口径。新增一行要填全七栏：

- "依据"写到文件与行号；
- "最近推送"用 GitHub API 的 `pushed_at`；
- "许可"以 LICENSE 文件为准，API 返回 `NOASSERTION` 时去读 LICENSE 原文。

新增或改动后，用 `curl -L` 确认链接能访问，并把页首的核对日期改为当天。一个项目 12 个月没有推送，或声明的版本落后主线两个大版本，就移到"版本不明"下方的"不再维护"小节（目前没有），不直接删除。条目由发现的会话报给设计会话，开微任务添加。

## 延伸阅读

- 官方仓库与文档入口：[A.3](A.3-official-resources.md)
- Isaac 各代框架与改名历史：[0.3](../0-map/0.3-lineage.md)

## 版本说明

本页按主线 Isaac Sim 5.1.0 + Isaac Lab 2.3.2 判断"差多远"；各项目声明的版本照抄对方仓库。表中声明 Isaac Lab 3.0 的项目（ProtoMotions、locomanipulation-teleop-isaaclab）在 3.0 上的情况由对方声明，本站未核对。

3.0 的差异以 [8.6 版本追踪](../8-frontier/8.6-version-tracking.md) 为准，本页最后核对的版本见该页核对状态表。

[^rl]: Isaac Lab `source/isaaclab_rl/setup.py`（tag v2.3.2）L43–L53：`skrl>=1.4.3`（L44）、rl-games 用 `isaac-sim/rl_games` 的 `python3.11` 分支（L46）、`rsl-rl-lib==3.1.2`（L49） <https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_rl/setup.py#L43-L53>
[^mimic]: Isaac Lab `source/isaaclab_mimic/setup.py`（tag v2.3.2）L32：`robomimic@git+…@v0.4.0` <https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_mimic/setup.py#L32>
