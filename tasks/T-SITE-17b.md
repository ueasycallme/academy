# T-SITE-17b 7.4：CI 第一次运行的结果补成实际数据

状态: 已合并
优先级: P3（微卡，约 15 min，不跑 GPU）
类型: 文字回填
依赖: T-SITE-17（已合并 f1b015f）
产出: `docs/7-infra/7.4-testing-ci.md` L87 一句

## 背景

7.4 L87 写"workflow 第一次在 GitHub 上实际运行的结果本站会在运行后补记"，这句在 T-SITE-17 之前就已过时（校验方发现）。设计方 2026-10-24 用 GitHub API 复核：`examples-tests.yml` 共运行 9 次，全部 success；第一次是 2026-10-11 13:49（UTC），由 push 触发：<https://github.com/ueasycallme/academy/actions/runs/38144708691>；最近一次 2026-10-20 01:36（UTC）。

## 要做什么

把 L87 的"会在运行后补记"改成实际结果：第一次运行日期、"截至 2026-10-24 共 9 次，全部通过"，并链接第一次运行的页面（正文可以写仓库地址，D-034 只去掉了顶栏图标）。查询用 `https://api.github.com/repos/ueasycallme/academy/actions/workflows/examples-tests.yml/runs`（未登录每小时 60 次，够用）。若合并前又多了运行，按查询当时的次数写。

## 校验（examine）

对照 API 结果核对次数、日期与链接；-W 构建。

## 附记

（实现/校验 session 写）

- **实现（accomplish，2026-10-24）**：7.4 L87 改为"第一次运行是 2026-10-11（UTC），push 触发，通过（链接 runs/38144708691）；截至 2026-10-24 共运行 9 次，全部通过"。删掉了"合并前只做了 YAML 解析与路径核对"这半句，因为它已经被实际运行取代。
  - **API 复核**：2026-10-24 查询结果 total_count 9。9 次都是 push 触发，都是 completed / success。最早一次 2026-10-11T13:49:27Z（38144708691），最近一次 2026-10-20T01:36:18Z。
  - -W 通过。

**校验（examine，2026-10-24）**：通过。API 复核 run 38144708691 为 push 触发、success、2026-10-11T13:49:27Z；examples-tests.yml 共 9 次，全部 success；链接 200。快照 7a13686，-W 通过，audit-internal 0。
