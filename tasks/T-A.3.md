# T-A.3 官方资源导航

状态: 已合并
优先级: P1（附录里最先做：其他附录页与多数正文页的"延伸阅读"都要回链本页）
类型: 参考页
依赖: 无
产出: `docs/appendix/A.3-official-resources.md`（替换占位页）
公共要求: 见 `tasks/T-A-common.md`

## 必须覆盖

1. **按层分组的官方入口表**（与 0.2 分层一致）：Isaac Lab（文档 v2.3.2 与 main、GitHub、Releases、Discussions、论文 Mittal et al. 2023 Orbit arXiv:2301.04195）、Isaac Sim（5.1.0 文档、6.1 文档、论坛板块、Release notes、WebRTC 客户端下载页）、Omniverse Kit / USD（Kit SDK 文档、OpenUSD 官方、usd-core PyPI）、PhysX（文档、GitHub）、Newton（GitHub、文档）、RL 库（rsl_rl、skrl、rl_games、SB3 各自 GitHub 与文档）、Galbot 描述仓库。每行：名字、链接、"什么时候来这里"一句话、本站对应页面。
2. **本站与官方的关系**一段：本站是导读层（CLAUDE.md 定位），中文翻译站 isaac.kiloong.com 的说明（译自最新版，与 5.1.0 可能有差异）。
3. **提问与求助**：官方论坛分区、GitHub issue 模板要点、提问前自查（回链 1.9"如何提问"，不重复）。
4. **怎么看文档版本号**：Isaac Lab 文档的版本切换、Isaac Sim 文档 URL 里的版本段，一段 + 截图可免。
5. 维护规则一段。

## 验收标准

每个链接 2026-10 可访问（抓取被拒的按 CONVENTIONS 第 4 节处理，注明）；分组与 0.2 一致；回链 0.2、1.9、1.1 可达。

## 附记

### 实现（isaac-academy-accomplish，2026-10-09）

**修改**：只写 `docs/appendix/A.3-official-resources.md`。重跑了 gen_placeholders。

**链接核对**：页内 30 个外部链接全部用 `curl -s -L -A Mozilla/5.0` 于 2026-10-09 访问，返回码都是 200。没有抓取被拒的。

**自查**
- [x] 1 官方入口：按 0.2 自上而下分 5 组（Isaac Lab、Isaac Sim、Kit 与 USD、物理引擎含 Newton / Warp、RL 库），另加主线机器人一组。每行四栏：资源、链接、什么时候来这里、本站对应页面。论文按卡片引 arXiv:2301.04195（Orbit）。
  - PhysX 文档链接是 5.6.1 版。Isaac Sim 5.1 内置的 PhysX SDK 具体版本本站没有核对，表中已注明，不作断言。
- [x] 2 本站与官方的关系：导读层的定位取自 CLAUDE.md；说明翻译站译自最新版，可能与 5.1.0 / 2.3.2 不一致。
- [x] 3 提问与求助：一张三行表（论坛 / Issues / Discussions）。bug 模板要点取自 v2.3.2 的 `.github/ISSUE_TEMPLATE/bug.md`（permalink）。自查清单回链 1.9"如何提问"，不重复。
- [x] 4 怎么看文档版本号：Isaac Lab 与 Isaac Sim 文档 URL 里的版本段，一段，无截图。
- [x] 5 维护规则一段（四栏格式、用 curl 确认、失效链接只标注不删除）。
- [x] 按附录公共要求：没有学习目标、前置知识、常见误解三节；保留"怎么用这一页"、延伸阅读、版本说明。没有新术语。
- [x] 链接：0.2、1.1、1.9、8.6 等站内页，-W 构建通过。
- [x] 篇幅（D-027）：含表 1173。
- [x] `check_head_build.sh --worktree` 通过。

### 校验附记（isaac-academy-examine，2026-10-09）

**通过**，见 `reviews/T-A.3.md`。31 个外部链接逐个 curl 核对都是 200（论坛一个第一次超时，重试正常）；bug 模板要点与 v2.3.2 一致；PhysX SDK 版本维持"未核对"。
