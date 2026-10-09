# T-AUDIT-01b 1.5 固定句 + 6 个示例文件头注

状态: 待实现
优先级: P2（机械改动，不占 GPU；与 T-AUDIT-01a 一起做）
类型: 微任务（源自 reviews/AUDIT-01.md G-2、G-3，D-029 第 3 条）
产出: `docs/1-env/1.5-install-61-30.md`；报告 G-3 列出的 6 个 examples 文件

## 必须完成

1. 1.5 "版本说明"末尾补 T-8.6b 的固定句。
2. G-3 的 6 个文件按 CONVENTIONS 第 5 节（D-029 口径）补头注：验证版本、日期；GPU 若 README 已写可省；`reach/__init__.py` 三项全补。
3. `sphinx-build -W` 通过；校验方用 audit-all.sh 复跑，G-2 / G-3 应为 0。

## 附记

（实现/校验 session 写）
