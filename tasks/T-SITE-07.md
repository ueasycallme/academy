# T-SITE-07 GitHub Pages 部署（academy.kiloong.com）

状态: 已合并
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
6. **子路径与根路径**：公告条与自定义模板里以 `/` 开头的链接在 `ueasycallme.github.io/academy/` 子路径下会失效（reviews/T-SITE-06.md）。要么全部改为相对路径 / `pathto()`，要么确认只通过自定义域名根路径访问并在 README 写明；两者都验证一次。
7. 本地用 `act` 或至少 `python -c` 验证 workflow YAML 合法；实际推送由用户或设计 session 执行。

## 附记

（实现/校验 session 写）

### 实现附记（isaac-academy-accomplish，2026-09-30）

**当前在做**：本任务已完成。接下来做 T-1.9。

**产出**
- `.github/workflows/pages.yml`：包含 build 与 deploy 两个 job。build 依次执行 checkout@v4、setup-python@v5（3.10，按 `requirements-docs.txt` 缓存 pip）、`pip install -r requirements-docs.txt`、`sphinx-build -E -a -W --keep-going -b html docs docs/_build/html`、configure-pages@v5、upload-pages-artifact@v3；deploy 使用 deploy-pages@v4，环境为 github-pages。
    - 权限：contents read、pages write、id-token write。
    - 并发：同一时间只保留一次部署，不中途取消。
    - 触发：push 到 `main` 或 `master`，以及 workflow_dispatch。**与任务卡的差异**：任务卡写的是 main，但本地仓库当前分支名是 `master`，所以两个都列上，推送哪个都能触发。
- `docs/_extra/CNAME`（内容为 `academy.kiloong.com`）与 `docs/_extra/.nojekyll`（空文件），在 `conf.py` 中通过 `html_extra_path = ["_extra"]` 复制到产物根目录。没有放进 `_static/`，因为放在那里会进入 `_static/` 子目录，而不是根目录。
- `conf.py`：`html_baseurl = "https://academy.kiloong.com/"`，页面因此带有 canonical 链接。没有加 sitemap（可选项，要引入 sphinx-sitemap 依赖，暂不引入）。
- README 新增"部署"一节：说明工作流，并用清单列出仓库所有者需要在 GitHub 与 DNS 上完成的 5 件事（推送、Pages Source 选 GitHub Actions、DNS 中 CNAME `academy` → `ueasycallme.github.io`、填写自定义域名并勾选 Enforce HTTPS、确认首次运行成功）。

**验证**
- YAML：用 PyYAML 解析通过（jobs 为 build 与 deploy；on 为 push [main, master] 与 workflow_dispatch）。本机没有 `act`，无法在本地运行 Actions。
- 模拟构建：把工作区文件导出到临时目录，新建干净的 Python 3.10 venv，执行与工作流完全相同的安装与构建命令。结果：返回码 0；产物根目录有 `CNAME`（内容为 academy.kiloong.com）、`.nojekyll`、`index.html`；0.2 页含 `<link rel="canonical" href="https://academy.kiloong.com/0-map/0.2-layers.html" />`。
- 实际推送与部署由用户或设计 session 执行（按规定，本 session 不做 git 写操作）。

**注意事项**：站点按"部署在域名根目录"配置，T-ENV-01 的公告条链接用了根相对路径 `/1-env/…`。如果将来改为部署在 github.io 的子路径下，需要同步修改。README 中已写明。

### 校验附记（isaac-academy-examine，2026-09-30）
结论：通过。YAML 合法、5 个 action 版本存在；全新 Python 3.10 环境按 requirements 构建 `-W` 通过；CNAME、.nojekyll、canonical 均在产物中；根路径与子路径都实测过，只有公告条一处根路径链接在子路径下 404，README 已写明只按根路径部署。1 条建议见 `reviews/T-SITE-07.md`。

### 校验附记·补充（isaac-academy-examine，2026-09-30）
建议 1 已采纳：公告条链接在子路径下（浅层与深层页）改写正确并返回 200；产物中已没有以 / 开头的链接。

### 第 6 项：子路径与根路径（isaac-academy-accomplish，2026-09-30；在首次提交合并之后完成，改动尚未提交）

- 扫描：对构建产物 grep 以 `/` 开头的 `href`、`src`，发现**只有公告条的链接**是根相对路径。页面内链接、导航与静态资源都由 Sphinx 生成相对路径（页面带 `data-content_root="../"`）。
- 处理方式（兼顾两种访问方式）：
    1. `docs/conf.py` 中公告条链接改为自定义域名下的绝对地址 `https://academy.kiloong.com/1-env/1.2-version-decision.html`，这样无 JS 时也能用；同时加上 `data-academy-local="1-env/1.2-version-decision.html"`。
    2. `docs/_static/js/announcement-close.js` 新增 `localizeLinks`：把公告条中带 `data-academy-local` 的链接改写为 `data-content_root` 加上该相对路径。
    3. README"部署"一节改为说明两种访问方式都支持。
- 验证（headless Chrome，重新全量构建之后）：
    - **子路径**：把产物复制到 `…/subpath/academy/` 并在 8771 端口提供服务。`/academy/0-map/0.2-layers.html` 上公告链接为 `http://127.0.0.1:8771/academy/1-env/1.2-version-decision.html`，fetch 返回 200；academy.css 已加载；没有 4xx 资源；左栏链接、logo 都在 `/academy/` 之下。深层页 `/academy/6-galbot/4-task/6.4.1-reach.html` 的公告链接同样指向 `/academy/1-env/…`，返回 200。
    - **根路径**（8770 端口，产物在根目录）：首页公告链接为 `http://127.0.0.1:8770/1-env/1.2-version-decision.html`，返回 200。
- 涉及文件：`docs/conf.py`、`docs/_static/js/announcement-close.js`、`README.md`。

