# T-A.4 校验报告：社区项目与论文代码索引（标注版本）

校验 session：isaac-academy-examine，2026-10-11
结论：第 1 轮**退回**（2 条低），第 2 轮**通过**。
- 卡片要求抽查 ≥ 10 条，本 session 核了**全部 24 条**：版本依据所引的行（当天重新下载对方默认分支的原文件）、许可、`pushed_at`、链接可达。
- 只有两条的"声明的版本"没有照抄原文，与页首"一律照抄对方的写法"不符，退回改这两处即可。

## 核对方法

- 原文：`raw.githubusercontent.com/<仓库>/<默认分支>/<文件>`，按页面"依据"列的行号取行（`scratch/examine/tA4/check.txt`）。
- 许可：读 LICENSE 原文；GitHub API 的 `license.spdx_id` 另取一次（`pushed.txt`）。
- 最近推送：GitHub API 的 `pushed_at`。
- 链接：`curl -L https://github.com/<仓库>` 全部返回 200。
- 本 session 的未登录 API 限额一度被 3.6 / 6.1.7 的上游查询用完，限额恢复后补核，所以报告比其他项晚。

## 逐条结果

| 组 | 项目 | 所引行（原文摘要） | 许可 | 推送 | 结果 |
|---|---|---|---|---|---|
| 1 | robot_lab | L3 IsaacSim-5.1.0、L4 IsaacLab-2.3.2 | Apache-2.0 | 2026-10 | 一致 |
| 1 | unitree_rl_lab | L3 5.1.0、L4 2.3.0 | Apache-2.0（文件名 LICENCE） | 2026-05 | 一致 |
| 1 | Isaac-RL-Two-wheel-Legged-Bot | L3 IsaacSim-4.5、L4 Lab-2.0.0 | MIT | 2026-03 | 一致 |
| 1 | holosoma | Dockerfile L2 "IsaacSim 5.1.0 / IsaacLab 2.3.2 image" | Apache-2.0 | 2026-10 | 一致 |
| 1 | GR00T-WholeBodyControl | L13 IsaacLab-2.3.2 | API 为 NOASSERTION；LICENSE 是"DUAL LICENSE NOTICE"，代码 Apache 2.0 | 2026-09 | 一致 |
| 1 | ProtoMotions | L11 IsaacLab-3.0 | Apache-2.0 | 2026-09 | 一致 |
| 1 | HumanoidVerse | L13 IsaacSim-4.2.0 | MIT | 2025-06 | 一致 |
| 2 | isaacLab.manipulation | L3 4.5.0、L4 2.0.2 | MIT | 2025-06 | 一致 |
| 2 | MetaIsaacGrasp | L1、L13 "IsaacLab 2.0 and IsaacSim 4.5(.0)" | MIT | 2025-06 | 一致 |
| 2 | trash-collection-isaaclab | L2 图片 `v2.3.2`，`alt="IsaacLab v2.3.0"` | BSD-3-Clause | 2026-08 | 一致，页面已注明两者不同 |
| 3 | go2_omniverse | L168 Track A（2023.1.1、Orbit 0.3.0），L172 Track B（Isaac Sim 5.0、IsaacLab 0.54.3） | BSD-2-Clause | 2026-07 | 一致 |
| 4 | leisaac | pyproject L19 "Isaac Sim :: 5.1.0"，L41 `isaaclab[…]==2.3.0` | Apache-2.0 | 2026-04 | 一致 |
| 4 | unitree_sim_isaaclab | L15 "For the RTX 50 series GPUs, please use Isaac Sim version 5.0.0"，L127 "requires Isaac Sim 4.5.0/Isaac Sim 5.x.0" | API 为 NOASSERTION；原文是 Apache License 2.0 | 2026-03 | 见问题 2 |
| 4 | locomanipulation-teleop-isaaclab | L2 图片 `v3.0.0`，`alt="IsaacLab v3.3.0"` | BSD-3-Clause | 2026-10 | 一致，页面已注明 |
| 5 | kinova_isaaclab_sim2real | setup.py L41 "Isaac Sim :: 4.5.0" | MIT | 2025-07 | 一致 |
| 6 | rsl_rl | Isaac Lab v2.3.2 `isaaclab_rl/setup.py` L49 `rsl-rl-lib==3.1.2`；上游 `pyproject.toml` L7 `version = "5.5.1"` | API 为 NOASSERTION；原文是 BSD 条款（"Redistribution and use in source…"） | 2026-10 | 一致 |
| 6 | skrl | 同上 L44 `skrl>=1.4.3` | MIT | 2026-10 | 一致 |
| 6 | robomimic | `isaaclab_mimic/setup.py` L32 `@v0.4.0` | MIT | 2026-08 | 一致 |
| 7 | whole_body_tracking | L3 4.5.0、L4 2.1.0、L32 "Install Isaac Lab v2.1.0" | MIT | 2026-07 | 一致 |
| 7 | ASAP | L20 IsaacGym Preview4、IsaacSim-4.2.0 等 | MIT | 2026-01 | 一致 |
| 7 | HOVER | L3 4.5.0、L4 2.0.0、L52 "tested with Isaac Lab versions 2.0.0" | Apache-2.0 | 2025-07 | 一致 |
| 7 | IsaacLabEureka | L3 5.1.0、L4 2.3.0 | Apache-2.0 | 2025-10 | 一致 |
| 7 | viplanner | `omniverse/README.md` L32 "tested with IsaacSim 4.2.0 and IsaacLab 1.2.0 (commit: 0bccd88…)" | API 为 NOASSERTION；原文是 BSD 3-Clause | 2025-11 | 一致 |
| 7 | NavRL | L69 "Isaac Sim version 2023.1.0-hotfix.1" | MIT | 2025-07 | 见问题 1 |

- 推送一列 24 条全部一致，都在 2025 年以后，满足收录标准。
- 几个仓库默认分支的最后提交早于 `pushed_at`（如 robot_lab 默认分支 2026-05、`pushed_at` 2026-10），页面"含非默认分支的推送"的说明已经覆盖。

**排除项**：
- isaac-go2-ros2：API 的 license 为 None，`LICENSE*` 都返回 404，无许可，排除正确。
- spot-rl-example：`pushed_at` 2024-06-05，排除正确。

**版本不明 5 个**：rl_sar、xr_teleoperate、isaaclab_ur_reach_sim2real、RoboVerse、rl_games 上游。默认分支 README 里 grep 不到 Isaac Sim / Isaac Lab 的版本号（rl_sar 只有 "legged_gym (IsaacGym)"；ur_reach 只写"tested with ROS2 Humble"）。只列名、不列链接，与收录标准一致。

**脚注**：
- v2.3.2 `isaaclab_rl/setup.py` L43–L53：L44 skrl、L46 `isaac-sim/rl_games@python3.11`、L49 `rsl-rl-lib==3.1.2`；
- `isaaclab_mimic/setup.py` L32 robomimic `@v0.4.0`。
- 成立。

**"怎么判断"的两个例子**：
- go2_omniverse README L62–L66"Isaac Sim 5.x boot fixes"：ROS 2 桥的库从 `isaacsim.ros2.bridge` 移到 `isaacsim.ros2.core`；关节缓冲从 warp 数组转 NumPy 后再索引。与页面一致。
- viplanner：L32 写测试版本是 1.2.0，L39 链接到 `IsaacLab/source/extensions`，这是 1.x 的目录结构。"按 1.x 写"成立。
- 两例都没有点名批评。

**措辞**：没有排名与评价性词语；"本站相关页"一列只写本站哪一页用到它。iit 两个仓库的徽章不一致：表中照抄图片，括号注明替代文字，并在"怎么判断"末段说明"以依赖文件或安装说明为准"，写清楚了。

## 站点检查

**快照**：工作区的 docs 与 examples 已提交到草稿目录里的克隆，然后构建。快照里同时有 1.6 与 T-0.8m。

- **审计**：
  - anchors：站内链接 6672，0 问题（A.3、0.3#看-import-判年代、1.1、8.1、8.4 等都能解析）；
  - placeholders：0 问题；
  - version：一般级 0。
  - 8.6 计数按设计说明：1.6 已按 103 / 100 / 55 先合，A.4 合并时以工作树的 104 / 101 / 56 为准，不在本报告提项。
- **严格构建**：`check_head_build.sh --worktree`（-W）通过（`strict_build33.log`）。

## 问题与建议

| # | 位置 | 问题 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|---|
| 1 | 表 7 NavRL | 声明的版本写"Isaac Sim 2023.1.0"，原文是 "Isaac Sim version **2023.1.0-hotfix.1**"，还强调"use this exact version"。页首说"一律照抄对方的写法" | NavRL README L69 | 改为"Isaac Sim 2023.1.0-hotfix.1" | 低 |
| 2 | 表 4 unitree_sim_isaaclab | 写"Isaac Sim 4.5.0；RTX 50 系列用 5.0.0"。L127 原文是 "requires Isaac Sim 4.5.0/Isaac Sim 5.x.0"，页面漏了"5.x.0" | unitree_sim_isaaclab README L15、L127 | 改为"Isaac Sim 4.5.0 / 5.x.0；RTX 50 系列用 5.0.0" | 低 |

## 第 2 轮（复核）

| # | 处理 | 核对 |
|---|---|---|
| 1 | 表 7 NavRL 改为"Isaac Sim 2023.1.0-hotfix.1" | 与 README L69 原文一致 |
| 2 | 表 4 unitree_sim_isaaclab 改为"Isaac Sim 4.5.0 / 5.x.0；RTX 50 系列用 5.0.0" | 与 README L15、L127 一致 |

改动只有这两格（`diff`）。为了不干扰实现方 7.4 的计时，本 session 等它的 GPU 用完（21:14:49）才跑构建：anchors 审计 6673 条链接，0 问题；`check_head_build.sh --worktree`（-W）通过（`strict_build34.log`）。

结论：第 2 轮**通过**。
