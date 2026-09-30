# T-SITE-02 静态资源自托管（面向中国大陆读者）

状态: 已合并
优先级: P1（上线前必须完成；排在 T-0.2 校验结束之后再领）
类型: 基础设施
依赖: T-SITE-01
来源: reviews/T-SITE-01.md 建议 1

## 目标

站点在中国大陆网络下不依赖任何境外 CDN 也能完整渲染：Mermaid 图、字体、图标全部自托管或使用系统字体。

## 必须完成

1. **Mermaid 自托管**：把 `mermaid.min.js`（与 Material 9.7.7 当前加载的 mermaid@11 同一大版本）放到 `docs/assets/js/`，通过 `extra_javascript` 加载，并确认 Material 不再从 unpkg 拉取。若 Material 的 superfences mermaid 集成不允许替换来源，改用 pymdownx 的 `mermaid` 自定义 fence + 自带初始化脚本，深浅色主题切换仍需正常（参考 Material 文档的 mermaid 自定义方案）。记录采用的方案与理由。
2. **字体**：`mkdocs.yml` 设置 `font: false`，关闭 Google Fonts；正文用系统中文字体栈（如 `-apple-system, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`），代码用系统等宽字体栈；写入 `docs/stylesheets/extra.css`。
3. **图标**：确认 Material 图标为内联 SVG，不依赖外部请求；若有例外，记录。
4. **验证**：构建后用浏览器加载任意页面，网络记录中不出现 `unpkg.com`、`fonts.googleapis.com`、`fonts.gstatic.com`、`cdn.jsdelivr.net` 等境外域名。把域名清单写进附记。
5. 在 `reviews/ENV.md` 旁不需要动；把"本地预览需 `env -u PYTHONPATH`"的说明补进 `README.md`（仓库根目录，新建，内容：本地预览步骤、目录说明、指向 WORKFLOW.md）。

## 验收标准

- `mkdocs build --strict` 零警告。
- 断网（或屏蔽上述域名）状态下打开 `_template-check.md`，Mermaid 图正常渲染，深浅色可切换。
- 页面网络请求全部指向本站。

## 附记

（实现/校验 session 写）

### 实现附记（isaac-academy-accomplish，2026-09-30）

**产出**
- `docs/assets/js/mermaid.min.js`：mermaid 11.17.2，取自 npm registry 的 tarball `mermaid-11.17.2.tgz` 中的 `package/dist/mermaid.min.js`，sha256 `581ed7d74bd9048d0e3a91363927d72ef22942d7722546b27f7cc29e35390eb8`。unpkg 上 `mermaid@11` 当前也重定向到 11.17.2，版本与原先一致。许可文件放在同目录 `mermaid.LICENSE.txt`（MIT）。
- `mkdocs.yml`：`theme.font: false`；新增 `extra_javascript: [assets/js/mermaid.min.js]`，附注释说明原因与版本。
- `docs/stylesheets/extra.css`：用 `--md-text-font` 设中文系统字体栈（-apple-system、PingFang SC、Microsoft YaHei、Noto Sans CJK SC 等），用 `--md-code-font` 设系统等宽字体栈。
- `README.md`（仓库根目录，新建）：本地预览步骤（统一带 `env -u PYTHONPATH`，并说明原因）、不要升级 MkDocs 2.x、目录说明、指向 WORKFLOW / CONVENTIONS / DECISIONS。

**Mermaid 方案与理由**：采用"预加载全局 mermaid"方案，没有改用 pymdownx 的自定义 fence。Material 9.7.7 的 bundle 中，Mermaid 加载函数的逻辑是：`typeof mermaid=="undefined"` 时才去拉 `https://unpkg.com/mermaid@11/dist/mermaid.min.js`，否则直接用已有的全局对象，随后照常用 Material 自己的 `themeCSS` 初始化。所以只要在 `extra_javascript` 里先加载本地文件，Material 的 Mermaid 集成（包括深浅色主题跟随）原样保留，不用自写初始化脚本。时序上：`extra_javascript` 与 bundle 都是 body 末尾的同步脚本，Material 在 DOM 就绪后才处理 mermaid 块，那时本地 mermaid 已定义。以后升级 Material 时，需要复查 bundle 里的这段逻辑是否还在，以及大版本是否一致。

**图标**：Material 图标以内联 SVG 或 CSS `data:image/svg+xml` URI 的形式出现，没有外部请求。bundle 中还有 `https://api.github.com`，只在配置了 `repo_url` 时用于拉仓库信息，本站未配置，不会触发。

**验证**
- 构建产物 grep：`site/**/*.html` 中没有 `fonts.googleapis.com`、`fonts.gstatic.com`、`unpkg.com`、`cdn.jsdelivr.net`。仅剩 `_template-check` 页正文里两个指向 squidfunk.github.io 的普通超链接，属于内容链接，不是资源加载。
- Chrome 网络记录（`/0-map/0.2-layers/` 整页加载）：全部 21 条请求中，本站请求都指向 `127.0.0.1:8765`（HTML、main/palette/extra CSS、bundle、`assets/js/mermaid.min.js`、search worker、`search_index.json`），另有 5 条 `data:image/svg+xml` 图标，其余是浏览器扩展自身的 `chrome-extension://` 请求，与本站无关。**境外域名：无。** `_template-check` 页用 Performance API 检查，结果相同，页面只访问 `127.0.0.1:8765`。
- Mermaid 渲染：`_template-check` 图高 516px，浅色、深色一致；0.2 页两张图为 826×554、826×564。body 计算字体为系统字体栈首项 `-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", …`。
- 关于"断网"验收：没有真正断网测试。网络记录证明页面从不请求 unpkg 等境外域名，因此屏蔽这些域名不会影响渲染。校验方如需真正断网测试，可用 Chrome DevTools 的 Request blocking 屏蔽 `unpkg.com` 后复测。
- `env -u PYTHONPATH .venv/bin/mkdocs build --strict` 零 WARNING。

**自检清单**
- [x] 页面结构与模板一致：本任务不新增内容页
- [x] 任务卡"必须完成"1–5 均已完成
- [x] 每条断言有来源：Mermaid 加载逻辑的依据是 Material 9.7.7 的 bundle 源码（`material/templates/assets/javascripts/bundle.*.min.js`）
- [x] Mermaid 在 `mkdocs serve` 中正常渲染，深浅色均可
- [x] 示例代码：无
- [x] 术语：不涉及
- [x] `mkdocs build --strict` 通过

### 校验附记（isaac-academy-examine，2026-09-30）
结论：通过。校验方补做了真实屏蔽外网测试：headless Chrome 下除 127.0.0.1 外所有域名都解析失败，浅色、深色截图中 Mermaid 均正常渲染，页面没有外部请求。mermaid.min.js 的 sha256 与 npm tarball 一致。2 条建议见 `reviews/T-SITE-02.md`。
