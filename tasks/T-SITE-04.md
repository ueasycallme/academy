# T-SITE-04 视觉原型第二轮：按官方站实测数值对齐

状态: 已合并
优先级: P1（用户直接反馈；T-0.3 交校验后立即做，排在 T-0.4 之前）
类型: 基础设施（原型迭代）
依赖: T-SITE-03

## 用户反馈（原话要点）

1. 风格还是有点怪，要**全面参考 Isaac 官网风格**：文档目录宽度、章节目录宽度、正文宽度、字体、行间距、标题层级等等。
2. **默认为浅色**。

## 方法：先量后改

不要凭感觉调。用浏览器在官方站 https://docs.isaacsim.omniverse.nvidia.com/5.1.0/ 任选一个内容页（建议 Release Notes 或 Installation 页，内容类型丰富），用 `getComputedStyle` 逐项读取下列数值，与原型同一元素对照，做成表格写进附记：**元素 | 属性 | 官方站值 | 原型当前值 | 修改后值**。

## 必须对齐的项目

1. **三栏布局**：视口 1920 与 1440 两档下，左侧章节树宽度、右侧本页目录宽度、正文列宽与最大宽度、各栏内边距、顶栏高度；断点行为（何时收起右栏、何时收起左栏）。
2. **字体**：官方站的 `font-family` 栈、正文 `font-size`、`line-height`、字重；h1–h4 的 `font-size`、`font-weight`、`margin-top/bottom`、`letter-spacing`；代码字体与字号；表格字号与行高；列表间距。官方站的 NVIDIA Sans 是专有字体，**许可原因**不能用（与网络无关）；选度量接近的开源替代（Inter 或官方栈里的后备字体），中文用系统字体栈或 Noto Sans SC。**网络约束已放宽（D-015）**：站点托管在 GitHub Pages，允许从 Google Fonts 等 CDN 加载字体，不必自托管；Mermaid 等已自托管的资源保持现状即可。
3. **配色**：默认浅色。浅色模式的背景、正文色、链接色、侧栏背景、边框、代码块背景、admonition 各类型色值，全部从官方站浅色模式实测；深色模式保留可切换，色值同样实测。品牌绿 `#76B900` 的使用位置也照官方站（哪些元素用绿、哪些不用）。
4. **导航细节**：左侧章节树的层级缩进、当前页高亮样式、折叠箭头；右侧目录的标题（官方站叫什么就叫什么）、字号、当前节高亮；顶栏内元素与间距。
5. **内容元素**：admonition 的边框/图标/标题样式、代码块圆角与复制按钮、表格边框与斑马纹、脚注样式、图片与 Mermaid 图的外边距。
6. **标题层级**：确保 h1 只有页面标题、h2 为节、h3 为小节，视觉层级差与官方站一致；样板页 0.2 若有层级使用不当处在附记里指出（不改内容）。

## 验收标准

- 附记中的实测对照表覆盖上述 1–5 的关键属性，修改后值与官方站一致或差异 ≤ 5%，并说明有意保留的差异（如字体替代）。
- 默认浅色；刷新后仍为浅色（注意 pydata 主题会把上次选择存进 localStorage，验证时清一次）。
- 0.2 页浅色/深色截图各一张，与官方站同区域并排对比图放附记。
- `sphinx-build -W` 零警告。境外请求不再作为验收项（D-015）。

## 不做

- 不动 MkDocs 站；不迁移新页面；不用 NVIDIA 字体、logo、主题文件。

## 附记

（实现/校验 session 写）

### 实现附记（isaac-academy-accomplish，2026-09-30）

**当前在做**：本任务已完成。中途插入处理了 T-0.3 的退回（已重新提交）。下一步做 T-0.4。

**测量方法**：headless Chrome 通过 DevTools 协议加载页面（`/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/cdp.py`），用 `Emulation.setDeviceMetricsOverride` 固定视口，每次先清空 localStorage 再重新加载。测量脚本 `/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/measure.js` 对两边同一选择器调用 `getComputedStyle`，原始结果为 `/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/nv-*.json`、`sx*-*.json`。对照页面：官方站 5.1.0 `installation/requirements.html`，原型 `0-map/0.2-layers.html`。

**关键发现**：原型已锁定与官方站相同的 pydata-sphinx-theme 0.16.1，并在 T-SITE-03 中复制了全部色值与尺寸变量，所以三栏布局、断点、标题字号、admonition、表格、代码块在修改前就已一致（数值差为 0）。"风格有点怪"的主要来源是：默认深色、系统中文字体（圆且宽）、宽搜索框、左右栏标题的字号字重和措辞。

**实测对照表**（1920 视口、浅色；"一致"表示修改前后都与官方站相同）

| 元素 | 属性 | 官方站 | 原型（改前） | 原型（改后） |
|---|---|---|---|---|
| 页面 | 默认模式 | auto（跟随系统，无偏好时为浅色） | dark | light（按用户要求固定为浅色；清空 localStorage 后刷新仍为浅色） |
| 页面宽度 `.bd-page-width` | max-width / 左右 padding | 1408px / 16px | 一致 | 一致 |
| 顶栏 `.bd-header` | 高度 / 背景 / 阴影 | 48px / #fff / `#ccc 0 2px 4px` | 48px / 深色值 | 一致 |
| 左栏 `.bd-sidebar-primary` | 宽 / flex-basis / min-width / padding / 右边框 | 282px / 20% / 272px / 32·16·16·16 / 1px #d1d5da | 一致 | 一致 |
| 正文 `.bd-article-container` | 宽 / max-width / padding | 845px / 960px / 16px | 一致 | 一致 |
| 正文 `.bd-article` | padding-left | 32px | 一致 | 一致 |
| 右栏 `.bd-sidebar-secondary` | 宽 / flex-basis | 282px / 25% | 一致 | 一致 |
| 断点 | 1200 / 1000 / 960 / 900 视口下左栏·右栏·正文宽 | 272·272·656 / 272·隐藏·728 / 272·隐藏·688 / 隐藏·隐藏·900（出现汉堡按钮） | 一致 | 一致 |
| body | font-family | NVIDIA, Arial, Helvetica, sans-serif | 系统栈（-apple-system…PingFang SC…） | **"Inter", "Noto Sans SC", Arial, Helvetica, sans-serif**（有意差异：NVIDIA Sans 受许可限制） |
| body / p | font-size / line-height / 颜色 | 16px / 26.4px / #1a1a1a | 一致 | 一致 |
| h1 / h2 / h3 / h4 | font-size / weight | 36 / 28 / 24 / 20px，700 | 一致 | 一致 |
| 代码 | font-family | RobotoMono, SFMono-Regular, … | 系统等宽栈 | **"Roboto Mono"**（Google Fonts 开源版）+ 官方后备栈 |
| 行内代码 | 颜色 / 背景 | #004831 / #f7f7f7 | 一致（浅色） | 一致 |
| 表格 th | 下边框 | #004831（主色） | 一致 | 一致 |
| 表格斑马纹 | 奇数行 / 偶数行 | #f7f7f7 / #fff | 一致 | 一致 |
| admonition（hint） | 左边框 / 标题背景 / 阴影 | #00843f / #d6ece1 / `#ccc 0 3.2px 8px` | 一致（浅色） | 一致 |
| 正文链接 | 颜色 / 下划线 | 正文色 #1a1a1a，绿色下划线 #76b900 1px | 一致 | 一致（官方站 sphinx-design 卡片内的链接为主色 #004831，本页无卡片，所以不可比） |
| 左栏标题 | 文字 / 字号 / 字重 / 颜色 | "Table of Contents" / 19.2px / 600 / #1a1a1a | "目录" / 20px / 700 / #000 | **"Table of Contents" / 19.2px / 600 / #1a1a1a** |
| 左栏分组名 | 字重 / 颜色 | 600 / #1a1a1a | 700 / #000 | 600 / #1a1a1a |
| 左栏当前项 | 颜色 / 左侧绿条 | #004831 / inset 3px #76b900 | 一致 | 一致 |
| 右栏标题 | 文字 | "On this page" | "当前页面"（pydata 中文翻译） | **"On this page"**（覆盖 `page-toc.html` 模板） |
| 搜索 | 形态 | 34×34 图标按钮 | 163×42 输入框样式 | 34×34 图标按钮（隐藏文字与快捷键提示） |
| 页脚 | font-size | 14.4px | 16px | 14.4px |

深色模式（1920、官方站为 prefers-color-scheme: dark，原型为 localStorage mode=dark）：除字体外，所有测量项一致。与浅色一样，li 和链接两项差异来自两页选中的元素上下文不同，不是样式差异。

**有意保留的差异**
1. 字体：用 Inter / Noto Sans SC / Roboto Mono 替代 NVIDIA Sans / RobotoMono。三者均从 Google Fonts 加载（D-015 允许），已用 `document.fonts.check` 确认浅色与深色下都已加载。
2. 没有 NVIDIA logo、版本切换器、社交图标、公告横幅，站名为纯文字（许可要求；本站也没有多版本）。
3. 默认模式：官方站为 auto，本站按用户要求固定为 light。
4. 左右栏标题照官方站用英文（"Table of Contents" / "On this page"），这是按任务卡"官方站叫什么就叫什么"做的。若希望中文站用中文，只需改 `_templates/academy-toc-title.html` 与 `_templates/page-toc.html` 各一行。

**标题层级检查（0.2 页，不改内容）**：h1 只有页面标题，各节均为 h2，没有 h3，层级使用正确。可改进的一处："一张图看全栈"一节中的"逐层说明："是一个普通段落，实际起小标题作用，若改为 h3 会出现在右栏目录中。表格说明（"*表：…*"）也是斜体段落，与图注用法一致，无需改。

**截图**（1400×1100 首屏）
- 并排对比（左为官方站、右为原型）：`/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/shots/s4-compare-light.png`、`s4-compare-dark.png`
- 单张：`/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/shots/s4-sx-light.png`、`s4-sx-dark.png`、`s4-nv-light.png`、`s4-nv-dark.png`

**修改的文件**（均在 `site-sphinx/`）：`conf.py`（Google Fonts CSS、`default_mode: light`）、`_static/css/academy.css`（字体栈、左栏标题与分组名、页脚字号、搜索按钮）、`_templates/academy-toc-title.html`、新增 `_templates/page-toc.html`。未改动 MkDocs 站。

**构建**：`sphinx-build -E -a -W` 零警告；预览仍在 http://127.0.0.1:8767/。

### 校验附记（isaac-academy-examine，2026-09-30）
结论：通过。独立抽测 12 组属性（布局宽度、字号行高、标题、代码、表格、页脚、栏标题）与官方站完全一致；全新 profile 加系统深色偏好下默认仍为浅色；`-W` 构建零警告。2 条建议（英文栏标题、Google Fonts 在中国大陆的可达性）交用户决定，见 `reviews/T-SITE-04.md`。
