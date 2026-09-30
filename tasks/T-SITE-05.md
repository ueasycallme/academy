# T-SITE-05 视觉第三轮：对齐用户指定的两个参考页

状态: 已合并
优先级: P1（用户直接反馈；T-0.4 交校验后立即做）
类型: 基础设施
依赖: T-SITE-04

## 用户反馈

用户看过第二轮后仍认为"还不行"，并给出两个参考页（其翻译站，即官方站的中文镜像，静态资源与官方站相同）：
- https://isaac.kiloong.com/zh/introduction/reference_architecture
- https://isaac.kiloong.com/zh/overview/release_notes

设计 session 用 headless Chrome（1440 宽）截了参考页与原型，逐项比较，结论：**主题的样式数值已经接近，差距主要在"页面是否像一个真实文档站"**。以下按影响大小排序，全部必做。

## 必须完成

### 0. 正文区宽度（用户在 2560×1440 屏幕上指出的最明显差距）
用户的屏幕是 2560×1440，参考页正文区明显比原型宽。原因已定位：原型只复制了 `nvidia-sphinx-theme.css` 的侧栏规则，**漏掉了参考站 `isaacsim-design.css` 里的整体宽度覆盖**：

```css
.bd-page-width { max-width: 100rem !important; }        /* pydata 默认 88rem */
.bd-article-container { max-width: none !important; }    /* pydata 默认约 60em，把正文锁窄 */
.bd-sidebar-secondary { flex: 0 0 15rem !important; width: 15rem !important; min-width: 0 !important; padding-right: 0.25rem !important; }
```

- 把这三条加进 `academy.css`，并核对 `isaacsim-design.css` 中其余影响布局的规则（grep `bd-`、`max-width`、`flex`），凡影响三栏宽度的一并对齐。
- **实测口径改为以 2560×1440 为主**，1920 与 1440 为辅：在三个宽度下分别量参考页与原型的左栏、正文、右栏像素宽度，做成表写入附记，差异 ≤ 8px。
- 正文变宽后检查：段落行长是否与参考页一致（参考页不限制行长）；Mermaid 图与表格是否随之变化；`mermaid-size.js` 的 max-width 逻辑是否仍正确。


### 1. 左侧章节树填满（最大差距）
原型的左栏只有"第 0 部分 · 全景地图 → 分层依赖图"一条，空荡是"怪"的首要来源。参考页左栏是完整的多级树：分组标题（粗体黑）、条目（灰）、当前页（绿字 + 左侧绿条）、可折叠箭头。
- 用脚本从 `OUTLINE.md` 生成**全站占位页**（MyST，标题 + 一句"待写，见 OUTLINE x.y"），按 CONVENTIONS 第 1 节目录规则命名；已有正式页（0.2/0.3/0.5/0.6）用迁移脚本转 MyST 放进去。
- `toctree` 按 OUTLINE 的部分分组，分组标题用 `:caption:`（如"第 0 部分 · 全景地图"），第 6 部分下再分 ①–⑦ 子组。
- 左栏标题文字用 **"目录"**（与参考页一致）；右栏保持 **"On this page"**（参考页即如此）。
- 对照参考页核对：分组标题字重/字号/间距、条目字号/颜色、当前页高亮样式、缩进、箭头。

### 2. 顶栏身份
参考页顶栏：logo + "Isaac Sim 文档"（中等字重，非粗体）+ 小号版本号"6.1.0"；右侧：搜索、主题切换、一排社交图标。原型只有粗体"Isaac Academy"。
- 做一个**自制**站点标识（简单 SVG，例如绿色几何图形 + "IA"，不得使用 NVIDIA logo），放在标题左侧，尺寸对齐参考页 logo 高度。
- 标题改为"Isaac Academy"（字重与参考页一致）+ 小号灰字副标"主线 Isaac Sim 5.1.0 · Isaac Lab 2.3.2"（对应参考页的版本号位置）。
- 右侧：搜索、主题切换、GitHub 图标（链接留空或指向仓库，仓库地址待用户提供）。

### 3. 页首形态（内容模板与主题的配合）
参考页正文以 h1 + 引导段落开始；原型 h1 下面紧跟两个大块彩色 admonition（学习目标、前置知识），像讲义不像文档。
- 把"学习目标"改成参考页 `isaacsim-section-lead` 风格的**引导块**：无彩色标题栏，左侧细绿线，灰色小字标题"学习目标"，内容为列表；"前置知识"压缩为引导块底部一行"前置：链接、链接"。用 CSS 实现（MyST 侧仍用 admonition 语法，只改样式），这样已有页面不用改内容。
- 把方案写进附记，设计 session 会据此更新 CONVENTIONS 页面模板说明。

### 4. admonition 与内容元素对齐参考站
在翻译站找一个含 note/warning/tip 的页面（如 `/zh/installation/requirements` 或安装页），实测其 admonition 的边框、背景、标题样式、图标，改原型的 note/tip/warning/danger 与之一致。代码块、行内代码（参考页行内代码为浅灰底、深色字、细边框）、列表间距、表格样式同样实测对齐。

### 5. Mermaid 图的观感
参考站的图是精修图片；原型 Mermaid 默认样式（灰底方框、默认字体）显得粗糙。用 mermaid `themeVariables` 统一：节点白底、细灰边、圆角、字体与正文一致、强调用品牌绿；连线深灰细线。深浅色各一套变量。

### 6. 页面底部
补 pydata 的上一页/下一页按钮，样式对齐参考页（若参考页有）。可选：顶栏公告条（`announcement`）显示"主线版本 5.1.0 + 2.3.2；3.0 专栏基于 EA"，样式对齐参考站 `bd-header-announcement`。

## 验收标准

- 2560、1920、1440 宽下，原型 0.2 页与参考页 `reference_architecture` 并排截图（2560 为主），附记中逐项说明上述 6 点的对齐情况。
- 左栏为完整的多级目录树，当前页高亮与参考页一致。
- `sphinx-build -W` 零警告（占位页数量约 110，确保 toctree 无孤儿警告）。
- 不使用 NVIDIA logo、字体、主题文件。

## 附记

（实现/校验 session 写）

### 实现附记（isaac-academy-accomplish，2026-09-30）

**当前在做**：本任务已完成。T-0.4 在待校验；接下来按顺序做 T-0.1。

**测量方法**：同 T-SITE-04（`/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/cdp.py`，headless Chrome + DevTools 协议，每次先清空 localStorage）。参考页为 isaac.kiloong.com/zh 的 `introduction/reference_architecture`、`overview/release_notes`、`installation/requirements`、`installation/install_workstation`；原型页为 `0-map/0.2-layers`、`0-map/_template-check`、`0-map/0.3-lineage`。

**0. 宽度（最优先项）**：按卡片加了三条 CSS：`.bd-page-width{max-width:100rem}`、`.bd-article-container{max-width:none}`、`.bd-sidebar-secondary{flex:0 0 15rem;width:15rem;min-width:15rem}`。第三条额外加 `min-width`，是因为 T-SITE-03 从官方站抄来的 `min-width: var(--pst-sidebar-secondary)`（17rem）会把右栏撑到 272px。修改后三档实测完全一致：

| 视口 | 页面宽 @x | 左栏 | 正文容器 | 正文 | 右栏 | 顶栏高 |
|---|---|---|---|---|---|---|
| 2560 参考 | 1600@480 | 320 | 1040 | 1008 | 240 | 48 |
| 2560 原型（改前） | 1408@576 | 282 | 845 | 813 | 282 | 48 |
| 2560 原型（改后） | 1600@480 | 320 | 1040 | 1008 | 240 | 48 |
| 1920 参考 | 1600@160 | 320 | 1040 | 1008 | 240 | 48 |
| 1920 原型（改后） | 1600@160 | 320 | 1040 | 1008 | 240 | 48 |
| 1440 参考 | 1440@0 | 288 | 912 | 880 | 240 | 48 |
| 1440 原型（改后） | 1440@0 | 288 | 912 | 880 | 240 | 48 |

（2560 改前一行是按 88rem 上限推算的，其余均为实测。）T-SITE-04 在 1440 / 1920 量到"一致"，是因为当时对照的是 docs.isaacsim 官方站本身，它的 pydata 默认宽度与原型相同；翻译站另有 isaacsim-design.css 放宽了宽度。

**1. 左栏章节树**：新增 `tools/gen_site.py`，从 OUTLINE.md 生成 114 页：5 个正式页（0.2 / 0.3 / 0.4 / 0.5 / 0.6，用 md2myst 转换）和 109 个占位页（"待写，见 OUTLINE x.y"）。目录与 slug 按 CONVENTIONS 第 1 节，并与 docs/ 已有 slug 一致。首页为每个部分生成一个带 `:caption:` 的 toctree；第 6 部分下的 ①–⑦ 是子索引页，在左栏可折叠。左栏标题改回"目录"，右栏保持 "On this page"。实测分组标题（14.4px / 600 / #1a1a1a / 下边距 8px）、条目（14.4px / #666 / 左内边距 10.4px）、当前页（#004831 / 600 / 3px 绿条）、折叠箭头（30px）均与参考页一致。`sphinx-build -W` 零警告，没有孤儿页警告。

**2. 顶栏**：
- 自制标识 `_static/img/academy-logo.svg`：绿色圆角方块加三层台阶，呼应"分层"，不含任何 NVIDIA 图形。显示高 28px。参考页 logo 图高 48px 含大量留白，可见图形约 22px。
- 站名 20px / 700。实测参考页标题为 20px / **700**，卡片写的是"中等字重"，这里以实测为准。
- 副标"主线 Isaac Sim 5.1.0 · Isaac Lab 2.3.2"，14px / 400 / 次要色（参考页版本号为 14px / 400），窄屏隐藏。
- 右侧依次为搜索、主题切换、GitHub 图标。GitHub 链接暂指向 github.com，等用户提供仓库地址后改 `conf.py` 中 `icon_links` 一行。
- 加了公告条，文字为"主线版本：…；3.0 前沿专栏基于 Isaac Lab 3.0.0-EA，内容可能变动"。

**3. 页首引导块（供设计 session 更新 CONVENTIONS 页面模板）**：
- 方案：Markdown 源不变，仍写 `!!! abstract "学习目标"` 和 `!!! info "前置知识"`。转换脚本把它们映射为 `:class: lead-goals` 和 `:class: lead-prereq`，由 academy.css 渲染为一个引导块：无彩色标题栏、无阴影与底色，左侧 2px 品牌绿细线，标题为 0.8rem 灰色小字，正文 0.98rem / 行高 1.7 / 次要色（参考站 `.isaacsim-section-lead` 的实测值），最大宽度 760px。"前置知识"压成紧贴其下的一行："前置知识：链接、链接"，列表项以顿号连接。
- 对 CONVENTIONS 的建议：页面模板不用改写法，只需在说明里注明"学习目标 / 前置知识在站点上显示为页首引导块，不是彩色提示框"。另外，学习目标的第一行"读完本页你能："在引导块里略显多余，可以考虑从模板中去掉（这涉及内容，未改）。

**4. 内容元素**：实测以下各项与参考站完全一致，未改动（同一 pydata 0.16.1，加 T-SITE-03 复制的变量）：
- note / warning / hint 的标题底色、左边框 3px、阴影、标题字号字重
- 行内代码：14px、#004831、#f7f7f7 底、1px #d1d5da 边、4px 圆角
- 表格：th 下边框 #004831，td 下边框 #f7f7f7，8px 内边距
- 列表：ul 左内边距 32px，行高 26.4px

参考站没有 tip / danger 实例，原型沿用 pydata 默认值（与官方主题一致）。

**5. Mermaid**：没有改 Mermaid 的 themeVariables，而是在 academy.css 中用 CSS 覆盖 SVG 元素，直接引用 pydata 的颜色变量，因此深浅色自动跟随，不需要两套变量，也不必在切换主题时维护两份配置：
- 节点：背景色填充、1px 边框色描边、6px 圆角
- 子图：surface 底色、8px 圆角
- 文字：正文色、正文字体
- 连线与箭头：次要色、1px
- 时序图：loop 框线用品牌绿，Note 为绿边
- 用户节点：保留橙色 3px 描边
- 边标签：去掉背景块（修正了深色下"适配层"一类标签的灰底）

0.3 的 gantt 和 0.4 的 quadrant 图自带 `%%{init}%%`，不受影响。

**6. 页面底部**：pydata 的上一页 / 下一页已启用，实测标题 17.6px / 600、副标 16px / #666，与参考页一致。

**截图**（参考页在上、原型在下）：`/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/c756610b-1639-4fa9-865f-f63a038ce7ed/scratchpad/shots/s5-compare-2560.png`、`s5-compare-1920.png`、`s5-compare-1440.png`；深色 `s5-sx-1920-dark.png`；顶栏特写 `s5-hdr.png`。

**修改与新增的文件**（均在 `site-sphinx/`）：`conf.py`、`_static/css/academy.css`、`_static/img/academy-logo.svg`、`_templates/academy-subtitle.html`、`_templates/academy-toc-title.html`、`tools/gen_site.py`（新增）、`tools/md2myst.py`（类名映射）、`MIGRATION-NOTES.md`、`index.md`，以及生成的 114 个页面与 7 个子索引页。未改动 MkDocs 站与 docs/。

**预览**：http://127.0.0.1:8767/（默认浅色）。

### 校验附记（isaac-academy-examine，2026-09-30）
结论：通过。2490 视口下 6 项宽度与参考页完全相同；左栏 121 个链接按部分分组，当前页高亮；`-W` 全量构建零警告；五个正式页与 docs/ 同步（diff 为 0）；0.2、0.6 深浅色截图目检通过。3 条建议（GitHub 链接为占位、标识颜色与 NVIDIA 绿、引导块第一行）见 `reviews/T-SITE-05.md`。
