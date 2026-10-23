# T-GA-01 3.0 正式版环境与 1.5 / 1.1 / 1.2：搭 GA 环境、出"GA 事实底稿"

状态: 已合并
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

**进度（accomplish，10-23 17:05，按设计方通知暂停，19:30 恢复）**：
- **已完成**
  - worktree `~/wuql_ws/isaac_sim/IsaacLab-3.0-GA` @ e3f7d9ff1。本机没有 git-lfs，`worktree add` 时只对这一条命令用 `-c filter.lfs.*` 关掉 LFS 过滤。
  - 路线 A `uv sync`：rc=0，59.6 s，装 207 个包，`.venv` 8.1 GB。
  - F8：warp 1.17.0 `config.py` L115 仍为 RELAXED。
  - F7（路线 A 部分）：rsl-rl-lib 5.5.1、warp-lang 1.17.0、newton 1.6.1、torch 2.11.0+cu130、mujoco-warp 3.12.0。
  - 已存 GA 发布页正文 `scratch/accomplish/tga01/rel_v300.md`：`--cpu` 已删，AppLauncher 有限兼容，`--headless` 不再关可视化器，`--viz none`。
  - F1 源码初查：`visualizer[...]` 仍不按逗号拆（install.py L861–L869），待实测。
- **未完成**
  - `uv sync --extra isaacsim` 失败，rc=2，用时 5 min（日志 `scratch/accomplish/tga01/a_sync_isaacsim.log`）。原因是等 uv 缓存锁超时（300 s），日志原话 "is another uv process running?"，推断是校验方同时在用 uv 装环境。恢复后重跑。
  - 路线 B、C 未开始；Cartpole 与 F2–F6 未开始。
- **后台任务**：没有在跑的后台任务，也没有 GPU 进程。


**校验方环境进度（examine，2026-10-23，暂停时）**：路线 B 在 `~/wuql_ws/academy_ws/scratch/examine/envGA/` 下。源码是 `IsaacLab-3.0-GA`（v3.0.0，e3f7d9ff1，在校验方自己的镜像里检出，绕过了 lfs）；环境是 `env_isaaclab30_ga`。安装脚本 `install_b.sh` 在后台跑（PID 1291072，外层 timeout 是 PID 1291071，上限 5400 s），日志 `install_b.log`，末行 `rc=` 表示结束。Kit 还没预热，恢复后再做。
- 补（examine）：后台安装已结束，rc=0。各步用时：isaacsim 6.2.0.0 389 s，torch cu130 5 s，`isaaclab.sh -i` 94 s。都不是计时测量。Kit 仍未预热，等恢复后再做。
- 补（examine，Kit 预热）：路线 B，RTX 5090，驱动 580.178.04。命令 `isaaclab train --rl_library rsl_rl --task Isaac-Cartpole-Direct --num_envs 64 --max_iterations 1 physics=isaacsim_physx`，Kit 正常启动，rc=0（日志 `scratch/examine/envGA/warm/warm2.log`）。
  - 没有与驱动有关的警告或拒绝启动。Warp 打印 `Warp 1.17.0 initialized: CUDA Toolkit 12.9, Driver 13.0`，设备为 "NVIDIA GeForce RTX 5090" (31 GiB, sm_120)。
  - 启动时的全部警告（各 1 条）：`omni.platforminfo.plugin` "failed to open the default display.  Can't verify X Server version."；`omni.usd_config.extension` "Enable omni.materialx.libs extension to use MaterialX"；"Possible version incompatibility. Attempting to load carb::ujitso::IFactory with version v0.3 against v0.2."；`usdrt.population.plugin` "Last global time was not created…"；`isaaclab.utils.assets` "Serving remote assets from the local cache under '/tmp'…"。
  - 环境版本：Python 3.12.14、isaacsim 6.2.0.0、torch 2.11.0+cu130、rsl-rl-lib 5.5.1、warp-lang 1.17.0、newton 1.6.1；环境 26 GB。
  - 另一个问题，与驱动无关：本机没装 git-lfs，第一次运行在 Kit 起来之后报 `GitCommandError: git status … git-lfs: not found`，rc=1。原因是 rsl_rl 的 `_store_code_state` 会调用 git status。把检出的 `filter.lfs.*` 设为空操作后，第二次运行通过。读者装了 git-lfs 就应该不会遇到（推断，没有在装了 git-lfs 的机器上验证）。

**GA 事实底稿（accomplish，2026-10-23，RTX 5090 32 GB / 驱动 580.178.04；原始输出在 `scratch/accomplish/tga01/`）**

- **环境**
  - worktree：`~/wuql_ws/isaac_sim/IsaacLab-3.0-GA` @ e3f7d9ff1。
  - 路线 A：仓库内 `.venv`，`uv sync` 加 `--extra isaacsim` 后 25 GB。
  - 路线 B：`scratch/accomplish/env_ga_b`，26 GB。
  - 路线 C：`scratch/accomplish/env_ga_c`，`newton,rl[rsl-rl]` 装完 7.8 GB，为 F5 补装 `ov[ovphysx]` 后 8.3 GB。
  - 三个环境同一个 du 统计、硬链接只算一次，共 31 GB。这些包 uv 缓存里本来就有，`df` 显示的分区已用空间在装前装后都是 113 GB。
  - 安装用时都在缓存命中下测得：A `uv sync` 59.6 s；B 共约 42 s（其中 `isaaclab.sh -i` 35 s）；C 43 s。没有冷缓存下载的数字。
  - git：本机没有 git-lfs，而 git 配置里有 `filter.lfs.*`，所以 worktree 里 `git status` 会报 `git-lfs: not found`，rsl_rl 记录代码状态时随之 rc=1（校验方先发现）。本站用按进程的 `GIT_CONFIG_COUNT/KEY/VALUE` 把 filter.lfs.* 改成空操作，没有改仓库配置。属于本机特有问题，不写进页面。
  - 驱动：A、B 两次启动 Kit，日志里都没有 driver 相关的警告或错误，`[Error]` 计数为 0（`kit_20261023_173801.log`）。
- **F1 安装选择器**
  - extras 名称：EA 的全部保留，GA 新增 `dev`、`skrl-jax`、`torchrl`（两个 tag 的 pyproject `[project.optional-dependencies]` 对比）。
  - 逗号问题未修。`./isaaclab.sh -i 'visualizer[rerun,viser]'` 打印 `[WARNING] Unknown root extra 'rerun,viser'`，rc=0，rerun-sdk、viser 都没装（`tga01/f1_viz.log`）。
  - 源码：v3.0.0 `install.py` L861–L869 的 `visualizer` 分支把整个 selector 当成一个名字；`rl[...]` 分支 L851–L856 同样不拆。顶层的 `split_install_items`（L711）会跳过括号里的逗号。
- **F2 `--headless`**
  - `isaaclab train … --headless` → rc=2，`isaaclab: error: unrecognized arguments: --headless`，与 EA 相同。
  - `--viz none` → rc=0，banner 显示 `Visualizer none (headless)`。
  - 不写 `--viz` 时默认也是 `none (headless)`。
  - GA 发布页 "Visualization and recording" 一节写 "`--headless` no longer disables configured visualizers. Use `--viz none`"，统一 CLI 里这个参数已不存在（`tga01/probes/f2_*.log`）。
- **F3 `--cpu` / `--device cpu`**
  - `--cpu` → rc=2，unrecognized。
  - `--device cpu` → rc=0，banner `Device cpu`，Newton 在 CPU 上训练（64 env 2 次迭代 11.6 s）。
  - 与发布页 "The hidden `--cpu` argument; use `--device cpu`" 一致。
- **F4 默认物理后端**：不带 `physics=` 时，Isaac-Cartpole-Direct、Isaac-Cartpole（manager-based）、Isaac-Reach-Franka 三个任务在路线 A（装了 isaacsim）与路线 C 里，banner 都是 `Physics newton_mjwarp`，共 6 次运行全是 Newton。8.1 现写"多数任务默认 PhysX"，**8.x 卡要改**。
- **F5 Kit-less 的 PhysX**
  - 路线 C 里 `physics=physx` 的 banner 是 `physx (ovphysx)`：没装 ovphysx 时 rc=1，报 `ModuleNotFoundError: The OvPhysX backend requires the optional 'ovphysx' runtime wheel … uv run --extra ovphysx`；`./isaaclab.sh -i 'ov[ovphysx]'`（装上 ovphysx 0.6.4.72118723、ovstage 0.2.1.385922）后 rc=0。
  - `physics=ovphysx` 也是同样的行为。
  - `physics=isaacsim_physx` 名称不变，在路线 C 里 rc=1，报 "Isaac Sim is not installed or not found on PYTHONPATH"。
- **F6 AppLauncher / launch_simulation**
  - 在路线 A 跑 8.5 的 `convert_galbot_30.py`（用 AppLauncher）→ rc=0，打印一行 `AppLauncher is deprecated; use isaaclab.app.launch_simulation.`，输出与 EA 一致（mimic 0、过滤对 7、组合错误 0），转换结果在 `tga01/probes/gen30`。
  - `launch_simulation` 最小用法见官方教程 `scripts/tutorials/00_sim/create_empty.py`：`add_launcher_args(parser)`，再 `with launch_simulation(sim_cfg, args_cli): …`。路线 A 中到 "[INFO]: Setup complete..."，之后循环到 timeout，属预期。
  - 路线 C 中 rc=1，同样报 Isaac Sim 未安装：裸 `SimulationCfg` 的默认物理是 Kit 里的 PhysX，Kit-less 环境要显式选 Newton。
- **F7 版本**
  - 三个环境一致：rsl-rl-lib 5.5.1、warp-lang 1.17.0、newton 1.6.1、mujoco-warp 3.12.0、torch 2.11.0+cu130（CUDA build 13.0）、torchvision 0.26.0+cu130。
  - A、B 有 isaacsim 6.2.0.0；C 没有。
  - 源码包版本：isaaclab 28.0.0、isaaclab_tasks 25.2.0、isaaclab_rl 1.5.1、isaaclab_newton 9.1.4。
  - Python 3.12.14（uv 管理）。
- **F8 Warp**：warp 1.17.0 `warp/config.py` L115 为 `launch_array_access_mode: LaunchArrayAccessMode = LaunchArrayAccessMode.RELAXED`，仍为 RELAXED。
- **其他**
  - wheel：PyPI 上 `isaaclab` 3.0.0 已有 wheel（`isaaclab-3.0.0-py3-none-any.whl`，2026-10-19 上传）。GA 安装页 L593 起有"Isaac Lab Python package"一节（L606：只在大版本发布 wheel）。本站没有走这条路线。
  - 坑一（EULA）仍在：装了 isaacsim 的环境里，`isaaclab train --rl_library rsl_rl --help` 也要求接受 EULA，非交互时报 "EULA not accepted"。
  - 坑三仍在：路线 B 的 isaacsim 一步装进 `warp-lang==1.20.0.dev20261023` 与普通 `torch==2.11.0`，后两步才换成 1.17.0 与 +cu130（`tga01/b_install.log` L164、L176、L416–L417）。
  - `isaaclab train --help` 的 usage 把 `--rl_library` 写成必填，但实测省略它仍 rc=0、能训练（路线 C，Cartpole Direct 1 次迭代），与 EA 的行为相同（用任务默认）；help 的写法有误导，8.7 卡可留意。

**实现（accomplish，2026-10-23）**
- **1.5 整页改写**（文件名不变）
  - 标题、verified、提示框（note，"基于 v3.0.0 正式版"）。
  - 前置检查：驱动分两条写，Isaac Lab 下限 580.65.06 与 Isaac Sim 6.2 测试驱动 595.58.03，各给来源；补 Ubuntu 22.04 在 6.2 已弃用；本机两次 Kit 启动没有驱动警告。
  - 三条路线的命令照 GA 文档重写：路线 B 改 cu130，注明跳过 `sudo apt install`；路线 C 注明 `newton` 选择器已是空操作。
  - 补 extras 变化、wheel 已发布（未实测）。
  - 表 3 在 RTX 5090 上重测：A 路线 Newton 第一次与再次、A/B 的 PhysX、C 的 Newton，计时按 D-032 独占，开始前 nvidia-smi 无其他进程。
  - 坑一、三、四按 GA 复核（坑三的 nightly 变成 1.20.0.dev），坑二沿用 EA 的实测；新增坑六（uv 等锁超时，原因标推断）。
  - 脚注全部改指 v3.0.0 tag，行号已逐个核对。
  - 篇幅含表 3308（≤ 3500）。
- **1.1**
  - 3.0.0-EA、6.1 两行保留为历史、不再加粗；新增加粗的 3.0.0 与 6.2 两行（Kit 110.4.0，PyPI 6.2.0.0 于 2026-10-13 上传，二进制与容器页都在，6.1 / 6.2 文档页均无 Unsupported 横幅）。
  - 页首提示框、驱动与 Python 两条、误解、更新记录、版本说明同步更新。
- **1.2**
  - 决策树：Q3 改为"能接受大量破坏性变更吗？"，B 结点改为 6.2 + 3.0.0。
  - 前沿理由改写；切换时机写成"主线暂仍为 5.1 + 2.3.2，是否切换正在评估"。页面不写 D-035 编号，未替用户下结论。
  - 误解二、三改为 6.2 / 6.x。
- **示例**
  - `verify_install_30.py`：头注改 GA；新增 torch 必须是 CUDA 13 构建的检查；isaacsim 检查改为 6.2。
  - README 同步：在 5.1 环境里 5/10，在 EA 环境里 8/10，均已实测。
- **构建**：gen_placeholders 跑过；-W 通过。
- **给设计方**
  - 8.x 的问题已记在事实底稿：F4，8.1 写的默认后端不对；`--rl_library` 的 help 写法有误导。
  - `docs/index.md` L11 "前沿专栏：Isaac Sim 6.1 + Isaac Lab 3.0.0-EA" 不在 T-GA-02…05 的产出列表里，请决定归哪张卡。
  - 1.4 L291、1.7、1.8 L163、1.9 L250 等页的 3.0 说法留给 T-GA-05。
  - 路线 A 的 `.venv` 按卡的指示放在 worktree 里，不在 scratch 下。

**校验（examine，2026-10-23，第 1 轮）**：退回，1 条低级问题，同轮可修，另有 1 条建议，见 `reviews/T-GA-01.md`。
- 在校验方自己的路线 B 环境里复现：F2（`--headless` rc=2、`--viz none` rc=0）；F4（三个任务默认都是 `newton_mjwarp`，用 isaacsim_physx 那次运行作对照，确认 banner 可信；默认值来源是 `cartpole_common.py` L53）；Cartpole PhysX（3286 MiB、4.88 / 297.32）与 Newton（756 MiB、4.94 / 300）。
- 抽查 F1、F3、F5–F8 原件与表 3 的 summary，一致。permalink 行号逐个核过；`verify_install_30.py` 的 10/10、5/10、8/10 都复现；快照 4c53d2f，-W 通过。
- 问题 1（低）：1.5 表 4 写"5.1 环境用 Warp 1.18.0"，可本机 `~/.cache/warp/` 下没有 1.18.0 子目录。5.1 的 Kit 用的是自带的 omni.warp.core 1.8.2。
- 建议 1：坑六的锁冲突可以补上依据（锁文件与校验方装 isaacsim 的时段重合），仍标推断。

**实现第 2 轮（accomplish，2026-10-23）**
- ① 表 4 的 Warp 一行改为"5.1 环境里 Kit 用自带的 omni.warp.core 1.8.2（子目录 `1.8.2`），3.0 正式版用 1.17.0"。已核对：5.1 环境 `isaacsim/extscache/omni.warp.core-1.8.2+lx64` 存在，`~/.cache/warp/` 下没有 1.18.0。
- 建议项：坑六补了依据（锁文件是 isaacsim-extscache-kit 6.2.0.0 的；同一时段校验方在装同一个包），原因仍标推断。
- -W 通过。

**校验（examine，2026-10-23，第 2 轮）**：通过。
- 表 4 的 Warp 一行与缓存目录一致；坑六补了依据，仍标推断；快照 2f47a1a，-W 通过。
- 措辞小建议（不阻塞）：坑六的"校验方"读者看不懂，可改成"本站同时在另一个环境里装"。
