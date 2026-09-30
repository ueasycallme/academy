# T-SITE-10 校验报告

- 校验日期：2026-09-30
- 结论：**通过**（1 条供设计 session 决定的事项）

| 项 | 核查 | 结果 |
|---|---|---|
| conf.py | `myst_enable_extensions` 增加 `dollarmath`、`amsmath`，注释标 D-022；未自定义 MathJax 路径 | ✓ |
| MathJax 加载范围 | 全量构建 126 个 HTML，带 `<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">` 的只有 `index.html`、`0-map/_template-check.html`、`3-isaacsim/3.4-articulation.html`；带 `class="math"` 的只有后两页 | ✓（首页见下） |
| 裸 `$` 扫描 | 去掉围栏代码块与行内代码后扫描全部 `docs/**/*.md`：含 `$` 的只有 `_template-check.md` 与 3.4 页中有意写的公式 | ✓ |
| 3.4 公式 | `$$ \tau = K_p\,(q^* - q) + K_d\,(\dot q^* - \dot q) $$`，下方逐个解释 τ、K_p、K_d、q\*、q̇\*、q、q̇ 及单位（弧度口径，并注明 USD 中为度）；表 2 表头与目标列改为行内公式。与 T-3.4 通过版本的含义一致 | ✓ |
| 深浅色可读 | 1440 宽截图（`reviews/img/T-SITE-10-3.4-light.png`、`…-dark.png`）：MathJax 正常渲染，浅色深字、深色浅字，表格内行内公式正常 | ✓ |
| 长公式 | 390 宽加载 `_template-check`，MathJax 渲染 31 个容器；长公式容器 scrollWidth 749 > clientWidth 453，`overflow-x: auto` 在公式内滚动；页面 documentElement scrollWidth = clientWidth，无整页横向滚动 | ✓ |
| 中文搜索 | 构建产物 searchindex：`刚度`、`阻尼` 命中 3.4 与 `_template-check`，`字面` 命中 `_template-check`。另查 `目标`、`隐式` 只在 3.4 的 titleterms 中，与 HEAD 构建的索引完全相同，不是本次引入 | ✓ |
| 构建 | `check_head_build.sh --worktree` 通过（-W） | ✓ |

## 供设计 session 决定

- 首页 `index.html` 本身没有公式，但也加载 MathJax（Sphinx 的 `has_equations()` 对根文档把 toctree 纳入的文档一并计入，实现方附记已说明）。影响：首页多一次对 jsDelivr 的请求（defer 加载，不阻塞渲染）。若要"无公式页面一律不加载"，需要加 `html-page-context` 钩子；保持默认也可以接受。
