# 协作协议

三个 session 在同一目录工作。**文件系统是唯一事实来源**，session 之间的消息只用于通知。

## 角色

### 设计 session（`isaac-academy-master`）
- 维护 `OUTLINE.md`、`CONVENTIONS.md`、`WORKFLOW.md`、`CLAUDE.md`、`DECISIONS.md`。
- 为每个页面/示例写任务卡 `tasks/T-<编号>.md`。
- 处理 `DECISIONS.md` 中的"待裁断"条目。
- 校验通过后执行 `git commit`，并把任务状态改为"已合并"。
- 不写 `docs/`、`examples/`、`reviews/`。

### 实现 session（`isaac-academy-accomplish`）
- 从 `tasks/` 中领取状态为"待实现"的任务，把状态改为"实现中"。
- 按任务卡和 `CONVENTIONS.md` 写 `docs/`、`examples/`。
- 完成后过任务卡里的自检清单，把状态改为"待校验"，在附记区写明产出文件路径和自检结果，然后通知校验 session。
- 收到"退回"后，按 `reviews/T-<编号>.md` 中的问题清单逐条修改，逐条在附记区回复"已改 / 不认同（理由）"，再改回"待校验"。
- 不认同校验意见时，在 `DECISIONS.md` 追加"待裁断"条目，不要来回争论。
- 不改任务卡的正文，不改设计文件，不写 `reviews/`。

### 校验 session（`isaac-academy-examine`）
- 领取状态为"待校验"的任务，把状态改为"校验中"。
- 按 `CONVENTIONS.md` 的校验清单，逐条核查断言（对照官方文档、源码、release notes），运行示例代码（允许使用 GPU）。
- 写 `reviews/T-<编号>.md`，结论为"通过"或"退回"。退回必须附带可操作的问题清单，每条注明：位置、问题、依据、建议。
- 把任务状态改为"通过"或"退回"，通知对应 session（通过→设计，退回→实现）。
- 不改 `docs/`、`examples/`；发现小错误也写进报告，不直接修。

## 任务状态

```
待实现 → 实现中 → 待校验 → 校验中 → 通过 → 已合并
                     ↑                  │
                     └──── 退回 ────────┘
```

状态写在任务卡顶部的 `状态:` 行，只允许上述值。

## 文件所有权

| 路径 | 可写 session |
|---|---|
| `CLAUDE.md`、`WORKFLOW.md`、`CONVENTIONS.md`、`OUTLINE.md`、`DECISIONS.md`（裁断区） | 设计 |
| `tasks/*.md` 正文 | 设计 |
| `tasks/*.md` 的"状态"行与"附记"区 | 实现、校验 |
| `docs/**`（Sphinx 源，含 `conf.py`、`_static`、`_templates`）、`examples/**`、`tools/serve.sh`、`.github/workflows/**` | 实现 |
| `reviews/**` | 校验 |
| `DECISIONS.md`（待裁断区，追加条目） | 实现、校验 |

## 通知

用 `SendMessage` 给目标 session 发一行消息，格式：`[T-<编号>] <新状态> — <一句话>`。
例：`[T-0.2] 待校验 — docs/0-map/0.2-layers.md 与图已完成，自检通过。`

收到消息后以文件状态为准；消息与文件不一致时，以文件为准并回报设计 session。

## 裁断

`DECISIONS.md` 分两个区：
- **待裁断**：实现或校验 session 追加。格式：编号、任务、争议点、双方立场、各自依据。
- **已裁断**：设计 session 填写结论与理由。已裁断事项对后续所有任务生效，相当于规范的补充。

## 提交

设计 session 在任务"通过"后执行一次 `git commit`，提交信息首行 `T-<编号>: <页面标题>`，多个任务用"；"分隔，首行不写过程说明与 D- 编号（A.5 更新日志由首行生成，读者可见），细节放正文。**只 `git add` 该任务的产出文件与对应任务卡、校验报告，禁止 `git add -A`**（工作树里常有其他任务的中间稿）。提交后必须运行 `tools/check_head_build.sh`（导出 HEAD 做 strict 构建），失败则立即补提交遗漏文件。检查通过后立即 `tools/push_main.sh`。以上步骤已封装为 `tools/merge_task.sh '<提交信息>' <文件>...`（改任务卡状态、只 add 指定文件、按暂存树重生成占位页与首页、提交、检查、推送），合并一律用它（D-023，自动推；它会核实已与 origin 同步，检查失败不得推送），推送触发 GitHub Actions 部署。其他 session 不执行 git 写操作。

## GPU 与主机内存

一台 RTX 机器、16 GB 主机内存。**任一时刻只允许一个 session 运行 Isaac Sim 训练/长进程**（2026-10-08 20:16 校验方单独跑 8192 个环境的容量检查时主机内存告急，后台任务被系统终止；当时实现方没有 Isaac Sim 进程。单个大进程就能吃满，两个并存更不行）。顺序：校验方优先；实现方的长进程等校验方发"GPU 空出"后再启动；短跑（≤ 1 分钟）启动前问一句。`num_envs ≥ 4096` 的运行先确认空闲内存 ≥ 8 GB（`free -g`）。

## 额度保护（D-024）

周额度剩余 ≤ 5% 时停止推进，等待刷新。session 自己读不到额度百分比，触发靠两条：用户告知，或任一 session 看到额度提示 / 因额度被拒。看到就立刻通知设计 session，由它广播暂停。

收到暂停后：不领新任务，不启动新的 GPU 或长时间进程；把进度写进任务卡附记或报告草稿，然后停下。恢复由用户发起。

