# T-SITE-10 启用公式渲染（MathJax）

状态: 已合并
优先级: P1（T-3.5 交校验后做；T-3.4 通过后才改 3.4 的公式）
类型: 基础设施
依赖: D-022

## 必须完成

1. `docs/conf.py`：`myst_enable_extensions` 加入 `dollarmath`、`amsmath`；MathJax 用 Sphinx 默认配置（jsDelivr）。确认只有含公式的页面才加载 MathJax（Sphinx 默认行为），把实测结果写入附记。
2. 扫描全部已合并页面：代码之外不得有裸 `$`（设计 session 已查过为 0，启用后再用 `-W` 构建确认无新警告）。
3. 把 3.4 页的 PD 公式从文本代码块改成 `$$...$$`，公式下方逐个解释符号与单位（CONVENTIONS 第 3 节"公式"规则）。3.4 若仍在校验中，等它通过后再改，避免与校验交叉。
4. `_template-check.md` 增加一个行内公式与一个独立公式的样例；深浅色下截图确认公式颜色可读、在 1440 宽下长公式不撑破正文（必要时加横向滚动）。
5. 中文搜索（cjk-search.js）不受影响：搜一个含公式页面里的中文词，仍能命中。

## 验收标准

`sphinx-build -W` 零警告；公式在深浅色下可读；无公式页面不加载 MathJax；3.4 的公式含符号说明。

## 附记

（实现/校验 session 写）

### 实现附记（isaac-academy-accomplish，2026-09-30，第 1、2、4、5 项已完成；第 3 项等 3.4 校验通过）

- [x] 1. `conf.py` 中 `myst_enable_extensions` 加入 `dollarmath`、`amsmath`（注释标 D-022）；MathJax 用 Sphinx 默认配置（`https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js`，defer 加载）。
  - 实测全站 126 个 HTML 中只有 `0-map/_template-check.html` 引用了 MathJax，无公式页面不加载。
- [x] 2. 扫描全部 `docs/**/*.md`（去掉围栏代码块与行内代码后）：含 `$` 的行只有 `_template-check.md` 中新加的样例。构建产物中带 `class="math"` 的也只有这一页。`-W` 构建零警告。
- [x] 4. `_template-check.md` 新增"公式"一节：行内公式、字面美元符号（`\$5` 与行内代码两种写法）、独立公式及符号说明、一个长公式。截图目检：
  - `scratch/shots/t10-math-light-1440.png`、`t10-math-dark-1440.png`：公式颜色随主题变化，浅色为 rgb(26,26,26)，深色为 rgb(238,238,238)，都可读。1440 宽下长公式（848px）没有撑破正文。
  - `t10-math-long-390.png`：390 宽下长公式超出容器，MathJax 容器为 `overflow-x: auto`，可在公式内横向滚动；页面整体没有横向滚动（documentElement 未溢出）。因此没有加自定义 CSS。
- [x] 5. 中文搜索：在构建产物中用 `Search._performSearch` 搜"刚度""字面美元符号""目标位置""渲染检查页"，都命中含公式的 `_template-check` 页。
- [x] 3. 见下方"第 3 项"。

### 第 3 项（3.4 通过后完成，2026-09-30）

- 3.4 的 PD 公式由 text 代码块改为 `$$ \tau = K_p\,(q^* - q) + K_d\,(\dot q^* - \dot q) $$`。公式下方逐个说明 τ、K_p、K_d、q*、q̇*、q、q̇ 的含义与单位（弧度口径），并注明 USD 文件中为度。同节正文与表 2 中的 Kp、Kd、q* 统一改为行内公式。
- 截图 `scratch/shots/t10-34-light.png`、`t10-34-dark.png`（1440 宽）：该页共 14 个公式容器，浅色为 rgb(26,26,26)，深色为 rgb(238,238,238)，都可读。
- **MathJax 加载范围更新**：现在加载 MathJax 的页面有 3 个：`_template-check`、`3.4`，以及 `index.html`。首页本身没有公式，这是 Sphinx 的默认行为：`MathDomain.has_equations()` 对根文档会把 toctree 包含的文档一并计入。其余页面都不加载。若希望首页也不加载，需要自定义 `html-page-context` 钩子；本次没有做，保持默认，供设计 session 决定。
- `tools/check_head_build.sh --worktree` 通过（-W）。

### 校验附记（isaac-academy-examine，2026-09-30）
结论：通过。只有 3 个页面加载 MathJax（首页为 Sphinx 默认行为，交设计 session 决定）；公式在深浅色下可读；长公式在 390 宽下于公式内横向滚动；中文搜索不受影响；-W 构建通过。见 `reviews/T-SITE-10.md`。
