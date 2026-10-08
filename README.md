# isaac_tutor — academy.kiloong.com

Isaac Sim / Isaac Lab 中文学习网站（Isaac Academy）的内容仓库。站点定位、版本策略与硬规则见 [CLAUDE.md](CLAUDE.md)。

站点使用 **Sphinx + MyST-Parser + pydata-sphinx-theme**（D-020），源文件全部在 `docs/`，页面用 MyST Markdown 写，页面模板见 [CONVENTIONS.md](CONVENTIONS.md) 第 2 节。

## 本地构建与预览

```bash
python3 -m venv .venv
env -u PYTHONPATH .venv/bin/pip install -r requirements-docs.txt

tools/serve.sh            # 全量构建 docs/ 并在 http://127.0.0.1:8767/ 预览
tools/check_head_build.sh # 导出 HEAD 做 sphinx-build -W（警告即失败），提交后运行
tools/check_head_build.sh --worktree   # 检查当前工作区
```

- `env -u PYTHONPATH`：去掉 shell 里的 `PYTHONPATH`（例如 ROS 2 Humble 的 `/opt/ros/humble/...`），避免别的 Python 包混进构建环境。
- 改了 `docs/_static/` 下的 CSS 或 JS 后必须全量构建（`-E -a`，`tools/serve.sh` 已默认这样做）；增量构建不会重新复制静态文件。
- 依赖版本全部锁定在 `requirements-docs.txt`。Python 3.10 下 Sphinx 最高为 8.1.x。

## 目录

| 路径 | 内容 |
|---|---|
| `docs/` | Sphinx 站点源：`conf.py`、`index.md`（含各部分 toctree）、各部分目录、`_static/`、`_templates/` |
| `docs/_static/` | 样式 `css/academy.css`、自托管的 Mermaid 与脚本、站点标识 |
| `docs/_static/img/favicon/` | 站点图标：`favicon.svg`（由 `img/academy-logo.svg` 简化：铺满正方形、台阶加粗）与 `favicon-16.png`、`favicon-32.png`、`apple-touch-icon.png`。PNG 由 `python docs/_tools/make_favicons.py`（需 Pillow）按 SVG 的同一组矩形绘制、8 倍超采样后缩小得到；改了 SVG 坐标要同步改脚本。SVG 由 `conf.py` 的 `html_favicon` 引用，PNG 由 `docs/_templates/layout.html` 加进 `<head>` |
| `docs/MIGRATION-NOTES.md` | Material for MkDocs → MyST 的语法对照（迁移时的记录，不参与构建） |
| `examples/` | 示例代码，按 Isaac Lab 版本分目录，每个示例带 README |
| `tools/` | 构建检查与预览脚本 |
| `tools/legacy/` | 已退役的迁移工具（`md2myst.py`、`gen_site.py`），仅作记录，不再使用 |
| `tasks/`、`reviews/` | 任务卡与校验报告 |

## 部署

推送到 GitHub 后，`.github/workflows/pages.yml` 自动构建并发布到 <https://academy.kiloong.com>：

1. 触发：推送到 `main` 或 `master` 分支（本地当前分支名为 `master`，两者都已列入），或在 Actions 页面手动运行（workflow_dispatch）。
2. 构建：Python 3.10，安装 `requirements-docs.txt`（锁定版本，pip 缓存），执行 `sphinx-build -E -a -W --keep-going -b html docs docs/_build/html`，任何警告都会让构建失败。
3. 发布：上传 `docs/_build/html` 为 Pages artifact，再由 `actions/deploy-pages` 部署。
4. `docs/_extra/CNAME`（内容为 `academy.kiloong.com`）与 `docs/_extra/.nojekyll` 通过 `html_extra_path` 原样复制到产物根目录；`conf.py` 设置了 `html_baseurl`，页面带有指向自定义域名的 canonical 链接。

**需要仓库所有者在 GitHub 与 DNS 上完成的事**（工作流本身不能代劳）：

- [ ] 把本仓库推送到 <https://github.com/ueasycallme/academy>。
- [ ] 仓库 Settings → Pages → Build and deployment → Source 选 **GitHub Actions**。
- [ ] 在域名 `kiloong.com` 的 DNS 中添加 CNAME 记录：主机 `academy` → `ueasycallme.github.io`。
- [ ] 仓库 Settings → Pages → Custom domain 填 `academy.kiloong.com`，DNS 检查通过后勾选 **Enforce HTTPS**。
- [ ] 第一次推送后，在 Actions 页面确认 "Deploy site to GitHub Pages" 运行成功。

站点在域名根目录（academy.kiloong.com）与子路径（`ueasycallme.github.io/academy/`）下都能正常浏览：页面内链接与静态资源都是 Sphinx 生成的相对路径；公告条是原样输出的 HTML，它的站内链接由 `_static/js/announcement-close.js` 按页面的 `data-content_root` 改写为相对路径（无 JS 时回退为自定义域名下的绝对地址）。`html_baseurl` 固定为自定义域名，用于 canonical 链接。

站内搜索完全在浏览器端完成，不依赖外部服务：构建时 Sphinx 用 jieba 给中文分词建索引；查询时 `_static/js/cjk-search.js` 把连写的中文短语按索引词表切成词（如"导入路径"→"导入""路径"），再交给 Sphinx 自带的搜索。已知限制：切分后的多个词按"同时包含"匹配，不要求相邻，含完整短语的页面不会优先排序（设计 session 裁断暂不改 Sphinx 的打分逻辑，页面增多后再评估）。

数学公式用 MyST 的 dollarmath / amsmath，由 MathJax 渲染（Sphinx 默认从 jsDelivr 加载，D-022）。只有含公式的页面加载 MathJax；首页也会加载，因为 Sphinx 判断根文档是否有公式时会把 toctree 包含的页面一并计入，这是默认行为，没有另做定制。

## 协作

三个 Claude Code session 分工协作，协议见 [WORKFLOW.md](WORKFLOW.md)，写作与代码规范见 [CONVENTIONS.md](CONVENTIONS.md)，裁断记录见 [DECISIONS.md](DECISIONS.md)。
