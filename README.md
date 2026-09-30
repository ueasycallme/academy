# isaac_tutor — academy.kiloong.com

Isaac Sim / Isaac Lab 中文学习网站（Isaac Academy）的内容仓库。站点定位、版本策略与硬规则见 [CLAUDE.md](CLAUDE.md)。

## 本地预览

```bash
python3 -m venv .venv
env -u PYTHONPATH .venv/bin/pip install -r requirements-docs.txt
env -u PYTHONPATH .venv/bin/mkdocs serve        # http://127.0.0.1:8000
env -u PYTHONPATH .venv/bin/mkdocs build --strict
```

`env -u PYTHONPATH` 用来去掉 shell 里的 `PYTHONPATH`（例如 ROS 2 Humble 的 `/opt/ros/humble/...`），否则 ROS 的 Python 包会混进 venv，`pip freeze` 的结果也会不干净。

不要把 mkdocs 升级到 2.x：Material 9.7 与 MkDocs 2.0 不兼容，`requirements-docs.txt` 已锁定版本。

站点不依赖境外 CDN：Mermaid 自托管在 `docs/assets/js/`，字体用系统字体栈（`theme.font: false`），图标是 Material 内联 SVG。

## 目录

| 路径 | 内容 |
|---|---|
| `docs/` | 站点页面，目录规则见 CONVENTIONS.md 第 1 节 |
| `docs/assets/` | 图片、自托管脚本 |
| `docs/stylesheets/` | 自定义样式 |
| `examples/` | 示例代码，按 Isaac Lab 版本分目录 |
| `tasks/` | 任务卡 |
| `reviews/` | 校验报告 |
| `mkdocs.yml` | 站点配置 |

## 协作

三个 Claude Code session 分工协作，协议见 [WORKFLOW.md](WORKFLOW.md)，写作与代码规范见 [CONVENTIONS.md](CONVENTIONS.md)，裁断记录见 [DECISIONS.md](DECISIONS.md)。
