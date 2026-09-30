# T-SITE-06 正式切换到 Sphinx

状态: 待实现
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
