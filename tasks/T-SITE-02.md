# T-SITE-02 静态资源自托管（面向中国大陆读者）

状态: 待实现
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
