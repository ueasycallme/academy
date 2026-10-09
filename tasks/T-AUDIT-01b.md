# T-AUDIT-01b 1.5 固定句 + 6 个示例文件头注

状态: 已合并
优先级: P2（机械改动，不占 GPU；与 T-AUDIT-01a 一起做）
类型: 微任务（源自 reviews/AUDIT-01.md G-2、G-3，D-029 第 3 条）
产出: `docs/1-env/1.5-install-61-30.md`；报告 G-3 列出的 6 个 examples 文件

## 必须完成

1. 1.5 "版本说明"末尾补 T-8.6b 的固定句。
2. G-3 的 6 个文件按 CONVENTIONS 第 5 节（D-029 口径）补头注：验证版本、日期；GPU 若 README 已写可省；`reach/__init__.py` 三项全补。
3. `sphinx-build -W` 通过；校验方用 audit-all.sh 复跑，G-2 / G-3 应为 0。

## 附记

### 实现附记（isaac-academy-accomplish，2026-10-09）

1. **1.5 固定句**："版本说明"末尾补上 T-8.6b 的固定句。
2. **G-3 的 6 个文件补头注**：
   - 前 5 个（2.2 `inspect_usd.py`、2.4 `list_physics_schemas.py`、2.5 `check_asset.py` / `edit_usd.py`、2.7 `enable_hello.py`）各补一行"# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04（Isaac Sim 方式运行时）"。其中 2.2、2.4、2.5 也能用 usd-core 跑，所以注明了适用条件。
   - `reach/__init__.py` 补齐验证版本、验证日期（2026-10-08，同 reach 其余文件）和 GPU。
3. **顺手处理**：新建的 `lift/__init__.py`（T-6.4.3，实现中）也补了同样的头注，否则 audit-examples 会报"一般"。

**自查**：
- **examples / version 审计**：`audit-examples.py` 与 `audit-version.py` 在 scratch clone 上复跑：G-3 的 6 个文件都不再报；1.5 不再报缺固定句。
- **8.6 页数口径**：version 审计报"8.6 表注 75 页、实际 76 页"，多出的是 4.8 的草稿（T-4.8 实现中，已有版本说明）。4.8 交付时同步改 8.6。
- **构建**：-W 通过。

### 校验附记（isaac-academy-examine，2026-10-09）

**通过**，见 `reviews/T-AUDIT-01b.md`。在工作区快照上重跑审计脚本，并逐行核对了 diff。
