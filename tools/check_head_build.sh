#!/usr/bin/env bash
# 设计 session 每次 git commit 后运行：导出 HEAD 到临时目录，做 sphinx-build -W（警告即失败），
# 确保提交本身是完整的（没有遗漏页面、图片、静态文件或配置）。
# 用法：tools/check_head_build.sh            # 检查 HEAD
#       tools/check_head_build.sh --worktree # 检查当前工作区（未提交的改动）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPHINX="$ROOT/.venv/bin/sphinx-build"
[ -x "$SPHINX" ] || { echo "找不到 $SPHINX；先按 README 建环境：python3 -m venv .venv && .venv/bin/pip install -r requirements-docs.txt" >&2; exit 2; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
if [ "${1:-}" = "--worktree" ]; then
  SRC="$ROOT/docs"
  echo "== sphinx-build -W (worktree)"
else
  git -C "$ROOT" archive HEAD | tar -x -C "$TMP"
  SRC="$TMP/docs"
  echo "== sphinx-build -W (HEAD $(git -C "$ROOT" rev-parse --short HEAD))"
fi
[ -f "$SRC/conf.py" ] || { echo "找不到 $SRC/conf.py" >&2; exit 2; }
set +e
env -u PYTHONPATH "$SPHINX" -E -a -W --keep-going -q -b html "$SRC" "$TMP/_site" > "$TMP/build.log" 2>&1
rc=$?
set -e
grep -vE "^Building prefix dict|^Loading model|^Prefix dict has been built|^Dumping model" "$TMP/build.log" || true
if [ $rc -eq 0 ]; then echo "构建通过"; else echo "构建失败（sphinx-build 返回 $rc）"; exit 1; fi
