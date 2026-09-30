# 写作与代码规范

## 1. 目录与文件命名

```
docs/
  index.md                      首页
  0-map/0.2-layers.md           <部分编号>-<部分slug>/<页面编号>-<页面slug>.md
  1-env/1.1-compat-matrix.md
  6-galbot/1-asset/6.1.2-import-urdf.md
  assets/img/<页面编号>-<名字>.svg   图片
examples/
  isaaclab-2.3/<页面编号>-<slug>/   每个示例一个目录，含 README.md 说明运行方式
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

## 2. 页面模板

每页按以下顺序，标题层级固定：

```markdown
---
title: <页面标题>
verified: "Isaac Sim 5.1.0 / Isaac Lab 2.3.2"   # 无代码的概念页写 "n/a"
updated: 2026-09-30
sources_checked: 2026-09-30                       # 来源核查日期
---

# <页面标题>

!!! abstract "学习目标"
    - …（2–4 条，动词开头；不要写"读完本页你能："这类引导句）

!!! info "前置知识"
    - [x.y 页面标题](../路径.md)

<正文，二级标题分节>

（站点上"学习目标 / 前置知识"渲染为页首引导块：左侧细绿线、灰色小标题、前置知识压成一行，不是彩色提示框；源文件写法不变，见 T-SITE-05 附记第 3 点。）

## 常见坑
（可为空，但标题保留；概念页可改为"## 常见误解"，见 D-012）

## 延伸阅读
- 官方文档：…
- 源码：…
- 中文翻译：isaac.kiloong.com 对应页

## 版本说明
（本页内容在其他版本上的差异；3.0 相关差异必须在此提及并链接第 8 部分对应页）
```

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
- **图的尺寸**：单张图高度控制在一屏以内（约 ≤ 700px）。节点只写层名和 2–4 字角色，细节放正文或表格。架构图箭头语义统一为"构建在……之上 / 运行在……之中"，图说明写明（D-010）。方向约定（D-017）：分层/依赖图竖排、底层在下；流程/流水线/时间线左→右；时序图上→下。
- 不复制官方文档原文超过一句话。需要引用时改为链接。
- 不写"显然""众所周知"。不写营销语气。
- 提示框统一使用 MkDocs Material admonition：`note`、`tip`、`warning`、`danger`，"常见坑"里的每条用 `warning`。

## 4. 来源优先级

1. Isaac Lab 源码（tag `v2.3.2`，链接用 GitHub permalink 带 tag）
2. Isaac Lab 官方文档 https://isaac-sim.github.io/IsaacLab/v2.3.2/ 与 release notes
3. Isaac Sim 官方文档 https://docs.isaacsim.omniverse.nvidia.com/5.1.0/ 与 release notes
4. Omniverse Kit / USD / PhysX 官方文档
5. NVIDIA 官方论坛、GitHub issues（标注"社区经验"）
6. 论文、博客（标注"社区经验"）

中文翻译站 isaac.kiloong.com 只作"延伸阅读"链接，不作断言来源。

## 5. 代码规范

- 示例代码放 `examples/isaaclab-2.3/<页面编号>-<slug>/`，页面里只嵌入关键片段，并注明完整文件路径。
- 每个示例目录含 `README.md`：运行命令、预期输出、显存需求、运行时长。
- 文件头注释标明：验证版本、验证日期、GPU 型号。未运行过的写 `# 未验证`。
- 用 Isaac Lab 2.3.2 的 API 命名（`isaaclab.*`、`isaacsim.*`），不用 `omni.isaac.*` 旧命名，除非是在讲迁移。
- `num_envs` 默认值保守（≤ 1024），页面里说明如何调大。
- Python 遵循 Isaac Lab 仓库的风格（type hints、docstring），不引入额外依赖。

## 6. 实现自检清单（写在任务卡附记区，逐条打勾）

- [ ] 页面结构与模板一致，frontmatter 完整
- [ ] 任务卡"必须覆盖"各点均已覆盖
- [ ] 每条架构/版本/API 断言有来源
- [ ] 图有说明文字，Mermaid 能在 `mkdocs serve` 中渲染，**且已截图目检**（方向、层次、深浅色），截图路径写入附记
- [ ] 示例代码已运行（或明确标注未验证）
- [ ] 术语与术语表一致
- [ ] 内部链接可达（`mkdocs build --strict` 通过）

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
