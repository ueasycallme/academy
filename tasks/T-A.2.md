# T-A.2 常见错误信息索引

状态: 已合并
优先级: P1
类型: 参考页
依赖: T-1.9（安装排障已有 ~20 条，本页不重复其内容，只收录索引行并链接）、第 3–7 部分已上线页面
产出: `docs/appendix/A.2-error-index.md`（替换占位页）
公共要求: 见 `tasks/T-A-common.md`

## 必须覆盖

1. **索引表**：按错误信息原文（可 grep 的关键片段，放行内代码）排序，列：错误片段 → 阶段（安装 / 启动 / 资产导入 / 场景 / 训练 / 回放）→ 一句话原因 → 本站哪页讲（锚点）。来源三处：① 1.9 的全部条目（只做索引行）；② 第 2–7 部分各页"常见坑"里带错误信息的条目；③ `reviews/` 与 `tasks/*-notes.md` 里本站实测遇到过、正文已写的错误（例如 ValueError 关节默认位置越界、mimic 约束、NaN、Hydra 类型拒绝、`GetCompositionErrors` 缺失、退出码 0）。用 grep 把站内所有 "Error|错误|报错|ValueError|RuntimeError" 的出现处列一遍再筛，附记写明筛掉了什么。
2. **没有错误信息的"症状"**单独一小节（卡死、NaN、机器人飞走、显存爆、画面黑），每条指向讲它的页面（5.8、7.3、6.1.x、1.9）。
3. **怎么用这一页**：先 grep 自己的日志取关键片段，再在本页 Ctrl+F；指向 7.3"日志在哪"。
4. 维护规则：新页面写"常见坑"时若含错误信息，同时在本页加一行（写进 CONVENTIONS 由设计 session 做，本页只说明）。

## 验收标准

每行的站内锚点可达且目标处确实讲了该错误；1.9 的条目全部有索引行；条目 ≥ 30 行；校验方抽 10 行核原文片段是否与来源一致。

## 附记

### 实现（isaac-academy-accomplish，2026-10-09）

**修改**
- 写了 `docs/appendix/A.2-error-index.md`；
- 顺带修改已合并的 5.6：在"历史帧"一节的 Hydra 一句里补上报错原文 `ValueError: [Config]: Incorrect type under namespace: /observations/policy/history_length`。原文取自本站实测日志（T-5.6 的 m71/obs56 运行），原先只写了"以类型不符拒绝"，补上后 A.2 的这一行在正文里有出处；
- 重跑了 gen_placeholders。

**表 1 的来源与筛选**：
- 用 grep 在第 1–8 部分正文里搜行内代码中的 `Error|Exception|ERROR|Failed|Warning|not found|No module|Can't|Unresolved|overflow|out of memory|Invalid`，再加上 `Incorrect type`、`No runs present`、`Multiple matches` 单独搜，共约 75 处；
- **筛掉的**：
  - 奖励函数名、指标名中的 "error"，如 `position_command_error`、`Metrics/ee_pose/position_error`、`tcp_position_error`、`error_pos_2d`；
  - 脚注里只提到异常类名、没有报错原文的（如单独的 `RuntimeError`、`AttributeError`）；
  - 同一报错在多页重复出现的，合并为一行，"详见"列出多页。
- **1.9 的全部 18 条**：有报错原文的 13 条进表 1，链接到该条小节；没有报错原文的 5 条（ROS 2 冲突、首次启动很久、下载扩展失败、驱动过旧、close 卡住 / kill 不掉）进表 2"症状"。18 条全部有索引行。
- 表 1 共 **32 行**（≥ 30），按片段字母顺序排列。行由 scratchpad 里的 gen_a2.py 生成，锚点用 myst_parser 的 `default_slugify` 计算，与站点一致。

**锚点核验**：
- 表 1、表 2 的所有站内链接都用同一个 slug 函数与目标页的标题逐一比对，0 处不匹配；-W 构建通过；
- 另做了一次内容核验：除 1.9 的行（报错就是小节标题）外，每行的错误片段都能在所链接的小节正文里找到；第一轮有 6 行没对上，都已改为链接到真正讲它的小节，或在正文补上原文（即上面的 5.6）。

**自查**
- [x] 1 索引表 32 行，四列：片段、阶段、原因、详见。
- [x] 2 症状表 12 行，分别指向 1.9、3.2、3.5、5.8、6.1.2、6.1.5、6.5.2、6.6.1、7.3、8.4。
- [x] 3 怎么用这一页：先 grep 日志、再 Ctrl+F；回链 7.3"日志在哪"。
- [x] 4 维护规则一段（写进 CONVENTIONS 由设计做，本页只说明）。
- [x] 按附录公共要求：没有学习目标三节；没有新术语。
- [x] 篇幅（D-027）：含表 1341。
- [x] `check_head_build.sh --worktree` 通过。

### 校验附记（isaac-academy-examine，2026-10-09）

**退回**，见 `reviews/T-A.2.md`。47 个链接都能解析到小节，32 个片段都能在所链接的小节里找到；1.9 的 18 条全覆盖；抽查 12 行原文，11 行一致。问题 1（低）：`Accessed invalid expired prim` 与真实报错不逐字一致（USD 会在 expired 与 prim 之间插入类型名），2.5 L173 写法相同。5.6 的改动与复跑日志一致。

**按 reviews/T-A.2.md 修改（2026-10-09）**：表 1 的 `Accessed invalid expired prim` 改为 `Accessed invalid expired`。USD 会在 expired 与 prim 之间插入类型名，真实报错是 `Accessed invalid expired 'Xform' prim </Robot>`，与本站 2.3 / 2.5 实测时的日志一致。2.5 坑二同步改为完整原文 `RuntimeError: Accessed invalid expired 'Xform' prim </Robot>`（2.5 已合并，这是对已合并页面的修改）。表 1 由 gen_a2.py 重新生成，仍为 32 行；-W 构建通过。

### 校验附记（第二轮，isaac-academy-examine，2026-10-09）

**通过**。片段与 2.5 原文都已改正；链接与片段核对复跑全部通过。
