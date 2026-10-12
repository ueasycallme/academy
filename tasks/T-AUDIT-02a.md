# T-AUDIT-02a 全站一致性修正（文本类，源自 reviews/AUDIT-02.md）

状态: 已合并
优先级: P2（机械改动为主，不占 GPU；T-6.4.5b 训练间隙做）
类型: 微任务（AUDIT-02 的 G-1…G-6、G-8、G-9 与 S-1、S-2、S-3、S-6、S-9、S-10）
产出: 下列页面与示例目录 README

## 必须完成（条目编号同报告）

1. **G-1** 6.1.6 L171：改为"6.4.5 查明了原因（自碰撞，补 220 对过滤对后静置 0.2 rad/s）"，链 6.4.5"先修资产"。
2. **G-2** 6.6.1 L118：改为"ONNX 的数值比对见 6.7.2"（删"本机没有装 onnxruntime"）。
3. **G-3** 0.3 L176、3.11 L100：若本地有 3.0 环境，先跑一次 `python -c "import omni.isaac.core"`（≤ 1 min，不算长进程），把结果写进两处："本站 6.1 pip 包里 `omni.isaac.*` 扩展目录为 0（5.1 有 65 个），导入 `omni.isaac.core` 报 …"；没有 3.0 环境就只写目录层面的结论并注明"导入行为未测"。
4. **G-4** 6.1.2 L80：改为"同一组内的正则不能重叠（重叠时抛 `Multiple matches`）；不同组之间重叠不报错、后组静默覆盖（6.1.6）"。L82 不动。
5. **G-5** 2.5 L153 / L193、A.2 L67：改为"未捕获的异常时退出码实测为 0，不能靠退出码判断成败"，与 7.4 L95 一致。
6. **G-6** 6.4.1 L215：句末加"训练后的策略输出会超出 ±1，部署前要裁剪，见 6.7.3 二、动作"。
7. **G-8** 0.6 步骤表加表注"*表 1：…*"（措辞自定），之后 0.6 若还有别的表，编号顺延并核页内引用。
8. **G-9** 新建 `examples/isaaclab-2.3/3.6-sensors/README.md`（运行命令、预期输出、显存、时长，照 3.6 页 L79–L83）。
9. **S-1** 5 个重定向换成新地址：7.4 L128、L129，6.1.7 L132（docs.github.com）；1.6 L181（cuda-compatibility `latest`）；3.9 L146（Replicator API 跳到 `omni_replicator/latest`，**先核对引用的内容在新页上还在**，不在就保留旧链接并加一句"原 1.12.27 版地址已重定向"）。
10. **S-2** Prim / Term 小写 16 处按 `3-terms.txt` CASE 行机械替换；6.1.7 L77 的"prim spec"保留。
11. **S-3** A.1、A.2、A.3 的"版本说明"末尾补 T-8.6b 固定句（三页已在 8.6 表 2 逐行列出）；A.5 不加。
12. **S-6** 6.2.1 L125 加一句"专测见 6.2.3 表 1"；6.6.1 L30 附近加一句：原运行目录已在重启中丢失，重训目录与评估结果见 6.7.2。
13. **S-9** 第 6 部分 ②–⑦ 六个小节 index 页各补一句简介（这一节做什么、从哪页读起），写法参照 ①。
14. **S-10** 7.6 第一张表补"表 1"表注（后续编号不变即可，因为原来从表 2 开始）；`2.7-extensions` 目录 README 补一行 GPU；8.6 表 2 表注日期改 2026-10-12；A.5"里程碑"加"2026-10-12　大纲 114 页全部上线"（若该段由生成器产出则改生成器的数据源，附记说明）。

15. **AUDIT-02b G-1（站点样式）**：`docs/_static/academy.css` L144–L145 与 `table-code-wbr.js` L22 的选择器从 `.bd-article table code` 扩到 `.bd-article code`，注释里"只作用于表格"的说法一起改；改完在 390 px 下抽 6.4.7、6.1.7 两页看正文不再整体横滚（校验方会用 `MOBILE=1 audit-all.sh` 复跑，撑破页数：39 页范围内应为 0，全站应只剩 0.6 一页（Sphinx 生成的脚注回链，15 px，不改））。
16. **AUDIT-02b S-1**：1.1 脚注 `[^sim45]` 的纯文本长串改成可换行的写法（加空格或拆成短链接）；0.6 脚注回链 (1,…,20) 是 Sphinx 生成的，不改。

## 约束

- 只改列出的位置，不顺手改措辞；每条在附记里写"已改 / 未改（理由）"。
- `sphinx-build -W` 通过；附记给 `git diff --stat`。
- 校验方复核：`audit-all.sh` 重跑，G-1…G-9 应为 0（G-7 由 T-0.8o 处理），S-2 的 CASE 行只剩"prim spec"。

## 附记

（实现 / 校验 session 写）

### 实现方（2026-10-12）

1. G-1，已改：6.1.6 L171 改为"……曾达到 200–320 rad/s，6.4.5 查明了原因（自碰撞，补 220 对过滤对后静置 0.2 rad/s）"，链 6.4.5 `#先修资产被动滚子为什么空转`。
2. G-2，已改：6.6.1 L118 后半句改为"ONNX 的数值比对见 6.7.2"（链 `6.7.2-ros2-closed-loop.md`）。
3. G-3，已改，导入已实测。环境是 `/home/wuql/wuql_ws/isaac_sim/env_isaaclab30_pip`：`isaacsim` 6.1.0.0，Python 3.12.14。注意不是 AUDIT-02 用的 6.1.0-rc.26。
   - 该环境 `isaacsim/` 下的 `omni.isaac.*` 扩展目录数：`exts/` 0、`extscache/` 0、`extsPhysics/` 0、`extsDeprecated/` 0。5.1 环境（`isaacsim` 5.1.0.0）的 `extsDeprecated/` 有 65 个。
   - 字面命令 `OMNI_KIT_ACCEPT_EULA=YES python -c "import omni.isaac.core"`：rc 1，`ModuleNotFoundError: No module named 'omni.isaac'`。不启动 Kit 时 `omni` 命名空间本来就不全，5.1 下也不能这样导入，所以字面命令只作参考。
   - 先启动 `SimulationApp({"headless": True})` 再导入：报 `ModuleNotFoundError: No module named 'omni.isaac.core'`（Kit 把它转成 `[Error] [omni.kit.app._impl] [py stderr]` 行打印）。
   - 5.1 环境跑同一脚本：导入成功，模块在 `extsDeprecated/omni.isaac.core/`，并打印 `omni.isaac.core has been deprecated in favor of isaacsim.core.api` 等弃用警告。
   - 脚本与日志在 `scratch/accomplish/tA02/`：`import_after_app.py`、`lit.log`、`app.log`、`app51.log`。
   - 0.3 L176、3.11 L100 改为写实测结论。
   - 3.11 的"版本说明"一节没动，所以 8.6 表 2 仍把它归入"不涉及 3.0"。是否因为正文有了 6.1 的实测结论而改为逐行列出，请设计定。
4. G-4，已改：6.1.2 L80 照建议改写，链 6.1.6。
5. G-5，已改：2.5 L153（表 3 表注）、2.5 L193（坑五首句）、A.2 L67，都改为"未捕获的异常时退出码实测为 0，不能靠退出码判断成败"。
6. G-6，已改：6.4.1 表 6 第 3 项句末补"训练后的策略输出会超出 ±1，部署前要裁剪，见 6.7.3 二、动作"，链 `#二动作`。
7. G-8，已改：0.6 三张表依次加表注表 1（`env.step()` 的步骤与所在层）、表 2（三个时间尺度）、表 3（Manager-based 与 Direct 的对应）。页内原来没有"表 N"的引用；9.1 的五处"0.6 表 1"现在对得上。
8. G-9，已改：新建 `examples/isaaclab-2.3/3.6-sensors/README.md`，内容是运行命令、两段预期输出与资源表。显存、内存、时长取自 `scratch/accomplish/t36/*.summary`（2026-10-11 实测）。
9. S-1，已改：
   - 7.4 L128 → `…/actions/reference/workflows-and-actions/workflow-syntax`；
   - 7.4 L129 → `…/actions/concepts/runners/self-hosted-runners`；
   - 6.1.7 L132 → `…/billing/concepts/product-billing/git-lfs`；
   - 1.6 L181 → `…/cuda-compatibility/latest/index.html`；
   - 3.9 L146：旧地址重定向到 Replicator 文档首页，不是 API 页。改链到 `kit/docs/omni_replicator/latest/source/extensions/omni.replicator.core/docs/API.html`，核对 `create` / `modify` / `randomizer` / `trigger` / `orchestrator` / `WriterRegistry` 都在该页（curl 计数 29–95 次）。脚注加注"原 1.12.27 版地址已重定向；这是 latest 版，不固定版本"。
   - 跳转目标都用 `curl -sL` 核对过，返回 200。
10. S-2，已改 15 处：按 3-terms.txt 的 CASE 行逐行替换，代码与链接里的不动。`command term` → `command Term`；6.1.7 L77 的"prim spec"保留。
11. S-3，已改：A.1、A.2、A.3"版本说明"末尾各加固定句（只加一个空行与一句）；A.5 未加。
12. S-6，已改：6.2.1 L125 句末加"专测见 6.2.3 表 1"；6.6.1 L30 加"原运行目录已在一次重启中丢失，重训的目录与评估结果见 6.7.2"。
13. S-9，已改：第 6 部分 ②–⑦ 的 index 页各加一句"这一节做什么、从哪页读起"，放在标题与 toctree 之间。
14. S-10，已改：
    - 7.6 第一张表补"表 1"表注。
    - `2.7-extensions/README.md` 补一行 GPU，并说明 `exts/*/extension.py` 在 Kit 进程里运行。
    - 8.6 表 2 表注日期改为 2026-10-12。
    - A.5"里程碑"加"2026-10-12　大纲 114 页全部上线"。这一段是人工写的，不归生成器管（生成器只管 `changelog:begin` 之间）。这一行已随 1a3766a 进了 HEAD。
15. AUDIT-02b G-1，已改：
    - `academy.css` 与 `table-code-wbr.js` 的选择器由 `.bd-article table code` 扩到 `.bd-article code`（CSS 两行）。
    - 两处注释改为"正文行内代码……由表格内扩到全文"；CSS 注释里 `overflow-wrap: anywhere` 那句改为"只作用于右栏目录"（anywhere 规则本来就只在目录上）。
    - 390 px 实测未做，请校验方用 audit 脚本复核。
16. AUDIT-02b S-1，已改：1.1 `[^sim45]` 的两段路径改成行内代码（`docs.isaacsim.omniverse.nvidia.com/4.5.0/`、`/5.0.0/`），由 15 的断行规则折行。0.6 的脚注回链未改。

`gen_placeholders --check` 0 不一致；`check_head_build.sh --worktree`（-W）通过。本卡与 T-0.8o 合计改动：docs 37 个文件（两卡共用 2.5、3.9），examples 2 个（`2.7-extensions/README.md` 修改，`3.6-sensors/README.md` 新增）。工作区里另有 T-6.4.5b 的脚本与配置改动，不属于本卡。

补（设计裁断，并入第 3 条）：3.11 改为在 8.6 表 2 逐行列出。
- 3.11"版本说明"补写已核对项（6.1 中 `omni.isaac.*` 已移除，2026-10-12）与固定句。
- 8.6 表 2 加 3.11 一行，表注改为"逐页归类 112 页（逐行 48，其余 64）；不涉及 2 页（A.5、模板页）"。
- 0.3 原来就在逐行的"0.3、0.4……"那一行里，不在"其余 64"中，不用移。

### 校验方

- 2026-10-12 校验 session：**退回**（`reviews/T-AUDIT-02a.md`），3 条都是低级问题，请当轮补改：
  1. 3.11 的 `sources_checked`；
  2. 8.6 表 2 中 0.3 那一行要反映 6.1 实测；
  3. 2.5 坑五首句重复。
- 16 条改动全部核过，各项复跑：
  - 390 px：39 页撑破 0，全站 1（0.6）；
  - 8.6 三个数为 48 / 112 / 2（`audit-version.py` 已改为认得逐行列出的 3.11）；
  - figures、examples、术语表的问题都为 0；外链重定向 14 → 9；Prim / Term 小写只剩 "prim spec"。
  - -W 通过（`strict_build55.log`）。

第 2 轮（按 reviews/T-AUDIT-02a.md 的退回项）：
1. 已改：3.11 的 `sources_checked` 改为 2026-10-12。
2. 已改：8.6 表 2 把 0.3 从"0.3、0.4、0.5、0.6、0.8"那一行拆出来单列，写明正文的 6.1 实测，核对版本加 Isaac Sim 6.1.0（`isaacsim` 6.1.0.0），日期 2026-10-12；其余四页仍在原行。逐行仍是 48 页（0.3 原本就在逐行里），表注三个数不变。0.3 的 frontmatter `sources_checked` 也改为 2026-10-12（校验方第 2 轮补充）。
3. 已改：2.5 坑五第二句删掉重复的"未捕获的异常照样退出码 0；"，改为"本站实测：`close()` 会直接结束进程……"。
`check_head_build.sh --worktree` 通过。
- 2026-10-12 校验 session（复核）：第 2、3 轮补改核过，`audit-version` 结果为 48 / 112 / 2，0 个一般；-W 通过（`strict_build56.log`）。**通过**。
