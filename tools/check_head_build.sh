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

# 占位页：HEAD 导出里的占位页必须与生成器一致（T-SITE-12）
if [ -f "$TMP/tools/gen_placeholders.py" ]; then
  echo "== 占位页一致性检查 (HEAD)"
  (cd "$TMP" && python3 tools/gen_placeholders.py --check | tail -1) || { echo "占位页检查失败"; exit 1; }
fi

# 主线项目：HEAD 导出里包内的相对导入必须都能解析（防止只提交了依赖方、漏了被依赖的模块）
PROJ="$TMP/examples/isaaclab-2.3/6-galbot-project/source"
if [ -d "$PROJ" ]; then
  echo "== 项目相对导入检查 (HEAD)"
  (cd "$PROJ" && python3 - <<'PY'
import ast, pathlib, sys
bad = []
for f in pathlib.Path('.').rglob('*.py'):
    for node in ast.walk(ast.parse(f.read_text())):
        if isinstance(node, ast.ImportFrom) and node.level and node.module:
            base = f.parents[node.level-1]
            rel = node.module.replace('.', '/')
            if not (base/(rel+'.py')).exists() and not (base/rel).is_dir():
                bad.append(f"{f} -> {node.module}")
if bad:
    print("缺少被导入的模块："); print("\n".join(bad)); sys.exit(1)
print("相对导入全部可解析")
PY
  ) || { echo "项目导入检查失败：提交不完整"; exit 1; }
fi
