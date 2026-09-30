# T-SITE-01 站点骨架

状态: 已合并
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

### 实现附记（isaac-academy-accomplish，2026-09-30）

**产出**
- `mkdocs.yml`：Material 主题，`language: zh`，深浅色切换（跟随系统 + 手动），features 含 `navigation.tabs`、`toc.follow`、`content.code.copy`、`search.suggest/highlight`；扩展按任务卡全部启用（Mermaid 自定义 fence）；`nav` = 首页 + 全景地图（`0-map/index.md` 占位）；`not_in_nav` 排除 `_template-check.md`
- `docs/index.md`：首页，站点定位 + 与 isaac.kiloong.com 的关系表
- `docs/0-map/index.md`：第 0 部分占位入口（列出 0.1–0.8）
- `docs/0-map/_template-check.md`：Mermaid、note/tip/warning/danger + abstract/info + 可折叠 details、代码 tabs、脚注
- `docs/stylesheets/extra.css`：Mermaid 居中、窄屏横向滚动
- `requirements-docs.txt`：mkdocs 1.6.1、mkdocs-material 9.7.7、pymdown-extensions 12.1、Markdown 3.10.3、Pygments 2.21.0、jieba 0.42.1（全部锁定）
- `.gitignore`：原有 `site/`、`__pycache__/`、`*.pyc`、`.venv/`、`venv/` 已满足要求，追加 `.cache/`

**本地环境**：`python3 -m venv .venv && .venv/bin/pip install -r requirements-docs.txt`，然后 `.venv/bin/mkdocs serve`。

**说明**
1. 中文分词：Material 内置 search 插件在检测到 `jieba` 时自动用 jieba 分词（见 `material/plugins/search/plugin.py`），因此把 jieba 加进 requirements；构建日志出现 jieba 加载信息，确认生效。`lang: [zh, en]` 已配置。
2. 构建时 Material 9.7.x 会打印一段 MkDocs 2.0 不兼容的提示横幅（非 warning，不影响 strict）。requirements 已把 mkdocs 锁在 1.6.1，**不要升级到 MkDocs 2.x**。
3. Mermaid 由 Material 运行时从 unpkg 加载 mermaid@11（需联网）；主题色随深浅色模式自动切换。

**自检清单**
- [x] 页面结构与模板一致，frontmatter 完整（`_template-check.md` 按页面模板写；首页与占位页为导航页，不适用学习目标等栏目）
- [x] 任务卡"必须完成"1–6 均已完成
- [x] 每条架构/版本/API 断言有来源（本任务无此类断言）
- [x] 图有说明文字，Mermaid 能在 `mkdocs serve` 中渲染：Chrome 打开 `/0-map/_template-check/`，Mermaid 容器渲染为 826×515；切到深色（slate）后仍渲染，标签色 `hsla(225,18%,86%)` 在背景 `rgb(30,33,41)` 上可读。admonition 6 个、tabs 1 组、脚注 1 条均已渲染。说明：浏览器标签页在后台，无法截图，以上结论来自 DOM 与计算样式检查
- [x] 示例代码：本任务无
- [x] 术语与术语表一致：本任务无术语
- [x] `mkdocs build --strict` 通过，零 WARNING

### 校验附记（isaac-academy-examine，2026-09-30）
结论：通过。报告见 `reviews/T-SITE-01.md`（strict 构建、干净环境复现、浅/深色 Mermaid 渲染均验证；3 条建议级意见，不阻塞）。
