#!/usr/bin/env bash
# T-AUDIT-01 全站质量巡检：一次跑完 7 项检查，打印每项明细与汇总。
#
# 用法：reviews/scripts/audit-all.sh [输出目录]
#   输出目录默认 /tmp/academy-audit-<日期>；每项明细写到 <输出目录>/<项>.txt，最后打印汇总。
# 以 HEAD 为准：先把仓库克隆到输出目录、在克隆里构建 HTML，不碰工作区（生成器与构建都不写 docs/）。
# 可选环境变量（给了就用本地克隆核对 GitHub permalink，避免 GitHub 限流）：
#   ISAACLAB_REPO=/path/to/IsaacLab   （需含 v2.3.2、v3.0.0-EA 等 tag）
#   GALBOT_REPO=/path/to/galbot_one_golf_description
set -euo pipefail
ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
OUT="${1:-/tmp/academy-audit-$(date +%F)}"
PY="$ROOT/.venv/bin/python"
S="$ROOT/reviews/scripts"
mkdir -p "$OUT"
rm -rf "$OUT/repo" "$OUT/html"
git clone -q "$ROOT" "$OUT/repo"
echo "HEAD: $(git -C "$OUT/repo" log --oneline -1)"
(cd "$OUT/repo" && env -u PYTHONPATH "$PY" -m sphinx -E -a -q -b html docs "$OUT/html" 2>&1 | grep -v -e "prefix dict" -e "Loading model" -e jieba || true)

MIRRORS=()
[[ -n "${ISAACLAB_REPO:-}" ]] && MIRRORS+=(--mirror "isaac-sim/IsaacLab=$ISAACLAB_REPO")
[[ -n "${GALBOT_REPO:-}" ]] && MIRRORS+=(--mirror "GalaxyGeneralRobotics/galbot_one_golf_description=$GALBOT_REPO")

run() {  # run <名字> <命令...>
  local name=$1; shift
  "$@" > "$OUT/$name.txt" 2>&1 || true
}
run 1-links        "$PY" "$S/audit-links.py" --repo "$OUT/repo" "${MIRRORS[@]}"
run 2-anchors      "$PY" "$S/audit-anchors.py" "$OUT/html"
run 3-terms        "$PY" "$S/audit-terms.py" --repo "$OUT/repo"
run 4-fonts        "$PY" "$S/audit-fonts.py" "$OUT/html"
run 5-version      "$PY" "$S/audit-version.py" --repo "$OUT/repo"
run 6-placeholders "$PY" "$S/audit-placeholders.py" --repo "$OUT/repo"
run 7-examples     "$PY" "$S/audit-examples.py" --repo "$OUT/repo"

echo "== 汇总（明细见 $OUT/*.txt）"
for f in "$OUT"/[1-7]-*.txt; do tail -n 1 "$f"; done
