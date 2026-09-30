# 已退役的迁移工具

T-SITE-03 到 T-SITE-05 期间，站点同时存在 MkDocs 版（旧 `docs/`）与 Sphinx 原型（`site-sphinx/`），这两个脚本负责同步：

- `md2myst.py`：把 Material for MkDocs 语法机械转换为 MyST。
- `gen_site.py`：从 `OUTLINE.md` 生成全站页面树与占位页，并把旧 `docs/` 的正式页转换过去。

T-SITE-06（D-020）后 `site-sphinx/` 改名为 `docs/`，成为唯一站点源，页面直接用 MyST 写，这两个脚本已不再使用，其中的路径也已失效。保留在这里仅作记录；语法对照见 `docs/MIGRATION-NOTES.md`。
