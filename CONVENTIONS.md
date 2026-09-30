# 写作与代码规范

## 1. 目录与文件命名

```
docs/                            Sphinx 源（conf.py、_static、_templates 在此）
  index.md                      首页（含各部分 toctree）
  0-map/0.2-layers.md           <部分编号>-<部分slug>/<页面编号>-<页面slug>.md
  1-env/1.1-compat-matrix.md
  6-galbot/1-asset/6.1.2-import-urdf.md
  _static/img/<页面编号>-<名字>.svg   图片
  _build/                       构建产物，已 gitignore
examples/
  isaaclab-2.3/<页面编号>-<slug>/   每个示例一个目录，含 README.md 说明运行方式
tools/serve.sh                   本地预览（全量构建 + http.server，默认 8767）
tools/check_head_build.sh        设计 session 提交后运行
```

页面编号与 `OUTLINE.md` 一致。slug 用英文小写、连字符。各部分目录名固定如下：

| 部分 | 目录 |
|---|---|
| 0 全景地图 | `0-map` |
| 1 环境与版本 | `1-env` |
| 2 USD 与 Kit | `2-usd-kit` |
| 3 Isaac Sim 核心 | `3-isaacsim` |
| 4 Isaac Lab 核心 | `4-isaaclab` |
| 5 RL 入门 | `5-rl` |
| 6 主线项目 | `6-galbot/1-asset`、`2-scene`、`3-sim-align`、`4-task`、`5-train`、`6-eval`、`7-deploy` |
| 7 工程基础设施 | `7-infra` |
| 8 3.0 前沿 | `8-frontier` |
| 9 源码导读 | `9-source` |
| 附录 | `appendix` |

已定的占位页路径：`0-map/0.3-lineage.md`、`0-map/0.4-isaac-names.md`、`1-env/1.1-compat-matrix.md`、`8-frontier/8.1-what-changed.md`。页面 slug 由任务卡指定；未指定时实现方自拟并在附记中列出。

## 2. 页面模板（MyST，D-020 后唯一写法）

每页按以下顺序，标题层级固定。站点上"学习目标 / 前置知识"渲染为页首引导块（左侧细绿线、灰色小标题），不是彩色提示框。

`````markdown
---
title: <页面标题>
verified: "Isaac Sim 5.1.0 / Isaac Lab 2.3.2"   # 无代码的概念页写 "n/a"
updated: 2026-09-30
sources_checked: 2026-09-30                       # 来源核查日期
---

# <页面标题>

:::{admonition} 学习目标
:class: lead-goals

- …（2–4 条，动词开头；不写"读完本页你能："这类引导句）
:::

:::{admonition} 前置知识
:class: lead-prereq

- [x.y 页面标题](../路径.md)
:::

## <第一节标题>

这一节回答：<本节回答的问题>？

<正文。断言句末加脚注[^key]。站内链接写相对路径 [0.2 分层依赖图](../0-map/0.2-layers.md)，锚点链接写 [文字](page.md#标题)。>

```{mermaid}
flowchart TB
    A["…"] --> B["…"]
```

*图 1：<一行说明，写明箭头语义（D-010 / D-017）>*

::::{tab-set}
:::{tab-item} conda
```bash
…
```
:::
:::{tab-item} venv
```bash
…
```
:::
::::

## 常见误解            （概念页；实操页写"## 常见坑"；可为空但标题保留）

:::{admonition} 误解一：…
:class: warning

…
:::

## 延伸阅读

- 官方文档：…
- 源码：…
- 中文翻译（中文翻译站，译自最新版 Isaac Sim 文档，与主线 5.1.0 可能有差异）：…

## 版本说明

（本页内容在其他版本上的差异；3.0 相关差异必须在此提及并链接第 8 部分对应页）

[^key]: 页面名：URL（要点）
`````

MyST 要点：
- 提示框统一 `:::{admonition} 标题` + `:class: note|tip|warning|danger`，冒号围栏；内部要嵌套代码块或 tab-set 时，外层冒号多一个。
- 术语表锚点：块级目标写 `(term-xxx)=` 单独一行放在块前；行内写 `[**术语**]{#term-xxx}`。
- 占位页：frontmatter 加 `orphan: true` 且不进 toctree；进入 toctree 的页面不要写 `orphan`。
- 脚注、GFM 表格原生支持；`## 标题` 自动生成锚点（`myst_heading_anchors = 3`）。

## 3. 写作规范

- 简体中文。术语定义以 `0.8 术语表` 为准，中英使用规则（D-018）：
  - **保留英文不翻译**：USD 基本对象（Stage、Prim、Layer、Schema）；代码中的类名、配置项与参数（Articulation、configclass、Manager、Term、decimation、num_envs、dt、render_interval）；产品与项目名；业界通用且翻译后难检索的词（rollout、headless、sim2real、PPO）。大小写按术语表，如 Prim、Term 首字母大写。
  - **用中文，首次出现附英文**：一般概念，全页第一次写成"中文（English）"，之后只用中文，如"刚体（rigid body）"、"执行器（actuator）"、"域随机化（domain randomization）"。
  - **两种写法都允许**：适配层（wrapper）首次写对照形式，之后同页二选一保持一致。"扩展"可以单独使用，不强制附 extension。
  - 术语表未收录的词按上述规则判断；新增术语先补术语表再使用。
- 先讲"是什么、为什么这样设计"，再讲"怎么用"。每一节开头一句话说明本节回答什么问题。
- 段落短。一个概念一张图优先于一大段文字。
- 图用 Mermaid（流程、时序、依赖）或 SVG（架构图，放 `docs/assets/img/`）。图必须有一行文字说明。
- **断言必须可追溯**：涉及架构、依赖、版本、API 行为的每一句话，要能指向来源。来源放在句末的脚注或"延伸阅读"。查不到来源的写"（推断：依据…）"。
- **脚注格式**（全站标准，源自样板页）：`[^key]: 页面名：URL（要点）`。括号内写要点、不加引号；确需原文时单独加引号，且不超过一句。表格的"来源"列用同一套脚注。
- **站内交叉引用一律做成链接**，目标页不存在则建占位页（D-011）。
- **公式**（D-022，T-SITE-10 合并后生效）：行内 `$...$`，独立公式 `$$...$$`（MathJax）。只在能省掉一段文字时才用公式；每个公式下方逐个解释符号与单位；字面美元符号写 `\$` 或放进行内代码。
- **图的尺寸**：单张图高度控制在一屏以内（约 ≤ 700px）。节点只写层名和 2–4 字角色，细节放正文或表格。架构图箭头语义统一为"构建在……之上 / 运行在……之中"，图说明写明（D-010）。方向约定（D-017）：分层/依赖图竖排、底层在下；流程/流水线/时间线左→右；时序图上→下。
- **图中文字的最小字号**（D-025）：图在页面上实际渲染后（含被容器缩放），文字的字号不低于 12px（正文 16px 的 75%），在 1440 与 2560 两档宽度下都要满足。达不到时不要靠缩小整图来塞进一屏：合并参与者、缩短节点与消息文字，或拆成两张图。实现方自检与校验方截图目检都要量这一项，把测得的字号写进附记 / 报告。
- 不复制官方文档原文超过一句话。需要引用时改为链接。
- 不写"显然""众所周知"。不写营销语气。
- 提示框统一使用 MyST admonition（见第 2 节），"常见坑 / 常见误解"里的每条用 `warning`。

## 4. 来源优先级

1. Isaac Lab 源码（tag `v2.3.2`，链接用 GitHub permalink 带 tag）
2. Isaac Lab 官方文档 https://isaac-sim.github.io/IsaacLab/v2.3.2/ 与 release notes
3. Isaac Sim 官方文档 https://docs.isaacsim.omniverse.nvidia.com/5.1.0/ 与 release notes
4. Omniverse Kit / USD / PhysX 官方文档
5. NVIDIA 官方论坛、GitHub issues（标注"社区经验"）
6. 论文、博客（标注"社区经验"）

中文翻译站 isaac.kiloong.com 只作"延伸阅读"链接，不作断言来源。

**来源链接无法自动抓取时**（如 docs.omniverse.nvidia.com 对 curl / WebFetch 返回 403）：脚注仍写公开 URL；校验方可改用内容相同的官方副本核对（例如 Isaac Sim pip 包内随附的同一份文档、官方 GitHub 仓库里的源文件），并在校验报告里写明用的是哪份副本及其路径。不因"自动抓取被拒"判来源不成立，也不因此把链接换成非官方镜像。

## 5. 代码规范

- 示例代码放 `examples/isaaclab-2.3/<页面编号>-<slug>/`，页面里只嵌入关键片段，并注明完整文件路径。
- 每个示例目录含 `README.md`：运行命令、预期输出、显存需求、运行时长。显存数字注明测量口径（按进程还是整卡峰值、`num_envs`、是否 headless），优先按进程测量，统一用 `reviews/scripts/gpu-mem-per-process.sh`（实现与校验两边同一脚本）。
- 文件头注释标明：验证版本、验证日期、GPU 型号。未运行过的写 `# 未验证`。
- 用 Isaac Lab 2.3.2 的 API 命名（`isaaclab.*`、`isaacsim.*`），不用 `omni.isaac.*` 旧命名，除非是在讲迁移。
- `num_envs` 默认值保守（≤ 1024），页面里说明如何调大。
- 启动了 `SimulationApp` / `AppLauncher` 的脚本，退出前按顺序做三件事（均为本站实测，reviews/T-2.4.md、reviews/T-3.2.md）：
  1. 用了 Isaac Lab 的 `SimulationContext` 时，调用 `sim.clear_all_callbacks()` 与 `sim.clear_instance()` 释放它，否则会卡在 `close()`（Isaac Sim 的 `World` 不需要）；
  2. `sys.stdout.flush()`，否则输出重定向到文件或管道时会丢失；
  3. `simulation_app.close()`。
  仿真对象统一建在 `main()` 里，便于退出前释放。
- Python 遵循 Isaac Lab 仓库的风格（type hints、docstring），不引入额外依赖。

## 6. 实现自检清单（写在任务卡附记区，逐条打勾）

- [ ] 页面结构与模板一致，frontmatter 完整
- [ ] 任务卡"必须覆盖"各点均已覆盖
- [ ] 每条架构/版本/API 断言有来源
- [ ] 图有说明文字，Mermaid 能在本地预览中渲染，**且已截图目检**（方向、层次、深浅色），截图路径写入附记
- [ ] 示例代码已运行（或明确标注未验证）
- [ ] 术语与术语表一致
- [ ] 内部链接可达（`sphinx-build -W` 通过（`tools/serve.sh` 会构建））

## 7. 校验清单（`reviews/T-<编号>.md` 模板）

```markdown
# T-<编号> 校验报告

- 校验日期：
- 校验版本：Isaac Sim x / Isaac Lab y
- 结论：通过 / 退回

## 断言核查
| # | 页面位置 | 断言 | 来源是否成立 | 备注 |

## 覆盖检查
任务卡"必须覆盖"逐条：已覆盖 / 缺失 / 不准确

## 代码运行
命令、环境、GPU、结果、耗时、显存峰值

## 问题清单（退回时必填）
| # | 位置 | 问题 | 依据 | 建议 | 严重度(阻塞/一般/建议) |

## 其他意见
```

严重度为"阻塞"的问题存在时必须退回；只有"一般/建议"时可通过并附意见。
