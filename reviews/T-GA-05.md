# T-GA-05 校验报告：8.6 改写与全站 3.0 内容收口

校验 session：isaac-academy-examine，2026-10-24
结论：**通过**（第 2 轮；第 1 轮的 2 条一般、1 条低都已修，见文末）

- 8.6 改写、全站 3.0 断言、保留清单都核过，抽查 10 处全部成立。
- 全站巡检跑出两处新问题：
  - 8.1 图 2 字号低于 12 px。这是 T-GA-02 带进来的，我校验那张卡时没跑字号检查，漏了。
  - 1.1 的一个 EA 文档链接已经 404。

## 全站巡检

在草稿克隆里，把工作区的 `docs/`、`examples/`、`reviews/scripts/`、`tools/` 打成快照 `a6130dd`，跑 `MOBILE=1 audit-all.sh` 全套。镜像用 `env30/IsaacLab-3.0`（已含 v3.0.0、v3.0.0-EA、v2.3.2 三个 tag）与 `third_party/galbot_one_golf_description`。rc 0，明细在 `scratch/examine/audit_ga05/`。

| # | 检查 | AUDIT-03（36dc8f8） | 现在（a6130dd） | 结论 |
|---|---|---|---|---|
| 1 | 外链 | URL 1083，"失效" 1（S3 前缀，误报），403 1 | URL 1100；"失效 / 异常" 4，403 1（同一个 usdrt 页） | 新增 3 条：1.1 一条 404，见问题 2；packages.ubuntu.com 两条 500，见建议 1 |
| 2 | 站内锚点 | 7283 / 0 | 7440 / 0 | 无问题 |
| 3 | 术语首次附英文 | 首次详细讲解页 2（豁免） | 3 | 新增 8.1 L13"物理后端"，见问题 3 |
| 4 | 图字号 | Mermaid < 12 px 0 | 1 | 8.1 图 2，见问题 1 |
| 5 | 版本说明 | 问题 2 | 问题 1（A.5 缺固定句，原有的建议，按卡不加） | 无新问题 |
| 6 | 占位页 | 0 | 0 | — |
| 7 | examples 头注 | 0 | 0 | — |
| 8 | 术语表指向 | 一般 0 | 一般 0；建议 5 条、英文写法不一 10 组，都是旧有的 | — |
| 9 | 示例互指 | 0 | 0 | — |
| 10 | 导航 | 一般 0 | 一般 0；人工看 1（误报，见下） | — |
| 11 | 图表编号 | 0 | 0 | — |
| 12 | 内部叫法（T-SITE-17 新增） | — | 快照时的版本：一般 59、建议 12；8.6 已无命中 | 其余归 T-SITE-17 |
| 13 | 390 px | 撑破 1（0.6 脚注回链，按裁断不改） | 撑破 1（同一处） | — |

## 8.6 与保留清单

- **8.6 表 1 的 v3.0.0 一行**：日期 2026-10-19、Isaac Sim 6.2、Python 3.12，与 T-GA-01 已核的发布页和安装页一致。
- **表 2"文档与代码不一致"三条**：
  1. `--headless` / `--enable_cameras`：T-GA-01 F2 我复现过 rc=2；`isaaclab/app/` 里 grep 不到这两个参数。
  2. `visualization.rst` L146：T-GA-02 已核。
  3. `--rl_library` 必填：T-GA-04 校验时，我不写这个参数也跑通了。
  - 三条都写的是"v3.0.0 仍不一致"，不是"已修"。
- **维护流程**：改成了读者视角的三步，`audit-internal` 在 8.6 上 0 命中，没有会话名、微任务、卡号。
- **保留清单**：我用同样的 grep（不含 A.5）得到的行号，与附记逐行一致（0.3、0.8、1.1、1.5、3.11、6.4.6、8.1、8.3、8.4、8.5、8.6、8.7、8.8、8.10）。抽读了 3.11 L141、8.3 L60 / L71、8.5 L62、8.7 L168、8.8 L13，都是版本史或"EA 时如何、正式版如何"的对照句。

## 抽查 10 处 3.0 断言（v3.0.0 tag）

| 页 | 断言 | 核对 |
|---|---|---|
| 6.4.6 | #8018、#8318 已在 v3.0.0 | `git log v3.0.0` 里有 c06f83c44（#8018）、ed73bb961（#8318）；`merge-base --is-ancestor` 成立 |
| 3.6 | #6439、#7416 在 v3.0.0，imu.py L186 | 两个提交都在；`isaaclab_physx/sensors/imu/imu.py` L186 是 `accelerations = self._view.get_accelerations()` |
| 4.20 | `--teleop_device` 默认为 None | `teleop_se3_agent.py` L41–L43 `default=None` |
| 6.4.7 | robomimic 的 train / play 没有 `external_callback` | 两个文件 grep 都是 0 |
| 9.5 | Isaac-Lift-Franka 在 L17 | `core/lift/config/franka/__init__.py` L17 `id="Isaac-Lift-Franka"` |
| 1.8 | `--editor` 在 v3.0.0 的 help 里 | 我在 GA 环境跑 `isaaclab --help`，第 57 行有 `--editor ...` |
| 0.3 / 3.11 | 6.2 里 `import omni.isaac.core` 报错，`isaacsim.core.api` 能用 | 实现方的 `tga05/imp.log` L345 报 `ModuleNotFoundError`、`isaacsim.core.api OK`，环境路径是 `IsaacLab-3.0-GA/.venv`；我的 GA 环境里 `isaacsim/*/omni.isaac.*` 目录也是 0 个 |
| 0.2 | Kit 110.4.0 | Isaac Sim 6.2.0 Release Notes"Updated Isaac Sim to Kit SDK 110.4.0"（T-GA-01 已取回） |
| 8.6 表 2 | `--headless` 仍不一致 | 见上 |
| 0.8 | Kamino"v3.0.0 中标为实验性" | v3.0.0 的 `newton.rst` 与 8.2 表 2 一致（T-GA-02 已核） |

## 问题

| # | 位置 | 问题 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|---|
| 1 | 8.1 图 2（发布时间线，`flowchart LR`） | 1440 宽下缩放 0.673，文字 10.8 px，低于 D-025 的 12 px；2560 宽下 12.6 px，刚好达标。原因是 T-GA-02 在横向流程图末尾加了第 5 个节点"v3.0.0 正式版"，图变宽而被压缩。AUDIT-03 时这张图在两档都 ≥ 12 px | `audit-fonts`：`8.1 图2 min 10.8px scale 0.673`（1440）、`12.6px scale 0.79`（2560） | 改为两行排列（例如 beta 三个节点一行、EA 与正式版一行，或用 `flowchart TB`），或者缩短节点文字（去掉 beta 各节点的第三行说明）。改后两档都要 ≥ 12 px | 一般 |
| 2 | 1.1 脚注 `[^lab30-install]`（L135，EA 一行的来源） | 链接 `isaac-sim.github.io/IsaacLab/release/3.0.0/source/setup/installation/index.html` 已经 404：正式版文档重排，安装页搬到了 `isaaclab/installation`。这一行是按历史保留的，但链接不能是死的 | `audit-links`：FAIL 404 | 改为 tag 的 permalink：`blob/v3.0.0-EA/docs/source/setup/installation/index.rst`。脚注里"推荐 580.95.05 / 581.42.00""2.12.0（cu130）"等内容如果来自当时的 release/3.0.0 分支文档、不在 EA tag 里，就写明"该版文档已下线，2026-09-30 查阅"，不要指向 tag | 一般 |
| 3 | 8.1 L13（页首"基于 v3.0.0 正式版"提示框）"默认物理后端一条实测过" | 本页是"物理后端"的首次详细讲解页，按术语首次出现附英文（D-018 / D-029）的口径，第一次出现不在学习目标框或标题里，就要附英文；英文到 L64 才出现"物理后端（backend）"。EA 版的这一句没有这个词，是 T-GA-02 改写时带进来的 | `audit-terms`：`FIRST 8.1:13 物理后端 应附（Backend） 首次详细讲解页` | L13 改为"默认物理后端（backend）一条实测过"，或者换个说法，不在这里用这个词 | 低 |

**更正（已撤回）**：第 1 版报告说"OUTLINE 里 1.5 的标题仍是 6.1 + 3.0-EA"，这是误报。我的快照只同步了 `docs/`、`examples/`、`reviews/scripts/`、`tools/`，`OUTLINE.md` 还是旧的；项目里的 OUTLINE L43 在 8ece82b 已改为"安装 Isaac Sim 6.2 + Isaac Lab 3.0"。以后做快照时把根目录的 `OUTLINE.md` 一起同步。OUTLINE 页首的版本说明由设计方在合并本卡时改，不在实现方范围。

**建议 1（不作问题）**：1.4 L318、1.9 L256 引用的 `packages.ubuntu.com/jammy/python3` 与 `noble/python3`，今天两次请求都返回 500。同站首页是 200，搜索页也是 500，像是该站的包页面临时故障，与本卡改动无关。下次巡检再看；如果一直是 500，再换成 Launchpad 的对应页。

## 构建与篇幅

- **-W**：快照 `a6130dd` 单独跑 `-W` 通过（`strict_build_ga05.log`）。
- **篇幅**：8.6 改写后汉字 1653（不含 front matter），≤ 3500。

**自查**：问题 1、问题 3 都是 T-GA-02 带进来的。我当时只跑了 `-W`、核了链接，没有跑 `audit-fonts` 和 `audit-terms`。以后改动 Mermaid 图或页首文字的卡，校验时都单独跑这两项。

## 第 2 轮复核

快照 `7e97136`，这次连同根目录的 `OUTLINE.md` 一起同步。

- **问题 1**：8.1 图 2 改为 `flowchart TB` 里放两个 `direction LR` 子图（上行 beta、beta2、patch1，下行 EA、正式版），节点文字也缩短了。`audit-fonts` 结果：1440 与 2560 两档都是 16 px，缩放 1.003；全站 Mermaid 低于 12 px 的为 0。
- **问题 2**：1.1 `[^lab30-install]` 改指 `blob/v3.0.0-EA/docs/source/setup/installation/index.rst#L86-L96`。我在镜像里读了 L86–L96：Python 3.12、Ubuntu 22.04+ / Windows 11、32 GB / 16 GB、"Isaac Sim 5.1 and older are not supported"、推荐 580.95.05 / 581.42.00，都在。不在 EA tag 里的两条（下限 580.65.06 / 580.88、`torch==2.12.0` cu130）注明了"该版文档已下线，2026-09-30 查阅"。全站已没有 `release/3.0.0/source` 链接。
- **问题 3**：8.1 L13 改为"物理后端（backend）"。`audit-terms` 显示，首次详细讲解页未附英文的只剩 D-029 豁免的 2 条（4.14 Direct、4.9 Manager-based）。
- **导航**：用同步后的 OUTLINE 重跑 `audit-nav`，人工看 0（第 1 轮那条是快照的误报，已撤回）。
- **构建**：`-W` 通过（`strict_build_ga05_r2.log`）。
- 8.1 现在同时被 T-SITE-17 第一批改过（删了图 1 注里的决策编号）。本轮只核与本卡有关的三处，T-SITE-17 的改动在那张卡里核。

结论：**通过**。
