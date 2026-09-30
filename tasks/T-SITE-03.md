# T-SITE-03 视觉风格原型：对齐 Isaac Sim 官方文档站

状态: 已合并
优先级: P1（插队：T-0.2b 之后、T-0.6 之前）
类型: 基础设施（原型，用户看过后再决定是否切换）
依赖: T-0.2b

## 背景

用户看过 MkDocs Material 版样板页后认为界面不好看，希望参考 Isaac Sim 官方文档站（https://docs.isaacsim.omniverse.nvidia.com/5.1.0/ ，用户自己的翻译站 https://isaac.kiloong.com/zh/ 是同一风格）。该站基于 Sphinx + `nvidia-sphinx-theme`（其底座是 `pydata-sphinx-theme`）。

**`nvidia-sphinx-theme` 不能用**：其 PyPI 许可为 NVIDIA License Agreement，仅允许"in connection with NVIDIA's products and services"使用，且禁止衍生；本站是第三方站点。同样**不得使用 NVIDIA 的 logo、字体和商标素材**。

因此本任务用 **Sphinx + MyST-Parser + `pydata-sphinx-theme`（BSD-3）** 复现同样的版式与观感，配色与细节用自定义 CSS 逼近。这是原型，与现有 MkDocs 站并存，用户对比后再决定切换。

## 必须完成

1. 新建 `site-sphinx/`（与 `docs/` 平级，原型阶段独立目录，不动 MkDocs 配置）：`conf.py`、`requirements-sphinx.txt`（锁版本：sphinx、myst-parser、pydata-sphinx-theme、sphinx-design、sphinxcontrib-mermaid、sphinx-copybutton、jieba）。
2. **版式对齐官方站**（对照 https://docs.isaacsim.omniverse.nvidia.com/5.1.0/ 逐项）：
   - 顶部导航栏：左侧站名"Isaac Academy"文字 logo（不用任何 NVIDIA 素材），右侧搜索框、深浅色切换、GitHub 图标可留空
   - 左侧为可折叠的章节树（按 OUTLINE 部分分组），右侧为"本页目录"
   - 默认深色，可切换浅色；**配色采用 NVIDIA 色彩体系**（用户明确要求）：品牌绿 `#76B900` 为主色，深色模式背景、面板、边框、链接、代码块、admonition 的色值直接读官方站的 CSS 变量（`_static/styles/nvidia-sphinx-theme.css`、`custom.css`），逐项记录来源；浅色模式同理。只取色值，不复制主题文件
   - 页脚固定一行声明："本站为第三方学习站点，与 NVIDIA 无隶属关系；Isaac Sim、Isaac Lab、Omniverse 为 NVIDIA 的商标。"（避免被误认为官方站）
   - 正文宽度、行高、标题字号逼近官方站；中文用系统字体栈（同 T-SITE-02）
   - 页脚只放本站信息
3. **内容迁移（只迁 3 页做原型）**：`index.md`、`0-map/0.2-layers.md`、`_template-check.md` 转为 MyST 语法：`!!! abstract` → ` ```{admonition} 学习目标\n:class: abstract` 等；pymdownx tabs → sphinx-design `tab-set`；脚注、attr_list 锚点、frontmatter 按 MyST 方式。写一份 `site-sphinx/MIGRATION-NOTES.md` 记录 Material → MyST 的语法对照表，供日后全量迁移用。
4. **Mermaid**：`sphinxcontrib-mermaid` 使用本地 `mermaid.min.js`（复用 T-SITE-02 的文件），深浅色切换时图的主题要跟随（可用 mermaid 的 `theme: base` + CSS 变量，或切换时重渲染；记录方案）。
5. **无境外请求**：pydata-sphinx-theme 自带 FontAwesome 与 CSS，确认构建产物不引用 fonts.googleapis、unpkg、jsdelivr 等；用 T-SITE-02 同样的方法验证并写入附记。
6. **中文搜索**：`html_search_language = "zh"`（依赖 jieba），验证能搜到中文词。
7. `sphinx-build -W -b html` 零警告；在 **127.0.0.1:8767** 提供预览（与 MkDocs 的 8765/8766 并存），把 0.2 页在深浅色下的截图各一张放到附记（路径），并与官方站同区域截图并排对比，列出仍有明显差异的地方。

## 不做

- 不删除、不修改 MkDocs 配置与 `docs/`。
- 不迁移其他页面。
- 不使用 nvidia-sphinx-theme、NVIDIA logo/字体/图标。

## 验收标准

- 用户打开 8767 端口能直观感受"像 Isaac Sim 文档站"。
- 构建零警告、无境外请求、中文搜索可用、Mermaid 深浅色可读。
- MIGRATION-NOTES.md 能指导把现有 Material 页面机械转换为 MyST。

## 附记

（实现/校验 session 写）

**进度（isaac-academy-accomplish，2026-09-30）**：已开始后暂停，当前在收尾 T-0.6，T-0.6 转为"待校验"后回到本任务。已完成的部分：建了 `site-sphinx/.venv`，查明官方站用 pydata-sphinx-theme 0.16.1，读取了 `nvidia-sphinx-theme.css` 的色值变量。`site-sphinx/` 下还没有写任何站点文件。

### 实现附记（isaac-academy-accomplish，2026-09-30）

**当前在做**：本任务已完成。下一步处理被退回的 T-0.6。

**预览**：`http://127.0.0.1:8767/`（`python3 -m http.server` 服务 `site-sphinx/_build/html`，由本 session 在后台运行）。重建命令：`env -u PYTHONPATH site-sphinx/.venv/bin/sphinx-build -E -a -W --keep-going -b html site-sphinx site-sphinx/_build/html`。必须带 `-E -a`：增量构建不会重新复制改动过的 `_static` 文件（实测过）。

**产出**（均在 `site-sphinx/` 下；没有改动 `docs/` 与 `mkdocs.yml`）
- `conf.py`、`requirements-sphinx.txt`（Sphinx 8.1.3、myst-parser 4.0.1、pydata-sphinx-theme 0.16.1、sphinx-design 0.6.1、sphinxcontrib-mermaid 2.1.1、sphinx-copybutton 0.5.2、jieba 0.42.1 等，全部锁定）
- `_static/css/academy.css`：配色、字号与尺寸，每项都用 `[nv:…]` 注释标出来源变量或选择器
- `_static/js/mermaid-shim.mjs`（复用 T-SITE-02 的 mermaid.min.js）、`_static/js/mermaid-size.js`、`_static/js/mermaid.min.js` 与 LICENSE
- `_templates/academy-footer.html`（第三方声明）、`academy-toc-title.html`（左栏"目录"标题）、`academy-nav.html`（全站章节树）
- 迁移的页面：`index.md`、`0-map/0.2-layers.md`、`0-map/_template-check.md`；另有 9 个 orphan 占位页（从 docs 复制，加 `orphan: true`），用来让 0.2 的站内链接在 `-W` 下可解析
- `tools/md2myst.py`（机械转换脚本）、`MIGRATION-NOTES.md`（语法对照表与步骤）
- 根目录 `.gitignore` 增加 `site-sphinx/_build/`；`site-sphinx/.venv/` 已被原有的 `.venv/` 规则覆盖

**配色来源**：从官方站 `_static/styles/nvidia-sphinx-theme.css?v=df3ac72c` 读取（2026-09-30）。该文件头部声明为 NVIDIA 专有许可，所以只取数值，没有复制文件；全部字体（NVIDIA Sans、RobotoMono，托管在 images.nvidia.com）一律不用。
- 浅色：`--nv-color-green #76b900`、`--nv-color-green-2 #004831`、background `#fff`、on-background（顶栏）`#fff`、shadow `#ccc`、heading `#000`、text-base `#1a1a1a`、text-muted `#666`、surface `#f7f7f7`、on-surface `#333`、primary = green-2、link = text-base（靠绿色下划线区分）、inline-code = primary、secondary-bg / accent = green、table-row-hover = green
- 深色：background `#111`、on-background（顶栏）`#000`、shadow `#000`、heading `#fff`、text-base `#eee`、text-muted `#999`、surface `#1a1a1a`、on-surface `#ddd`、primary = green（`#76b900`）、secondary-bg / table-row-hover = green-2
- 字号与尺寸：h1–h6 为 2.25 / 1.75 / 1.5 / 1.25 / 1.125 / 1 rem，标题字重 700，顶栏高 3rem；左栏 flex-basis 20%，右栏 25%；当前导航项左侧加 3px 绿条；正文链接用绿色下划线
- `custom.css?v=767de534` 只含 rubric 标题、表格工具类与文字方向类，没有配色，未取用
- admonition、代码块、表格斑马纹：官方站没有覆盖，使用 pydata-sphinx-theme 默认值。从官方页面的 `DOCUMENTATION_OPTIONS.theme_version = '0.16.1'` 确认版本，本站锁定同一版本，所以这些颜色自动一致
- 默认深色：pydata 0.16 用 `html_context = {"default_mode": "dark"}` 设置（放在 theme options 里会报 unsupported option）

**Mermaid 方案**：见 MIGRATION-NOTES 的 Mermaid 一节。要点：
1. UMD 文件不能直接作为 module import，已改为 shim 用 `<script>` 加载。
2. 深浅色切换时，插件自带的 observer 会重渲染，dark 与 neutral 两个主题之间切换。实测节点填充色：深色 `rgb(31,32,32)`，浅色 `rgb(236,236,255)`（改 neutral 前测得）。
3. 插件样式会把小图放大（最初 0.2 图 1 显示高 1107px），由 `mermaid-size.js` 修正为原始尺寸：0.2 两张图为 371×549、492×558，切换深浅色后尺寸不变。

**无境外请求**：构建产物 grep 结果中，`fonts.googleapis`、`fonts.gstatic`、`unpkg`、`jsdelivr`、`cdnjs` 均为 0；HTML 里的外部 URL 只有正文超链接；`_static` JS 中出现的外部域名（clipboardjs.com、popper.js.org 等）都在许可或注释字符串里，不是请求。Chrome 用 Performance API 检查 0.2 页的全部资源请求，host 只有 `127.0.0.1:8767`。FontAwesome 由 pydata 从本地 `_static/vendor` 加载。

**中文搜索**：在 search.html 上实测（每次重新加载页面后搜一个词）：
- "脚注" → 渲染检查页、渲染检查页 > 脚注
- "版本绑定" → 分层依赖图 > 版本绑定链
- "量子纠缠" → 无结果（对照组）

**构建**：`sphinx-build -E -a -W --keep-going` 零警告。

**截图**（headless Chrome；浅色通过同源临时页写入 pydata 的 localStorage `mode=light` 后跳转，截完即删除该临时页）
- 0.2 页：`/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/shots/sx-0.2-dark.png`、`sx-0.2-light.png`；整页 `sx-0.2-dark-full.png`、`sx-0.2-light-full.png`
- 与官方站 Requirements 页首屏的并排对比（左为官方站、右为原型）：`/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/shots/compare-dark.png`、`compare-light.png`
- 渲染检查页：`/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/shots/sx-check-dark.png`、`sx-check-light.png`（6 种提示框、dropdown、tabs、脚注、Mermaid 均已目检）
- 截图在本 session 的 scratchpad，是临时目录

**与官方站仍有明显差异的地方**（按对比截图逐项列出）
1. 没有 NVIDIA logo（按要求不用），站名是纯文字；官方站 logo 右侧还有文档标题与版本下拉，原型都没有（本站暂无多版本）。
2. 顶栏右侧：官方站有 Discord、GitHub、Twitter 等社交图标，原型只有搜索与深浅色切换。
3. 字体：官方站用 NVIDIA Sans，西文更窄更方；原型用系统字体栈，中文为 Noto Sans CJK，整体更圆、更宽。
4. 左栏：官方站的"Table of Contents"标题与分组名更小，分组之间留白更大；原型的"目录"标题略大。原型目前只有一个分组、一页，树形折叠效果要等页面增多后才能对比。
5. 官方站顶部有版本公告横幅（本站不需要）。
6. Mermaid 图的配色（dark / neutral 主题）是灰阶，与官方站无可比对象；与 MkDocs 版的青绿节点不同。
7. 右栏标题：官方站为"On this page"，原型为"当前页面"（pydata 的中文翻译）。

**自检清单**
- [x] 任务卡"必须完成"1–7 均已完成
- [x] 配色逐项记录来源，只取色值；未使用 nvidia-sphinx-theme、NVIDIA logo、字体、图标；页脚第三方声明原文照录
- [x] 图有说明文字，Mermaid 渲染正常，已截图目检（深浅色，路径见上）
- [x] 示例代码：无
- [x] `sphinx-build -W` 零警告
- [x] 未改动 `docs/` 与 `mkdocs.yml`


### 校验附记（isaac-academy-examine，2026-09-30）
结论：通过。设计 session 指定的 5 个重点逐项验证：①无 NVIDIA 主题、字体、logo；②屏蔽外网下没有外部请求；③中文单词搜索可用，但连写的多词短语（如"导入路径"）返回 0 条，原因是 Sphinx 前端 `splitQuery` 不做中文分词（一般）；④Mermaid 深浅色截图与实时切换均正常；⑤用 MIGRATION-NOTES 与 md2myst 实际迁移未迁过的 0.6 页，`-W` 零警告。报告见 `reviews/T-SITE-03.md`。
