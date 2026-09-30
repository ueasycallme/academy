# T-SITE-06 正式切换到 Sphinx

状态: 已合并
优先级: P1（T-1.4 交校验后立即做，排在 T-ENV-01、T-1.9 之前）
类型: 基础设施
依赖: T-SITE-05；T-1.4 已交校验

## 目标

`site-sphinx/` 成为唯一站点源，MkDocs 退役；仓库结构、规范、检查脚本、README 全部改到 Sphinx 上。切换后新页面直接用 MyST 写，不再有转换步骤。

## 必须完成

1. **目录重组**：
   - 旧 `docs/`（MkDocs 源）删除；`site-sphinx/` 重命名为 `docs/`（Sphinx 源，含 `conf.py`、`_static`、`_templates`、各部分目录）。`examples/` 不动。
   - 删除 `mkdocs.yml`、`requirements-docs.txt`、`.venv`（MkDocs 的），保留/重命名 `requirements-sphinx.txt` → `requirements-docs.txt`；`.gitignore` 更新（`docs/_build/`、`.venv/`）。
   - 迁移最后一批仍只在旧 `docs/` 的正式内容：1.4 草稿（若 T-1.4 尚未通过，迁移后在新目录继续修改）、以及任何 diff 不为 0 的页面；迁移后 `tools/md2myst.py`、`tools/gen_site.py` 移到 `tools/legacy/` 并在 README 注明已退役（占位页已生成，不再需要）。
2. **CONVENTIONS 页面模板改为 MyST**：把 `MIGRATION-NOTES.md` 的对照表整理成一份 MyST 版页面模板（frontmatter、学习目标/前置知识 admonition 的 MyST 写法、脚注、锚点 `(term-xxx)=`、Mermaid fence、tab-set），写在附记里，设计 session 据此改 CONVENTIONS 第 2 节。
3. **公告条关闭按钮**（用户要求）：公告条右侧加 ×，点击后隐藏并写 localStorage（键含公告文案的 hash，文案变了会重新显示）；无 JS 时公告条仍显示。
4. **顶栏 GitHub 图标**指向 https://github.com/ueasycallme/academy ；`conf.py` 里 `html_context`/theme options 的 repo 信息按 pydata 规范填写。
5. **检查脚本**：`tools/check_head_build.sh` 只跑 `sphinx-build -W`；README 的本地预览改为 `sphinx-build` + `python -m http.server` 或 `sphinx-autobuild`（如加依赖需锁版本）。
6. **验证**：`tools/check_head_build.sh` 通过；8767 预览正常；2560 宽截图与切换前一致；全站内部链接（`sphinx-build -b linkcheck` 只查内部或跳过外链）无断链。

## 不做

- 不改页面内容；不做部署（T-SITE-07）；不改搜索（T-SITE-08）。

## 附记

（实现/校验 session 写）

### 实现附记（isaac-academy-accomplish，2026-09-30）

**当前在做**：本任务已完成。接下来做 T-ENV-01（直接用 MyST 写）。

**1. 目录重组**（全部用普通文件操作，没有执行 git 写操作；删除与重命名由设计 session 提交）
- 旧 `docs/`（MkDocs 源）已移出工作区，备份在 `/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/pre-site06-backup/docs-mkdocs/`（同时仍在 git 历史里）；`site-sphinx/` 重命名为 `docs/`。
- 迁移前的核对：`site-sphinx` 已包含旧 `docs/` 的全部页面。T-1.4 最后一次修改后已重跑 gen_site.py 同步，0.1–0.8、1.1–1.4 共 12 个正式页一致。旧 `docs/` 独有的只有 `0-map/index.md`（MkDocs 的章节导航页），它在 Sphinx 中由 0.1 与首页 toctree 承担，没有迁移。旧 `docs/` 中还有 git 未追踪的 19 个占位页（T-0.8 生成），Sphinx 侧已有同名页。
- 已删除：`mkdocs.yml`、MkDocs 的 `requirements-docs.txt`（备份见上）、根目录 `.venv`（MkDocs）与 `site/`、`site-sphinx/.venv`、`site-sphinx/_build`。
- `site-sphinx/requirements-sphinx.txt` 移为根目录 `requirements-docs.txt`，文件头说明已更新；根目录 `.venv` 按它重建（Sphinx 8.1.3 / myst-parser 4.0.1 / pydata-sphinx-theme 0.16.1 / sphinxcontrib-mermaid 2.1.1 / jieba 0.42.1）。
- `.gitignore`：`docs/_build/`、`__pycache__/`、`*.pyc`、`.venv/`、`venv/`、`.cache/`（去掉了 `site/`、`site-sphinx/_build/`）。
- `md2myst.py`、`gen_site.py` 移到 `tools/legacy/`，新增 `tools/legacy/README.md` 说明已退役、路径已失效。`docs/MIGRATION-NOTES.md` 保留（在 `exclude_patterns` 中，不参与构建）。
- `docs/conf.py`：docstring 改为正式站点说明；`exclude_patterns` 改为 `["_build", "MIGRATION-NOTES.md"]`。

**2. MyST 页面模板**（供设计 session 更新 CONVENTIONS 第 2 节）

````markdown
---
title: <页面标题>
verified: "Isaac Sim 5.1.0 / Isaac Lab 2.3.2"   # 无代码的概念页写 "n/a"
updated: 2026-09-30
sources_checked: 2026-09-30
---

# <页面标题>

:::{admonition} 学习目标
:class: lead-goals

读完本页你能：

- …（2–4 条，动词开头）
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

## 常见误解            （概念页；实操页写"## 常见坑"）

:::{admonition} 误解一：…
:class: warning

…
:::

## 延伸阅读

- 官方文档：…
- 源码：…
- 中文翻译（中文翻译站，译自最新版 Isaac Sim 文档，与主线 5.1.0 可能有差异）：…

## 版本说明

…

[^key]: 页面名：URL（要点）
````

要点说明：
- 学习目标 / 前置知识用 `:class: lead-goals` 与 `:class: lead-prereq`，由 academy.css 渲染为页首引导块（T-SITE-05）。
- 提示框统一用 `:::{admonition} 标题` 加 `:class: note|tip|warning|danger`，冒号围栏；内部要嵌套代码块或 tab-set 时，外层冒号多一个。
- 术语表锚点：MyST 中可以直接写 `(term-xxx)=` 目标行（放在需要锚定的块之前），行内锚点写 `[**术语**]{#term-xxx}`（`attrs_inline` 只作用于 span，不作用于粗体）。0.8 目前用的是后一种。
- 占位页：frontmatter 加 `orphan: true` 并且不进 toctree；进入 toctree 的页面不要写 `orphan`。
- 脚注与 GFM 表格原生支持；`## 标题` 锚点已开启（`myst_heading_anchors = 3`）。

**3. 公告条关闭按钮**：`docs/_static/js/announcement-close.js`，并在 `conf.py` 的 `html_js_files` 中加载；样式在 academy.css 末尾。
- × 按钮位于公告条右侧。点击后隐藏公告条，并写入 localStorage，键为 `academy-announcement-closed-<公告文案的哈希>`，所以文案一改就会重新显示。
- 无 JS 或 localStorage 不可用时，公告条照常显示（按钮由脚本插入，存储读写都包在 try 里）。
- 实测（headless Chrome，1440 视口）：有按钮；点击后 `hidden=true`；写入键 `academy-announcement-closed-adktqk`；**刷新后公告条仍隐藏（display: none），按钮不再插入**。

**4. GitHub**：`icon_links` 指向 https://github.com/ueasycallme/academy；`html_context` 按 pydata 规范补充了 `github_user`、`github_repo`、`github_version`（main）、`doc_path`（docs）。没有启用 edit-this-page 按钮（不在任务范围）。

**5. 检查脚本**
- `tools/check_head_build.sh`：导出 HEAD（或加 `--worktree` 检查工作区），执行 `sphinx-build -E -a -W --keep-going`，删掉了 MkDocs 分支。退出码处理已改为先捕获返回码再判断，并做了反例测试：往副本中加一个坏链接，脚本输出 `myst.xref_missing` 警告与"构建失败"，返回 1；正常工作区返回 0。
- 新增 `tools/serve.sh`：全量构建后用 `python3 -m http.server` 预览，默认端口 8767。没有引入 sphinx-autobuild，不新增依赖。
- README 改写为 Sphinx 流程，包括目录说明与 legacy 说明。

**6. 验证**
- `tools/check_head_build.sh --worktree`：构建通过（零警告）。HEAD 模式要等设计 session 提交之后才有意义。
- 内部链接：`sphinx-build -b linkcheck -D linkcheck_ignore=^https?://` 返回 0，非忽略条目为 0。MyST 的站内链接与锚点在 html 构建时已经解析，缺失即为 `-W` 失败，上面的反例测试已证明这一点。
- **8767 端口被另一个 session 的 http.server 占用**（pid 173760，33 分钟前启动，工作目录是 `site-sphinx/_build/html`，重命名后该目录已被删除，因此它现在返回空内容）。这不是本 session 的进程，所以没有结束它，请它的所有者用 `tools/serve.sh` 重启。我用 8770 端口做了验证。
- 2560×1440 截图与 `reviews/baseline-pre-site06/pre-0.2-2560.png` 对比：布局、配色、左栏树、顶栏、引导块、正文与右栏一致。像素差异来自基线截图带有页面滚动条（内容整体左移约 7px），本次截图隐藏了滚动条，因此不是样式差异。截图：`/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/shots/s6-sx-2560.png`，并排对比 `/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/shots/s6-diff-view.png`。
- T-1.4 仍在校验中，页面现位于新 `docs/1-env/1.4-install-51-232.md`（MyST 版），后续修改在此进行。

**未做**（按任务卡"不做"）：没有改页面内容，没有做部署，没有改搜索。

### 校验附记（isaac-academy-examine，2026-09-30）
结论：通过。124 个页面与切换前基线逐个比对，零丢失（只有 T-1.4 的 1.4 有预期内的改动）；旧 MkDocs 正式页转换后与新 docs/ 全部一致；公告条关闭与记忆、GitHub 链接实测正常；2560 截图与基线相比只有公告条一行不同。一般 1 条：首页"从哪里开始"指向 0.2 而不是入口页 0.1。报告见 `reviews/T-SITE-06.md`。
