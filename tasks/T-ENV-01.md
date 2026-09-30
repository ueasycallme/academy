# T-ENV-01 披露 Isaac Sim 5.1.0 的 Unsupported 状态

状态: 待实现
优先级: P1（T-1.4 交校验后立即做）
类型: 微任务（跨页，D-019）
产出: 修改 `docs/0-map/0.1-overview.md`、`docs/1-env/1.1-compat-matrix.md`、`docs/1-env/1.2-version-decision.md`、Sphinx 公告条文案（site-sphinx 同步）

## 必须完成

1. 三页各加一个 `warning` 提示框（措辞统一，放在首次提到主线版本处）：Isaac Sim 5.1.0 官方文档已标注 "Unsupported release"（引用原文一句并脚注 5.1.0 文档页）；本站仍以 5.1.0 + Isaac Lab 2.3.2 为主线的理由（2.3.x 最高支持 5.1；3.0 仍为 EA，GA 目标 2026-10 底，来源 v3.0.0-EA release notes）；主线将在 3.0 GA 后切换，进展见 8.6。
2. 1.1 表中 Isaac Sim 5.1 行加"官方支持状态：已停止支持（2026-09 核对）"列或备注；6.0/6.1 行写"支持中"。
3. 站点公告条改为："主线：Isaac Sim 5.1.0（官方已停止支持）+ Isaac Lab 2.3.2；3.0 前沿专栏基于 EA。为何仍选 5.1.0 → 链接 1.2"。
4. 8.6 版本追踪占位页顶部加一行"待写：跟踪 3.0 GA 与主线切换"。

## 验收标准

三页 warning 措辞一致；来源脚注成立；两站构建零警告；校验只复核这些改动。

## 附记

（实现/校验 session 写）
