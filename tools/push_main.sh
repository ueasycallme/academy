#!/usr/bin/env bash
# 设计 session 用：推送 main 并核实已与 origin 同步（D-023 自动推）。失败重试一次。
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
for attempt in 1 2; do
  if timeout 120 git push origin main >/tmp/push_main.log 2>&1; then break; fi
  echo "push 失败（第 $attempt 次）："; tail -5 /tmp/push_main.log
  [ $attempt -eq 2 ] && exit 1
  sleep 10
done
git fetch -q origin main
if [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]; then
  echo "已推送：$(git log -1 --format='%h %s' | cut -c1-80)"
else
  echo "推送后本地与 origin/main 不一致"; git status -sb | head -1; exit 1
fi
