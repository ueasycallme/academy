# T-AUDIT-01a 术语首次详细讲解页补英文（49 处 / 29 页）

状态: 已合并
优先级: P2（机械改动，不占 GPU；lift 训练间隙做）
类型: 微任务（源自 reviews/AUDIT-01.md G-1，D-029 第 1 条）
产出: 修改报告附表列出的 29 页

## 必须完成

1. 按 reviews/AUDIT-01.md G-1 附表逐条，在该页首次出现处改为"中文（English）"，英文以术语表为准；"Manager-based 环境 / Direct 环境"两处豁免不改。
2. 只改首次出现，不动其他措辞；`sphinx-build -W` 通过；附记给 `git diff --stat` 与条数（应为 47）。
3. 改完让校验方用 `reviews/scripts/audit-terms.py` 复跑，G-1 应为 0。

## 附记

### 实现附记（isaac-academy-accomplish，2026-10-09）

按 reviews/AUDIT-01.md G-1 附表处理，共 47 处，涉及 27 页（另外 2 处为豁免：4.9 的"Manager-based 环境"、4.14 的"Direct 环境"，未改）。

**做法**：
- 在附表所列行，于术语第一次出现处插入"（english）"，用脚本逐条定位，执行前先打印改前改后的对照。
- 英文取自术语表，一般概念按报告的建议用小写，例如"刚体（rigid body）"；专有缩写保留大写，例如"KL 散度（KL divergence）"。
- "压平"的术语表英文是"Flatten / Export"，这里只取 flatten。

**4 处手工处理**（直接插入会出现括号套括号，或紧跟的括号本来就不是英文）：
- 4.11 "课程（见 [4.9 图 1]…）" → "课程（curriculum；见 [4.9 图 1]…）"；
- 6.1.4 "过滤对（只依赖 pxr）" → "过滤对（filtered pair；只依赖 pxr）"；
- 5.1 表格中"观测（策略看到的状态）" → "观测：策略看到的状态（state）"；
- 6.1.2 "把固有频率提高后重测（阻尼比 1.0，…）" → "把固有频率（natural frequency）提高、阻尼比（damping ratio）设为 1.0 后重测（…）"。这里调整了句式，意思不变。

其余都只插入括号，不动别的措辞。按卡上要求，没有删掉页内后文已有的对照。

**git diff --stat**（这 27 页）：27 个文件，+39 / −39。

**自查**：
- **术语审计**：`audit-terms.py --repo <scratch clone，工作区 docs 提交进去>` 复跑，"首次详细讲解页"一项从 49 降为 2，剩下的就是两处豁免。
- **构建**：`check_head_build.sh --worktree`（-W）通过。

### 校验附记（isaac-academy-examine，2026-10-09）

**通过**，见 `reviews/T-AUDIT-01a.md`。在工作区快照上重跑审计脚本，并逐行核对了 diff。
