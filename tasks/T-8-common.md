# 第 8 部分任务卡的公共要求（设计 session）

适用于 T-8.x 全部任务卡。第 8 部分是"3.0 前沿专栏"（D-001 / D-019）：主线仍是 Isaac Sim 5.1.0 + Isaac Lab 2.3.2，本部分讲 3.0 改了什么、为什么、怎么迁移。内容基于 **Isaac Lab v3.0.0-EA**（tag `v3.0.0-EA`，commit ae37b028e，2026-09-16；要求 Isaac Sim 6.1.0），是 EA 之后尚无 GA 的状态，每页顶部用一个 `warning` 提示框写明"基于 EA，GA 后可能变动，最后核对日期"。

- **来源**：以 `v3.0.0-EA` tag 为准——本地仓库 `~/wuql_ws/isaac_sim/IsaacLab` 已有该 tag（`git show v3.0.0-EA:<路径>` 或 `git worktree add ../IsaacLab-3.0 v3.0.0-EA` 只读检出，**不要切换主检出的 v2.3.2**）。permalink 用 `https://github.com/isaac-sim/IsaacLab/blob/v3.0.0-EA/<路径>#L<行>`。GitHub Releases 页（v3.0.0-beta / beta2 / beta2.patch1 的发布说明，tag 内 `docs/source/refs/release_notes.rst` 为副本）与 `docs/source/migration/migrating_to_isaaclab_3-0.rst`、`docs/source/concepts/*.rst`（physics_backends、backend_architecture、backends_and_presets、native-physics-api/*）是主要文档来源。
- **3.0 实测环境**（2026-10-09 起，T-1.5）：本机已有 `~/wuql_ws/isaac_sim/IsaacLab-3.0`（v3.0.0-EA + Isaac Sim 6.1.0，uv 环境；Kit-less Newton 路线另有验证）。8.x 后续页面（8.2 / 8.3 / 8.5）**可以也应当实测**，口径与第 6 部分相同（显存按进程 + 主机 RSS）；8.1 / 8.4 / 8.6 写作时未运行 3.0，其断言来自源码与文档，T-8.6c 已改口为"未逐条实测"。没有实测的断言仍不写"实测"。
- **版本名**：EA 之前有 v3.0.0-beta（2026-03-16）、beta2（2026-06-16）、beta2.patch1（2026-06-30），EA（2026-09-16）最新。页面里统一叫"3.0 EA"，提到 beta 时写明是更早的预发布。
- **与主线对照**：每页都要有"2.3.2 里是什么 → 3.0 里变成什么"的对照表，2.3.2 一侧引 v2.3.2 permalink。
- **不预测**：GA 时间、后续计划只引 NVIDIA 公开说法并注明出处与日期，没有就不写。
- **篇幅**：上限 3500（D-027 口径）。**图**：D-017 / D-025。**新术语**：每页附记列出（本部分会有不少：backend、Newton、MJWarp、Kamino、Kit-less、SceneDataProvider 等），交付后设计 session 开术语微任务。
