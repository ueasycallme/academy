# T-SITE-06 校验报告

- 校验日期：2026-09-30
- 基线：`reviews/baseline-pre-site06/`（切换前、提交 4211840 时拍的快照：124 个 .md 的 sha256、正式页清单、0.2 页 2560 截图）
- 结论：**通过**（1 条一般、1 条建议；另有 2 处设计 session 负责的文件需同步）

## 设计 session 指定的重点
| 项 | 核查 | 结果 |
|---|---|---|
| 内容零丢失（Sphinx 侧） | 新 `docs/` 的 124 个 .md 与基线 sha256 逐个比对：**0 个缺失、0 个新增**，只有 `1-env/1.4-install-51-232.md` 有变化，属于 T-1.4 从占位页转为正式页，是预期内的改动 | ✓ |
| 内容零丢失（MkDocs 侧） | 用实现方备份的旧 MkDocs `docs/`（76 个 .md）逐页执行 `tools/legacy/md2myst.py` 后，与新 `docs/` 对比：全部正式页 diff 为 0（其中 1.3 在基线之后有过改动，也已同步）。只有 3 处不同，均可解释：`index.md`（Sphinx 首页多了 toctree，正文另见问题 1）；`_template-check.md`（多了 `orphan: true`）；`0-map/index.md`（MkDocs 独有的章节导航页，由 0.1 与首页 toctree 替代） | ✓ |
| 公告条关闭按钮与 localStorage | Chrome 实测：清空 localStorage 后公告条可见（高 39px）；× 按钮为 `<button aria-label="关闭公告">`，点击后隐藏，写入 `academy-announcement-closed-<hash>=1`；刷新后仍隐藏；跳到 0.6 页也保持隐藏。键名带 hash，公告内容改变后会重新显示，设计合理 | ✓ |
| GitHub 链接 | 顶栏图标指向 `https://github.com/ueasycallme/academy`，与 D-020 中用户确认的地址一致 | ✓ |
| 2560 截图与切换前一致 | 全新 profile 在 2560×1440 下截 0.2 页，与基线逐像素比对：差异只在顶部 y=13–28 的公告条一行（`reviews/img/T-SITE-06-topstrip-before-after.png`：文字换成 D-019 披露并加了 ×）；其余区域逐像素相同 | ✓ |
| 构建 | `tools/check_head_build.sh --worktree`：构建通过（Sphinx `-W`）；脚本已改为只跑 sphinx-build | ✓ |

## 问题清单
| # | 位置 | 问题 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|---|
| 1 | `docs/index.md`"从哪里开始" | 写的是"先读 [分层依赖图](0-map/0.2-layers.md)"。T-0.1 已把 0.1 定为全站入口页，MkDocs 版首页也是经 `0-map/index.md` 指向 0.1。这句是 Sphinx 原型生成时带进来的（基线里就是如此），这次切换后成为正式首页，才显出问题 | T-0.1 任务卡"全站入口页" | 改为"先读 [0.1 Isaac 体系一页看懂](0-map/0.1-overview.md)" | 一般 |

## 建议
| # | 位置 | 意见 |
|---|---|---|
| 1 | 公告条链接 | `href="/1-env/1.2-version-decision.html"` 是以站点根目录开头的绝对路径。用自定义域名 academy.kiloong.com 部署在根目录时没问题；但如果先通过 `ueasycallme.github.io/academy/` 访问（T-SITE-07 配置自定义域名之前），链接会跳到 `ueasycallme.github.io/1-env/…` 而失效。建议改成相对路径，或在 T-SITE-07 中验证 |

## 给设计 session（设计 session 负责的文件）
- `WORKFLOW.md` L46 的文件所有权表仍列着 `mkdocs.yml`。
- `CLAUDE.md` L8 仍写"站点：MkDocs Material，部署到 Cloudflare Pages"，与 D-020（Sphinx、GitHub Pages）不符。
