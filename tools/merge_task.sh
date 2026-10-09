#!/usr/bin/env bash
# 设计 session 合并一张任务卡：只 add 指定文件，按暂存树重生成占位页与首页进度表，
# 提交后跑 check_head_build 并推送（push_main.sh 会先跑检查）。
#
# 用法：tools/merge_task.sh '<提交信息首行>' <文件或目录>...
# 任务卡的"状态: 通过"由本脚本改为"已合并"（只改传入的 tasks/*.md）。
set -euo pipefail
cd "$(dirname "$0")/.."

msg="$1"; shift
[ $# -gt 0 ] || { echo "no files given" >&2; exit 1; }

for f in "$@"; do
  case "$f" in tasks/*.md) sed -i 's/^状态: 通过$/状态: 已合并/' "$f";; esac
done
git add -- "$@"

# 按暂存树（不含工作树里其他任务的中间稿）重生成占位页与首页
tree=$(git write-tree)
tmp=$(mktemp -d)
git archive "$tree" | tar -x -C "$tmp"
(cd "$tmp" && python3 tools/gen_placeholders.py >/dev/null && python3 tools/gen_placeholders.py --check | tail -1)
for f in $(git ls-files docs); do
  if [ -f "$tmp/$f" ] && ! git show ":$f" | cmp -s - "$tmp/$f"; then
    echo "regenerated: $f"
    git update-index --cacheinfo 100644,"$(git hash-object -w "$tmp/$f")","$f"
  fi
done
rm -rf "$tmp"

git commit -q -m "$msg

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"

# 更新日志：提交后按 HEAD 的 git log 重生成 A.5（这样表里含本次提交），有变化就 amend 进同一提交
if [ -f tools/gen_changelog.py ] && git ls-files --error-unmatch docs/appendix/A.5-changelog.md >/dev/null 2>&1; then
  python3 tools/gen_changelog.py >/dev/null
  if ! git diff --quiet -- docs/appendix/A.5-changelog.md; then
    git add docs/appendix/A.5-changelog.md && git commit -q --amend --no-edit
  fi
fi
git log -1 --format='%h %s'
tools/push_main.sh
