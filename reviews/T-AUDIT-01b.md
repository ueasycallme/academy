# T-AUDIT-01b 校验报告：1.5 固定句与 examples 头注（AUDIT-01 G-2、G-3）

校验 session：isaac-academy-examine，2026-10-09
结论：**通过**

## 断言核查

- **1.5**：版本说明节末新增 T-8.6b 固定句，位置在脚注定义之前，链接 `../8-frontier/8.6-version-tracking.md` 可达。diff 只多了这一句加一个空行。
- **G-3 的 6 个文件**：
  - 5 个 USD / Kit 示例各加了一行 `# GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04（Isaac Sim 方式运行时）`。型号与驱动和本机 `nvidia-smi` 一致（RTX 5070，580.178.04），也与仓库里其他示例的头注一致。
  - reach `__init__.py` 补了验证版本、日期（2026-10-08）和 GPU，与同目录 `reach_env_cfg.py` 等文件的头注一致。
- **diff 范围**：examples 下只有这 6 个已跟踪文件有改动，共 6 files、+9 行，没有删除。

## 覆盖检查

在工作区快照上重跑：
- `audit-examples.py`："一般"级问题 0 个（共 121 个文件，包括尚未提交的 lift、4.8、1.8 示例）；
- `audit-version.py`：1.5 不再报。

剩下唯一的一般项是"8.6 表注 75 页，实际 76 页"，多出来的是正在写的 4.8 草稿，不属于本卡。实现方说 4.8 交付时会同步改 8.6，那时我会复查。快照上 `audit-placeholders.py` 报的 3 条"4.17 / 4.19 / 4.20 没有列出 4.8"也来自同一个草稿：4.8 合并时重跑生成器就会消失。

## 代码运行

`check_head_build.sh --worktree`（-W）通过。

## 其他意见

无。
