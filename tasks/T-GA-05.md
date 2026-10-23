# T-GA-05 收口：8.6 版本追踪改写 + 全站"版本说明"里的 3.0 内容按正式版扫一遍

状态: 已合并
优先级: P1（T-GA 系列最后一张，T-GA-01…04 全部合并后开工）
类型: 改写（不跑训练；实现约 3 h，校验约 2 h，校验方顺带跑一次全站巡检脚本）
依赖: T-GA-01…04、D-035、`tasks/T-8-common.md`
产出: `docs/8-frontier/8.6-version-tracking.md`；8.6"本站核对状态"表里列出的其余页面的"版本说明"与正文 3.0 断言（0.1–0.8、1.3、1.4、1.7、1.9、2.x、3.x、4.1、4.2、4.6、4.19、4.20、6.4.3、6.4.6、6.4.7、6.7.3、9.3、9.4、9.5、A.2、A.3 等，以表为准）；`docs/0-map/0.8-glossary.md` 中涉及 3.0 的条目；`docs/index.md` 首页"前沿专栏"一行（L11，手写，不是生成器产物；全专栏升级完才改，所以放在本卡）

## 要做什么

1. **8.6 改写**：表 1 加 v3.0.0 一行（日期、Isaac Sim 6.2、Python 3.12、主要变化、破坏性变更、已知问题，来源为 v3.0.0 的 release notes 与 GitHub 发布页）；"GA 复核时留意"一节按 T-GA-01 的 F2 写出结论：GA 发布页说 `--headless` 不再关闭可视化器，但本站实测 v3.0.0 的 `isaaclab train --headless` 仍返回 rc=2，文档与代码仍不一致，这一条改为"v3.0.0 仍不一致"并保留来源，不撤掉；"本站核对状态"表全部改为按 v3.0.0 核对、写新日期；EA 阶段的说明改成历史；"未来"只引 NVIDIA 公开说法（如 3.0.x 补丁），没有就不写。8.6 表 2 的页数统计按需同步。
2. **全站扫一遍**：对表里每页的 3.0 断言逐条按 v3.0.0 核对，改 permalink 与行号；T-GA-02 / 03 / 04 附记里列出的"受影响句子"（如 8.4 第 5 步、8.6 L81 引 8.10 的数字）在这里统一改。6.4.6 写的"IK 偏移雅可比问题 EA 仍在，release/3.0.0 已由 PR #8018 修复"，核对 v3.0.0 是否包含该修复。0.3 的"Isaac Sim 6.1 中 `omni.isaac.*` 已移除"改为 6.2 并实测一次 `import omni.isaac.core`。
3. 术语表：涉及 3.0 的条目（预设、可视化器、入口点、Kit-less 等）按 GA 核对；新术语攒到附记，由设计方开术语卡。
4. 全站 `grep -rn "3\.0\.0-EA\|3\.0 EA\|Isaac Sim 6\.1" docs/` 的剩余命中逐条说明为什么保留（只允许版本史与对照句）。

5. **8.6"维护流程"一节（原 L89–L93）在本卡改写**（设计裁断 2026-10-24）：保留"新 tag 发布后本站怎么更新"这层意思，因为它解释了"最后核对"日期的含义；但改成读者视角的三步：① 列出新 tag 与核对范围；② 只读新 tag 的文件，在表 1 加一行，按表 2 逐页核对并修改，"最后核对"改为新日期；③ 在另一个独立环境里逐格复核后发布。去掉"Claude Code 会话""设计 / 实现 / 校验会话"和卡号 T-8.6x。
6. 页面里的"校验方 / 实现方"字样（如 8.5 L104、L122）不在本卡处理，统一由 T-SITE-17 清理；本卡新写的句子不要再用这两个词。

## 校验（examine）

跑 `audit-all.sh` 全套；抽查 10 页的 3.0 断言与 v3.0.0 来源；第 4 条的保留清单逐条看；-W 构建。

## 验收标准

8.6 反映 v3.0.0；全站 3.0 断言按正式版核对；EA / 6.1 的剩余命中都有理由；巡检 0 阻塞。合并后设计方改 CLAUDE.md、OUTLINE、T-8-common 的版本表述，并向用户提交 D-019 主线切换评估（D-035 第 1 条）。

## 附记

（实现/校验 session 写）

**实现（accomplish，2026-10-24）**：原件在 `scratch/accomplish/tga05/`；只有 0.3 的导入检查跑了 Kit，其余都只读 v3.0.0 tag 的文件。
- **8.6**
  - 表 1 加 v3.0.0 一行，来源是 tag 安装页徽章 L6–L12（IsaacSim-6.2.0、python-3.12）、GA 发布页两节、迁移文档。GA 发布页没有已知问题一节，照实写。
  - 新增表 2"文档与代码不一致"三条（`--headless` / `--enable_cameras`；visualization.rst L146"多数任务默认 PhysX"；`--rl_library` 必填），按卡要求保留来源、写"v3.0.0 仍不一致"。
  - 核对状态表（现为表 3）全部按 v3.0.0 重写日期；行合并后仍逐页列出 52 页，其余 64 页。
  - 升级建议改为"主线暂仍 5.1 + 2.3.2，正在评估"。
  - 维护流程改成读者视角三步（设计方第 5 条），去掉会话名与 T-8.6x。
  - 用 audit-version.py 的工作区版本跑（`tga05/audit_wt.py`，把 git show 换成读文件）：问题只剩 A.5 缺固定句一条，原本就有的建议。为了与脚本的口径一致，没有给 8.6 加"版本说明"一节。
- **全站扫描**
  - 首页 L11 改为"Isaac Sim 6.2 + Isaac Lab 3.0.0 正式版"。
  - 0.1、1.4：页首提示框同 1.1，"GA 后切换主线"改为"正在评估"。
  - 0.2：版本链表、3.0 提示框、分层图、Kit 110.4.0、PyPI 6.2.0.0 脚注。
  - 0.3：时间线加 Isaac Lab 3.0（2026-10-19）与 Isaac Sim 6.2（GitHub v6.2.0 发布 2026-10-14）；`omni.isaac.*` 在 6.2 上实测（`tga05/imp.py`、`imp.log`）：pip 包 `omni.isaac.*` 目录 0 个，`import omni.isaac.core` 报 ModuleNotFoundError，`import isaacsim.core.api` 正常；3.11 同步。
  - 0.4、0.5、0.6、0.8、1.2、4.1、4.6 的 3.0 脚注由 EA Release Notes 改为 GA 发布页，所引内容都已在 GA 发布页里找到：Direct Isaac Sim imports、ProxyArray、index / mask、Kit-less、XYZW、"fresh Python 3.12 environment"。
  - 1.8：`--editor` 已在 v3.0.0 help 中核对。1.9、2.8：资产根 6.2 为 T-GA-01 实测；2.1 改为"6.x"；3.9 改为 6.2，仍未核对。
  - 3.6：#6439、#7416 都在 v3.0.0 中，imu.py L186。
  - 4.19、4.20：脚本 L 号改指 v3.0.0；第二套遥操作栈在 v3.0.0 里称"Isaac Capture-based"，`--teleop_device` 默认 None，`record_demos.py` 有 isaac_teleop。
  - 6.4.6：git log 确认 #8018（commit c06f83c44）与 #8318 都在 v3.0.0；`_compute_frame_jacobian` L253–L270 已是新写法，页面改为"v3.0.0 已修复"。
  - 6.4.7：robomimic 的 train.py / play.py 仍无 `external_callback`。
  - 9.5：Isaac-Lift-Franka 在 L17。A.3：文档链接改为 v3.0.0。
  - 8.3 L76、L100、L119：崩溃比例补上"正式版 13 次 0 次"（T-GA-03 附记所列）。
  - 8.4 第 5 步、8.6 L81 不含 8.10 的具体数字，不用改。
  - 涉及页面的 `sources_checked` 改为 2026-10-24，与 8.6 表 3 一致；表 3 里"只指向 8.1 / 8.4 / 1.5"的 14 页也一并改了日期。
- **术语表**：Kamino 改为"v3.0.0 中标为实验性"；OvPhysX 去掉"实验性"，改为"要另装 ovphysx、不能与 Kit 同进程"；GA 条目写发布日期；3.0 一组的说明改为基于 v3.0.0。
  - 新术语候选：`launch_simulation`、`list_envs`、Isaac Capture、LEAPP、TorchRL、`ActuatorCollection` / `actuators.target_command`。
- **剩余 EA / 6.1 命中的保留理由**（grep `3\.0\.0-EA|3\.0 EA|3\.0-EA|Isaac Sim 6\.1|release/3\.0\.0`，不含 A.5）
  - 0.3 L46、L56、L60、L73、L188：时间线与发布日期表里的历史版本。
  - 0.8 L294：EA 词条本身。
  - 1.1 L47、L62、L105、L106、L120、L134–L136、L142、L146：EA / 6.1 两行按 1.1 规则保留为历史，以及这两行的脚注。
  - 1.5 L31、L230：提到前一版基于 EA。
  - 3.11 L141：6.1 与 6.2 都实测过。
  - 6.4.6 L152、L173、L180、L181：PR 历史（release/3.0.0 回移）与"EA 时仍在"的对照。
  - 8.1 L111、L165：版本时间线。
  - 8.3 L60、L71、L76、L100、L119：Galbot 资产表是 EA 时的实测、崩溃比例的 EA 对照。
  - 8.4 L65、L118、L163：标"EA"的实测行。
  - 8.5 L13、L62、L181：迁移实录与容量对照是 EA 时的记录。
  - 8.6 L27、L98、L100：表 1 的 EA 行与脚注。
  - 8.7 L168：2.3 → 3.0 对照表里"`--viz newton`（3.0 EA）"一行。
  - 8.8 L13：截图是 EA 时的。
  - 8.10 L13：最早按 EA 写成。
- **未处理（按卡）**："校验方 / 实现方"字样交给 T-SITE-17；本卡新写的句子没有用这两个词。
- gen_placeholders 跑过；-W 通过。

**本卡改动的文件清单（供按清单合并，44 个，均在 docs/ 下）**：0-map/0.1-overview.md 0-map/0.2-layers.md 0-map/0.3-lineage.md 0-map/0.4-isaac-names.md 0-map/0.5-sim-lab-boundary.md 0-map/0.6-one-step.md 0-map/0.7-learning-paths.md 0-map/0.8-glossary.md 1-env/1.2-version-decision.md 1-env/1.3-hardware.md 1-env/1.4-install-51-232.md 1-env/1.7-install-methods.md 1-env/1.8-dev-tools.md 1-env/1.9-install-troubleshooting.md 2-usd-kit/2.1-why-usd.md 2-usd-kit/2.2-usd-concepts.md 2-usd-kit/2.4-physics-schema.md 2-usd-kit/2.8-nucleus.md 3-isaacsim/3.11-api-map.md 3-isaacsim/3.1-sim-loop.md 3-isaacsim/3.2-simulation-app.md 3-isaacsim/3.3-rigid-collision.md 3-isaacsim/3.4-articulation.md 3-isaacsim/3.5-urdf-mjcf-import.md 3-isaacsim/3.6-sensors.md 3-isaacsim/3.8-rendering.md 3-isaacsim/3.9-replicator.md 4-isaaclab/4.19-mimic.md 4-isaaclab/4.1-why-isaac-lab.md 4-isaaclab/4.20-teleop-devices.md 4-isaaclab/4.2-repo-map.md 4-isaaclab/4.6-assets.md 6-galbot/4-task/6.4.3-lift.md 6-galbot/4-task/6.4.6-teleop-demos.md 6-galbot/4-task/6.4.7-mimic.md 6-galbot/7-deploy/6.7.3-sim2real-checklist.md 8-frontier/8.3-newton.md 8-frontier/8.6-version-tracking.md 9-source/9.3-articulation-data.md 9-source/9.4-train-script.md 9-source/9.5-franka-lift.md appendix/A.2-error-index.md appendix/A.3-official-resources.md index.md 

**校验（examine，2026-10-24，第 1 轮）**：退回，2 条一般、1 条低，另有 1 条交设计方，见 `reviews/T-GA-05.md`。
- `MOBILE=1 audit-all.sh` 全套跑在快照 a6130dd 上：锚点、占位页、示例、互指、图表编号都是 0；版本说明只剩 A.5 那条原有的。
- 保留清单与我的 grep 逐行一致；抽查 10 处 3.0 断言（6.4.6、3.6、4.20、6.4.7、9.5、1.8、0.3 / 3.11、0.2、8.6 表 2、0.8）全部成立。-W 通过；8.6 汉字 1653。
- 问题 1（一般）：8.1 图 2 加了第 5 个节点后，1440 宽下文字只有 10.8 px（D-025）。是 T-GA-02 带进来的，当时校验漏了。
- 问题 2（一般）：1.1 的 `[^lab30-install]` 链接（release/3.0.0 文档）已 404，请改为 v3.0.0-EA tag 的 permalink。
- 问题 3（低）：8.1 L13 第一次出现"物理后端"没有附英文。
- 建议：packages.ubuntu.com 包页面今天返回 500，下次巡检再看。
- 更正（examine）：第 1 轮说"OUTLINE 里 1.5 的标题还没改"是误报，我的快照没有同步 OUTLINE.md，已在报告里撤回。

**实现第 2 轮（accomplish，2026-10-24）**
- ① 8.1 图 2 改为两行：用两个 `direction LR` 的子图放在 `flowchart TB` 里，上行是 beta、beta2、patch1，下行是 EA、正式版；beta2 与 patch1 的节点文字缩短了。图注改为"上行自左向右，接着下行"。每行最多 3 个节点，估计缩放会比原来 5 个节点一行时大，字号请用 audit-fonts 复核。
- ② 1.1 [^lab30-install] 改指 `blob/v3.0.0-EA/docs/source/setup/installation/index.rst#L86-L96`。EA tag 里有 Python 3.12、Ubuntu 22.04+ / Windows 11、不支持 5.1、推荐 580.95.05 / 581.42.00；不在 EA tag 里的两条（580.65.06 / 580.88 下限，`torch==2.12.0` cu130）注明"取自 release/3.0.0 在线文档，该版已下线，2026-09-30 查阅"。
- ③ 8.1 L13 改为"物理后端（backend）"。
- **合并提醒**：8.1 现在两张卡都改过。T-SITE-17 第一批删了图 1 注里的"D-010"；本轮改了 L13 与图 2。合并时请把 8.1 当作两张卡共有的文件。-W 通过。

**校验（examine，2026-10-24，第 2 轮）**：通过。8.1 图 2 两档都是 16 px，全站 Mermaid < 12 px 为 0；1.1 脚注改指 v3.0.0-EA tag 的 L86–L96，并注明下线的两条；8.1 L13 补了英文。快照 7e97136（含 OUTLINE），-W 通过；audit-nav 人工看 0。
