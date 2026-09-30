# Material for MkDocs → Sphinx + MyST 迁移笔记

原型阶段（T-SITE-03）只迁移了 3 页：`index.md`、`0-map/0.2-layers.md`、`0-map/_template-check.md`。本文记录语法对照与迁移步骤，供日后全量迁移。

## 机械转换工具

```bash
cd site-sphinx
env -u PYTHONPATH .venv/bin/python tools/md2myst.py ../docs/<路径>.md <路径>.md
```

`tools/md2myst.py` 做下表中标注"脚本"的转换，其余需手工处理。转换后必须跑：

```bash
env -u PYTHONPATH .venv/bin/sphinx-build -E -a -W --keep-going -b html . _build/html
```

`-E -a` 是全量重建。增量构建不会重新复制改动过的 `_static` 文件（实测过），改了 CSS/JS 后必须全量重建。

## 语法对照表

| Material（docs/） | MyST（site-sphinx/） | 方式 |
|---|---|---|
| `!!! note "标题"` + 4 空格缩进正文 | `:::{admonition} 标题` / `:class: note` / 正文顶格 / `:::` | 脚本 |
| `!!! abstract "学习目标"` | 同上，`:class: hint`（pydata 的 hint 为绿色，与官方站 Hint 一致） | 脚本 |
| `!!! info "前置知识"` | 同上，`:class: note` | 脚本 |
| `!!! tip` / `warning` / `danger` | 同上，class 不变 | 脚本 |
| `??? note "标题"`（可折叠） | `:::{dropdown} 标题`（sphinx-design） | 脚本 |
| `=== "Python"` 内容块（pymdownx.tabbed） | `::::{tab-set}` 包裹若干 `:::{tab-item} Python` | 脚本 |
| ` ```mermaid ` | ` ```{mermaid} `；`%%{init: …}%%` 行原样保留 | 脚本 |
| 嵌套（提示框里有 tabs 等） | 外层冒号围栏比内层多一个 `:` | 脚本自动计算 |
| YAML frontmatter（title/verified/updated/sources_checked） | 原样保留；MyST 读取为页面元数据 | 原样 |
| 脚注 `[^key]` 与 `[^key]: …` | 原样（MyST 原生支持） | 原样 |
| GFM 表格 | 原样 | 原样 |
| 相对链接 `[x](../1-env/1.1-compat-matrix.md)` | 原样；目标文件必须存在，否则 `-W` 报错 | 原样 |
| 锚点链接 `[x](page.md#中文标题)` | 原样；依赖 `conf.py` 中 `myst_heading_anchors = 3` | 原样 |
| `{ .class }` 属性（attr_list） | `{.class}`；已启用 `attrs_inline`、`attrs_block` | 手工核对 |
| `mkdocs.yml` 的 `nav` | 父页面里的 `{toctree}` 指令，`:caption:` 写部分名（如"第 0 部分 · 全景地图"） | 手工 |
| `not_in_nav`（占位页、渲染检查页） | frontmatter 加 `orphan: true` | 手工 |
| 首页 `0-map/index.md` 这类章节入口 | 原型未迁移；全量迁移时做成带 toctree 的章节页 | 手工 |

## Mermaid

- `sphinxcontrib-mermaid` 以 ES module 方式加载 Mermaid。`_static/js/mermaid-shim.mjs` 用 `<script>` 标签加载 T-SITE-02 的 UMD 构建 `mermaid.min.js`（11.17.2），再导出 `globalThis.mermaid`。不能直接 `import` UMD 文件：在 module 作用域里它的顶层 `var` 不是全局变量，最后一行会报 `Cannot read properties of undefined (reading 'mermaid')`。
- 深浅色：插件自带 MutationObserver，`<html data-theme>` 变化时用 `mermaid_dark_theme`（dark）或 `mermaid_light_theme`（neutral）重新渲染。
- 尺寸：插件样式 `max-width: 100% !important` 会把小图放大。`_static/js/mermaid-size.js` 在每次渲染后按 viewBox 宽度设置 max-width，让图保持原始尺寸。
- 图中不要用会被 Mermaid 主题覆盖的填充色；只加描边（如用户落点的橙色描边），深浅色下都可读。

## 已知差异（相对 MkDocs 版）

- 图中节点配色由 Mermaid 的 `dark`/`neutral` 主题决定，与 Material 的青绿色调不同。
- 搜索使用 Sphinx 内置中文分词（`html_search_language = "zh"`，依赖 jieba），结果列表样式与 Material 不同。
