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
| `docs/MIGRATION-NOTES.md` | Material for MkDocs → MyST 的语法对照（迁移时的记录，不参与构建） |
| `examples/` | 示例代码，按 Isaac Lab 版本分目录，每个示例带 README |
| `tools/` | 构建检查与预览脚本 |
| `tools/legacy/` | 已退役的迁移工具（`md2myst.py`、`gen_site.py`），仅作记录，不再使用 |
| `tasks/`、`reviews/` | 任务卡与校验报告 |

## 协作

三个 Claude Code session 分工协作，协议见 [WORKFLOW.md](WORKFLOW.md)，写作与代码规范见 [CONVENTIONS.md](CONVENTIONS.md)，裁断记录见 [DECISIONS.md](DECISIONS.md)。
