# T-SITE-07 GitHub Pages 部署（academy.kiloong.com）

状态: 待实现
优先级: P1
类型: 基础设施
依赖: T-SITE-06

## 目标

推送到 GitHub 后自动构建并发布到 https://academy.kiloong.com 。

## 必须完成

1. `.github/workflows/pages.yml`：checkout → 安装 `requirements-docs.txt`（锁版本，缓存 pip）→ `sphinx-build -W -b html docs docs/_build/html` → 上传 artifact → `actions/deploy-pages`。触发：push 到 main + 手动。
2. `docs/_static/CNAME`（或通过 `html_extra_path`）内容为 `academy.kiloong.com`，确保出现在构建产物根目录。
3. `docs/_static/.nojekyll` 同样进入产物根目录。
4. `conf.py`：`html_baseurl = "https://academy.kiloong.com/"`；`sitemap` 可选。
5. README 增加"部署"一节：工作流说明；**需要用户在 GitHub 上做的事**列成清单：仓库 Settings → Pages → Source 选 GitHub Actions；DNS 加 CNAME 记录 `academy` → `ueasycallme.github.io`；Pages 里填自定义域名并勾选 Enforce HTTPS。
6. 本地用 `act` 或至少 `python -c` 验证 workflow YAML 合法；实际推送由用户或设计 session 执行。

## 附记

（实现/校验 session 写）
