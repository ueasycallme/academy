# T-SITE-07 校验报告

- 校验日期：2026-09-30
- 结论：**通过**（1 条建议；实际推送与 GitHub 设置由用户完成，本报告无法验证线上部署）

| 项 | 核查 | 结果 |
|---|---|---|
| 1. workflow | `yaml.safe_load` 解析通过：jobs 为 build、deploy，触发为 push（main、master）与 workflow_dispatch；5 个 action 版本（checkout@v4、setup-python@v5、configure-pages@v5、upload-pages-artifact@v3、deploy-pages@v4）的 tag 在 GitHub 上都存在（API 返回 200）；权限 `pages: write`、`id-token: write` 符合 deploy-pages 的要求；pip 缓存以 `requirements-docs.txt` 为 key | ✓ |
| 模拟 CI 构建 | 用 uv 新建 **全新** Python 3.10 环境，只装 `requirements-docs.txt`，执行与 workflow 相同的 `sphinx-build -E -a -W --keep-going`：退出码 0 | ✓ |
| 2–3. CNAME / .nojekyll | 通过 `html_extra_path = ["_extra"]` 进入产物根目录；CNAME 内容为 `academy.kiloong.com` | ✓ |
| 4. html_baseurl | 页面带 `<link rel="canonical" href="https://academy.kiloong.com/…">` | ✓ |
| 5. README 部署一节 | 工作流说明与用户待办清单（推送仓库、Pages Source 选 GitHub Actions、DNS CNAME、Custom domain、Enforce HTTPS、首次运行确认）齐全 | ✓ |
| 6. 根路径与子路径（两种都验证） | 扫描产物全部 126 个 HTML：以 `/` 开头的站内链接**只有一处**，即公告条的 `href='/1-env/1.2-version-decision.html'`（出现在 125 页）；其余样式、脚本、页面链接全部是相对路径。把产物放到 `/academy/` 子路径下用本地服务器实测：页面、CSS 与 1.2 页都返回 200，只有公告条链接指向的 `/1-env/…` 返回 404。实现方选择"只通过自定义域名根路径访问"，并在 README 中写明，符合任务卡允许的第二种方案 | ✓ |
| 7. 本地验证 | 没有 act，已用 YAML 解析代替（任务卡允许） | ✓ |

## 建议
| # | 意见 |
|---|---|
| 1 | 在配置好自定义域名之前（或 DNS 生效前），访客从 `ueasycallme.github.io/academy/` 进入时，全站 125 页的公告条链接都会 404。修复只涉及一处：公告条是 `conf.py` 里的一段 HTML 字符串，不能用 `pathto()`，可以在已有的 `announcement-close.js` 里，按 `DOCUMENTATION_OPTIONS.URL_ROOT` / `document.documentElement.dataset.content_root` 把这个链接改写成相对路径。不改也可以，前提是用户按 README 先完成自定义域名的设置 |
