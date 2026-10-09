# T-AUDIT-01a 术语首次详细讲解页补英文（49 处 / 29 页）

状态: 待实现
优先级: P2（机械改动，不占 GPU；lift 训练间隙做）
类型: 微任务（源自 reviews/AUDIT-01.md G-1，D-029 第 1 条）
产出: 修改报告附表列出的 29 页

## 必须完成

1. 按 reviews/AUDIT-01.md G-1 附表逐条，在该页首次出现处改为"中文（English）"，英文以术语表为准；"Manager-based 环境 / Direct 环境"两处豁免不改。
2. 只改首次出现，不动其他措辞；`sphinx-build -W` 通过；附记给 `git diff --stat` 与条数（应为 47）。
3. 改完让校验方用 `reviews/scripts/audit-terms.py` 复跑，G-1 应为 0。

## 附记

（实现/校验 session 写）
