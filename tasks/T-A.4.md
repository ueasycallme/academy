# T-A.4 社区项目与论文代码索引（标注版本）

状态: 已合并
优先级: P2（第三批第八张，不占 GPU；需要联网查证）
类型: 参考页
依赖: T-A.3（官方资源导航，本页不重复官方入口）、T-0.3（谱系）
产出: `docs/appendix/A.4-community-projects.md`（替换占位页）
公共要求: 见 `tasks/T-A-common.md`；篇幅上限按表格口径（D-016）

## 目标

读者想找"别人用 Isaac Lab 做过的事"时，有一张标明版本、活跃度与许可的表，而不是一堆不知道还能不能跑的链接。本页的价值在"标注版本"：每个项目写它声明支持的 Isaac Sim / Isaac Lab 版本与依据。

## 必须覆盖

1. **收录标准**（写在页首）：开源、有许可、README 或依赖文件里能查到 Isaac Sim / Lab 版本、2025 年以来有提交；不收无许可或无法确定版本的项目（可在"版本不明"小节列名不列链接）。
2. **分组与条目**：腿式 / 人形运动、操作与抓取、移动与导航、遥操作与数据采集、sim2real 与部署、工具与扩展（转换器、封装、可视化）、论文配套代码。每行：名称、链接、声明的 Isaac Lab / Sim 版本、版本依据（README 哪一句 / pyproject 哪一行，写法"README §Installation"即可）、最近活动月份、许可、一句"看什么"、本站相关页。总数 20–40 条。
3. **怎么判断一个项目还能不能跑**：一节方法——看版本声明、看 Isaac Lab 的 API 变化（回链 8.1 / 8.4 的迁移清单）、看 issue 里的报错；给两个真实例子（不点名批评）。
4. **维护规则**：与 A.3 同口径；注明"最后核对日期"，每条链接当天可达。
5. 不写评价性排名；"推荐"只能以"本站哪一页用到了它"的形式出现。

## 验收标准

校验方抽查 ≥ 10 条：链接可达、版本依据能在对方仓库里找到、许可正确；无未标来源的版本声明；A.3、0.3、8.1、8.4 链接可达。

## 附记

（实现/校验 session 写）

- 2026-10-11 实现（accomplish）：页面 `docs/appendix/A.4-community-projects.md`（count.py：含表 1839）；24 条，分 7 组（腿式 / 人形 7、操作 3、导航 1、遥操作 3、sim2real 1、工具 3、论文 6），另"版本不明"列名 5 个；8.6 表 2 102/99 → 103/100，"其余 55 页"；gen_placeholders 刷新 index.md（占位页 11）；check_head_build --worktree 通过。
- 数据来源：GitHub API（license、pushed_at、description；未登录，scratch/accomplish/tA4/*.json）与 raw 文件（README、pyproject / setup.py / Dockerfile；tA4/readme_*.md）。"依据"列的行号来自对原始文件的 grep -n。LICENSE 为 NOASSERTION 的（rsl_rl、GR00T-WBC、viplanner、unitree_sim_isaaclab）读了 LICENSE 原文：BSD-3、代码 Apache-2.0 + 权重另有许可、BSD-3、Apache-2.0。全部 25 个 GitHub 链接当天 curl -L 返回 200。
- 排除：无许可的 isaac-go2-ros2；2024-06 后无推送的 spot-rl-example；官方组织 isaac-sim 下的 IsaacLab-Arena（属 A.3）。IsaacLabEureka 已从 isaac-sim 移到 NVlabs，按 NVlabs 研究代码收录。
- 版本声明不一致：两个 iit-DLSLab 仓库 badge 图片与 alt 文字不同（v2.3.2 / v2.3.0，v3.0.0 / v3.3.0），表中照抄图片并注明。
- 新术语：无。

**校验第 1 轮（2026-10-11）：退回**，只有 2 条低，报告 `reviews/T-A.4.md`。
- 24 条全部核对（不是抽查）：所引原文行、许可（LICENSE 原文与 API）、`pushed_at`、链接 200。
- 一致的部分：版本不明 5 个、排除项 2 个、脚注、两个例子，iit 两个仓库的处理也写清了。
- 低 2 条：
  1. NavRL 应照抄为 "2023.1.0-hotfix.1"；
  2. unitree_sim_isaaclab 漏了 L127 的 "5.x.0"。
- 2026-10-11 第 1 轮退回后修改（accomplish）：① NavRL 版本照抄为 "Isaac Sim 2023.1.0-hotfix.1"；② unitree_sim_isaaclab 改为"Isaac Sim 4.5.0 / 5.x.0；RTX 50 系列用 5.0.0"。两处都对照了原 README 行。

**校验第 2 轮（2026-10-11）：通过**。2 处已照原文改好；-W 通过（`strict_build34.log`）。
