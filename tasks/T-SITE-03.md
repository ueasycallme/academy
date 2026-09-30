# T-SITE-03 视觉风格原型：对齐 Isaac Sim 官方文档站

状态: 待实现
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
   - 默认深色，可切换浅色；主色调取官方站的绿色系（用取色器读官方站 CSS 变量，记录数值来源），链接色、代码块、admonition 的配色逼近官方站
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
