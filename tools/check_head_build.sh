#!/usr/bin/env bash
# 设计 session 每次 git commit 后运行：导出 HEAD 到临时目录，做 strict 构建，
# 确保提交本身是完整的（没有遗漏占位页/图片/配置）。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git -C "$ROOT" archive HEAD | tar -x -C "$TMP"
status=0
if [ -f "$TMP/mkdocs.yml" ]; then
  echo "== mkdocs build --strict (HEAD)"
  (cd "$TMP" && env -u PYTHONPATH "$ROOT/.venv/bin/mkdocs" build --strict -q -d "$TMP/_site_mkdocs") || status=1
fi
if [ -f "$TMP/site-sphinx/conf.py" ] && [ -x "$ROOT/site-sphinx/.venv/bin/sphinx-build" ]; then
  echo "== sphinx-build -W (HEAD)"
  (cd "$TMP/site-sphinx" && env -u PYTHONPATH "$ROOT/site-sphinx/.venv/bin/sphinx-build" -W -q -b html . "$TMP/_site_sphinx") || status=1
fi
[ $status -eq 0 ] && echo "HEAD 构建通过" || echo "HEAD 构建失败：提交不完整"
exit $status
