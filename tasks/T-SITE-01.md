# T-SITE-01 站点骨架

状态: 待实现
优先级: P1
类型: 基础设施
依赖: 无

## 目标

建立 MkDocs Material 站点骨架，使后续页面可以直接放入并本地预览。

## 必须完成

1. `mkdocs.yml`：
   - `site_name: Isaac Academy`，`site_url: https://academy.kiloong.com`
   - 主题 `material`，语言 `zh`，启用深浅色切换、导航 tabs、目录跟随、代码复制按钮、搜索（中文分词：`plugins.search.lang: [zh, en]`，如 Material 内置分词不足则记录到附记区）
   - Markdown 扩展：`admonition`、`pymdownx.details`、`pymdownx.superfences`（含 Mermaid 自定义 fence）、`pymdownx.tabbed`、`pymdownx.highlight`、`footnotes`、`attr_list`、`md_in_html`、`toc(permalink)`
   - `nav` 按 `OUTLINE.md` 的部分划分，先只填首页与 0-map 占位
2. `docs/index.md`：首页占位，一段话说明站点定位（可从 CLAUDE.md 取），列出与 isaac.kiloong.com 的关系。
3. `requirements-docs.txt`：mkdocs、mkdocs-material 及所用插件，锁定版本。
4. `.gitignore`：`site/`、Python 缓存、虚拟环境。
5. `mkdocs build --strict` 通过；`mkdocs serve` 可本地预览。
6. 在 `docs/0-map/` 放一个含 Mermaid 图与全部 admonition 类型的 `_template-check.md`（不进 nav），用于确认渲染，校验通过后可保留作模板参考。

## 验收标准

- `mkdocs build --strict` 零警告。
- Mermaid 图、四种 admonition、代码 tabs、脚注在本地预览中渲染正常。
- 深色模式下 Mermaid 图可读。

## 自检清单

见 CONVENTIONS.md 第 6 节。

## 附记

（实现/校验 session 写）
