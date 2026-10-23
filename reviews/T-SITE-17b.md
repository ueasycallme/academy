# T-SITE-17b 校验报告：7.4 L87 写明 workflow 的实际运行结果

校验 session：isaac-academy-examine，2026-10-24
结论：**通过**

- **改动**：只改了 `docs/7-infra/7.4-testing-ci.md` L87 这一句。原来的"第一次在 GitHub 上实际运行的结果，本站会在运行后补记"，改为"第一次运行是 2026-10-11（UTC），由 push 触发，结果通过（运行记录）；截至 2026-10-24 共运行 9 次，全部通过"。
- **事实核对**（GitHub API，2026-10-24）：
  - `actions/runs/38144708691`：workflow "Galbot project tests (no GPU)"，event `push`，conclusion `success`，created_at 2026-10-11T13:49:27Z，commit ac2e69b；
  - `workflows/examples-tests.yml/runs`：total_count 9，9 次都是 `success`。
  - 页面上的链接返回 HTTP 200。
- **删掉的半句**："workflow 文件在合并前只做了 YAML 解析与路径核对"。这句讲的是合并前的状态，现在已有真实运行结果，删掉不影响结论。
- **检查**：
  - 快照 `7a13686`，`-W` 通过（`strict_build_17b.log`）；
  - `audit-internal` 0 处一般、0 处建议，新句子没有带回内部叫法。
