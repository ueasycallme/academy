# T-GA-02 3.0 概念与迁移页升级：8.1 / 8.2 / 8.3 / 8.4 与 A.1 的"3.0 变化"列

状态: 待实现
优先级: P1（T-GA 系列第 2 张；依赖 T-GA-01 的环境与事实底稿）
类型: 改写 + 少量实测（实现约 3 h，校验约 1.5 h）
依赖: T-GA-01（通过后开工）、D-035、`tasks/T-8-common.md`
产出: `docs/8-frontier/8.1-what-changed.md`、`8.2-multi-backend.md`、`8.3-newton.md`、`8.4-migration-23-30.md`、`docs/appendix/A.1-api-cheatsheet.md` 的 3.0 列

## 要做什么

1. **差异清单先行**：用 `git diff --stat v3.0.0-EA v3.0.0 -- <这四页引用过的每个文件>` 列出四页脚注里引用的源码与文档在 GA 中改了哪些、搬去哪里，写进附记。EA→GA 的文档目录重排过，迁移文档与 concepts 文档要先找到新路径。
2. **逐页改写**：
   - 页顶提示框改为"基于 v3.0.0 正式版，最后核对 2026-10-xx"；`verified:` 与版本说明同步；所有 permalink 改为 `v3.0.0` 并重核行号。
   - 8.1：图 1 与"多数任务默认 PhysX"一句按 T-GA-01 的 F4 改；GA 发布页的六项要点里本站没讲到的（如 Isaac Capture、LEAPP 导出、可变形体）各给一句定位和链接即可，不展开。
   - 8.2：预设与后端选择按 GA 核对（`PresetCfg`、`presets=` 语法）；Cartpole 换预设的实测在 RTX 5090 上重做并替换。
   - 8.3：Newton 版本 1.5.2 → 1.6.1，对比表按 GA 核对。
   - 8.4：迁移清单补上 EA→GA 中对"从 2.3 迁过来的读者"有影响的改动：`AppLauncher` 弃用改用 `launch_simulation`、`--cpu` 改 `--device cpu`、`--viz newton` 改 `newton_gl`、`NewtonVisualizerCfg` 拆分、录像改 `VideoRecorderCfg`、观测噪声回调不得原地修改、部分指标返回设备上的张量、`load_torchscript_model` 改为抛异常。每条给 v3.0.0 来源。第 5 步"转换并评估旧检查点"的数字由 T-GA-03 重测，本卡只改文字并留回链。
   - A.1 的"3.0 变化"列按新 8.4 同步。
3. 不写"EA 时如何"，除非这个变化本身对已经用过 EA 的读者有用；需要时一句话带过。

## 校验（examine）

核每条新增与改写的来源（v3.0.0 permalink 行号）；复现 8.2 的 Cartpole 换预设一次；8.1 图 1 与 F4 一致；-W 构建；篇幅 ≤ 3500（D-027）。

## 验收标准

四页与 A.1 的 3.0 断言全部按 v3.0.0 核对过；页顶提示框与版本说明已改；8.2 数字为 GA + RTX 5090；校验通过。

## 附记

（实现/校验 session 写）
