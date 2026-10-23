# T-GA-01 3.0 正式版环境与 1.5 / 1.1 / 1.2：搭 GA 环境、出"GA 事实底稿"

状态: 实现中（accomplish 10-23 开工）
优先级: P1（T-GA 系列第 1 张，其余四张依赖本卡的环境与事实底稿）
类型: 实测改写（实现约 3–4 h，校验约 1.5 h）
依赖: D-035；`tasks/T-8-common.md`（页首 2026-10-23 补注优先）
产出: `docs/1-env/1.5-install-61-30.md`（文件名不变，标题改为"安装 Isaac Sim 6.2 + Isaac Lab 3.0"）、`docs/1-env/1.1-compat-matrix.md` 与 `docs/1-env/1.2-version-decision.md` 的 3.0 部分、`examples/isaaclab-3.0/1.5-install/`；本卡附记里的"GA 事实底稿"

## 背景

Isaac Lab v3.0.0（commit e3f7d9ff1）已正式发布，要求 Isaac Sim 6.2、Python 3.12。本站 3.0 内容按 v3.0.0-EA + Isaac Sim 6.1 写成，D-035 决定全部升级。本卡先把环境搭好，并把后面四张卡都要用的关键事实一次查清。

## 要做什么

1. **环境**（都放 `~/wuql_ws/academy_ws/scratch/accomplish/` 下，不动 EA 环境）：
   - Isaac Lab 源码：`cd ~/wuql_ws/isaac_sim/IsaacLab && git worktree add ../IsaacLab-3.0-GA v3.0.0`（tag 设计方已 fetch；不切换主检出）。
   - 按 1.5 现有的三条路线各建一次：A uv 自动安装、B 自管环境 + pip（`isaacsim` 6.2.0.0）、C 不装 Isaac Sim 的最小安装。官方安装文档在 v3.0.0 中换了位置，先在 tag 里找到新路径再照做，页面脚注引新路径。
   - **驱动**：Isaac Sim 6.2 文档的 Linux 测试驱动是 595.58.03，本机是 580.178.04。第一次启动 Kit 时留意驱动相关的警告或拒绝。只是警告、能跑：照实写进 1.5 前置检查。拒绝启动或崩溃且能归因于驱动：停下报设计方，不要升级驱动。
   - 磁盘：每个环境约 15–25 GB，开工前 `df -h /` 记一次。Docker 镜像与构建缓存已占约 65 GB，不要动它们。
2. **GA 事实底稿**（写在本卡附记，每条给命令、输出摘录、结论；后续卡直接引用，不必各自重查）：
   - F1 安装选择器：`isaaclab` 安装命令的 extras 名称与 EA 是否相同；EA 的 `visualizer[rerun,viser]` 逗号不拆分问题（install.py）是否已修。
   - F2 `--headless`：`isaaclab train` 带 `--headless` 的返回码与行为；`--viz none` 的行为（EA 时 rc 2，见 8.6"GA 复核时留意"）。
   - F3 `--cpu` 已删除、`--device cpu` 可用（发布页说法实测确认）。
   - F4 默认物理后端：Cartpole Direct、Cartpole manager-based、`Isaac-Reach-Franka-v0` 各自不带 `physics=` 时用的是哪个后端（看日志或打印配置）。pyproject 注释称 Newton 是 "default physics engine"，8.1 现写"多数任务默认 PhysX"，以实测为准。
   - F5 Kit-less 进程里 `physics=physx` 是否仍走 OvPhysX、是否仍需要 `ov[ovphysx]`；`isaacsim_physx` 名称是否不变。
   - F6 `AppLauncher` 在 GA 里能否照旧启动本站 8.5 的脚本（发布页说已弃用、兼容有限），以及 `launch_simulation` 的最小用法。
   - F7 实际装上的版本：`rsl-rl-lib`、`warp-lang`、`newton`、`torch`、`isaacsim` 的版本号。
   - F8 Warp 的 `launch_array_access_mode` 默认值在 Warp 1.17.0 中是否仍为 RELAXED（8.9 引用）。
3. **改页面**：
   - 1.5：标题与 `verified:` 改为 v3.0.0 + Isaac Sim 6.2（RTX 5090、驱动号、日期）；三条路线的命令照 GA 重写并实测；"验证"一节的 Cartpole 双后端在 5090 上重测并替换数字；"常见坑"逐条按 GA 复核（已修的删掉或写"EA 时有，GA 已修"）；前置检查补 Ubuntu 22.04 在 6.2 中已弃用、驱动测试版本。示例 `verify_install_30.py` 与 README 同步并标验证版本。
   - 1.1 兼容矩阵、1.2 版本决策：3.0 一行 / 一段改为正式版与 Isaac Sim 6.2。1.2 的建议写成"主线暂仍为 5.1 + 2.3.2，是否切换在评估中（D-035）"，不要替用户下结论。
4. 不改 8.x 页，那是后面几张卡的事；发现 8.x 有明显错误记在附记里即可。OUTLINE 里 1.5 的标题由设计方合并时改。

## GPU

建环境只占 CPU 与网络。Cartpole 重测与 F2–F6 的探针占 GPU，非计时，可与校验方并行各一个 Kit；1.5 若有计时数字，开测前报"开始计时"，期间不做构建。

## 校验（examine）

- 在 `scratch/examine/` 下独立建一条路线 B 的环境，复现 F2、F4 与 1.5 的 Cartpole 一次。
- 抽查 F1、F3、F5–F8 的原始输出。
- 1.5 每个代码块的验证标注与实际一致；permalink 指向 v3.0.0 且行号对得上；-W 构建；篇幅。

## 验收标准

三条路线在 GA 上实测通过（或照实写明哪条不通及原因）；附记有 F1–F8 的事实底稿；1.5 / 1.1 / 1.2 不再出现 Isaac Sim 6.1 或"EA 最新"的说法（历史对照句除外）；校验方复现 F2、F4。

## 设计裁断（2026-10-23）

- **驱动口径分开写**（校验方查到）：Isaac Lab v3.0.0 安装文档（`docs/source/isaaclab/installation.rst`）的要求是 Linux 驱动 "580.65.06 or newer"（因默认装 CUDA 13.0 的 PyTorch），本机 580.178.04 满足；595.58.03 是 Isaac Sim 6.2 文档写的**测试版本**，不是最低要求。1.5 前置检查两条分开写、各给来源；D-035 第 7 条的"停下"只针对实际拒绝启动或驱动类崩溃。
- 安装文档里的 `sudo apt install …` 不执行（本机已有 cmake / gcc）；页面照抄官方命令时注明本站跳过及原因。

## 附记

（实现/校验 session 写）
