#!/usr/bin/env bash
# 本地预览：全量构建 docs/ 后用 http.server 提供静态页面（默认端口 8767）。
# 改了 _static 里的 CSS/JS 必须全量构建（-E -a），增量构建不会重新复制静态文件。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${1:-8767}"
env -u PYTHONPATH "$ROOT/.venv/bin/sphinx-build" -E -a -W --keep-going -q -b html "$ROOT/docs" "$ROOT/docs/_build/html"
echo "预览：http://127.0.0.1:${PORT}/"
exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$ROOT/docs/_build/html"
