# 协作协议

三个 session 在同一目录工作。**文件系统是唯一事实来源**，session 之间的消息只用于通知。

## 角色

### 设计 session（当前名 `isaac-tutor-10`，重启后可能变化，以 ListAgents 为准）
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

设计 session 在任务"通过"后执行一次 `git commit`，提交信息 `T-<编号>: <页面标题>`。**只 `git add` 该任务的产出文件与对应任务卡、校验报告，禁止 `git add -A`**（工作树里常有其他任务的中间稿）。提交后必须运行 `tools/check_head_build.sh`（导出 HEAD 做 strict 构建），失败则立即补提交遗漏文件。其他 session 不执行 git 写操作。
