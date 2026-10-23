# T-GA-01 校验报告：3.0 正式版环境与 1.5 / 1.1 / 1.2、GA 事实底稿

校验 session：isaac-academy-examine，2026-10-23
结论：**通过**（第 2 轮；第 1 轮的低级问题与建议都已处理，见文末）

- F2、F4、Cartpole 在校验方独立建的路线 B 环境里都复现了。
- 抽查的 F1、F3、F5–F8 原件与底稿一致。
- 1.5 的 permalink 都指向 v3.0.0，行号核对一致；`-W` 通过。
- 只有表 4 的 Warp 一格与本机缓存目录对不上（问题 1）。

## 校验方环境（独立于实现方）

- **源码**：从本地主仓库 fetch tag `v3.0.0`（e3f7d9ff1）到校验方自己的镜像，检出到 `scratch/examine/envGA/IsaacLab-3.0-GA`。本机没装 git-lfs，所以 `.usd` 等是 pointer 文件，镜像的 repo config 里把 `filter.lfs.*` 设为空操作。
- **路线 B**：命令照 v3.0.0 `installation.rst`"Python environment with Isaac Sim"一节，经 `isaaclab_docs.py` 模板、按 pyproject 版本展开：`uv venv --python 3.12` → `isaacsim[all,extscache]==6.2.0.0` → `torch==2.11.0 torchvision==0.26.0`（cu130）→ `./isaaclab.sh -i`。`sudo apt install` 没有执行（本机已有 cmake、gcc）。日志 `envGA/install_b.log`，rc=0。
- **实际装上的版本**：Python 3.12.14、isaacsim 6.2.0.0、torch 2.11.0+cu130、rsl-rl-lib 5.5.1、warp-lang 1.17.0、newton 1.6.1；isaaclab 28.0.0、isaaclab_tasks 25.2.0、isaaclab_rl 1.5.1、isaaclab_newton 9.1.4。与 F7 一致。环境 26 GB。
- **坑三**：我的安装日志里，isaacsim 一步同样装进了 `warp-lang==1.20.0.dev20261023` 与普通 `torch==2.11.0`（L211、L223），后两步才换成 1.17.0 与 +cu130（L244、L478）。与页面一致。
- **驱动**：Kit 在 580.178.04 上正常启动，没有驱动相关的警告或拒绝。启动警告原文已记在卡的附记里。

## 复现（RTX 5090 32 GB，驱动 580.178.04；非计时；日志 `scratch/examine/envGA/ga01/`）

| 项 | 命令（都在路线 B 环境，`isaaclab train --rl_library rsl_rl …`） | 结果 | 底稿 / 页面 |
|---|---|---|---|
| F2 `--headless` | `--task Isaac-Cartpole-Direct --num_envs 64 --max_iterations 1 --headless` | rc=2，`isaaclab: error: unrecognized arguments: --headless` | 一致 |
| F2 `--viz none` | 同上，换成 `--viz none` | rc=0，banner `Visualizer none (headless)` | 一致 |
| F2 不写 `--viz` | 同上，去掉 `--viz` | rc=0，banner 同样是 `none (headless)` | 一致 |
| F4 默认后端 | Isaac-Cartpole-Direct、Isaac-Cartpole、Isaac-Reach-Franka，都不带 `physics=` | 三个都 rc=0，banner 都是 `Physics newton_mjwarp` | 一致 |
| Cartpole PhysX（表 3 B 行） | 默认设置（4096 env、150 次迭代）+ `physics=isaacsim_physx` | 墙钟 24.9 s，训练 16.44 s，按进程显存峰值 3286 MiB，主机 RSS 峰值 4995 MiB；最后一轮 4.88 / 297.32 | 表 3 为 29 s / 16.5 s / 3286 MiB / 4.9 GB。显存与奖励逐位相同；训练时长差 0.1 s。墙钟我少 4 s，我这次不独占且 Kit 已预热，不作比较 |
| Cartpole Newton（补充） | 同上，`physics=newton_mjwarp` | 21.2 s / 12.41 s / 756 MiB / 2565 MiB；4.94 / 300 | 与表 3"A Newton 再次"（22 s / 12.5 s / 756 MiB / 2.5 GB）一致 |
| 验证脚本 | `verify_install_30.py`（路线 B、5.1 环境、EA 环境各一次） | 10/10；5/10（Python 3.11、torch cu128、没有 newton 与 isaaclab_newton、isaacsim 5.1）；8/10（torch cu128、isaacsim 6.1） | 与 1.5 和 README 一致 |

**banner 是否可信**：我拿 `physics=isaacsim_physx` 的一次运行作对照（`warm/warm2.log`）。那次 banner 是 `isaacsim_physx`，日志里有 `KitLauncher` 和 `/physicsScene`。F4 的三次运行里这两样都没有，出现的是 `isaaclab_newton` 的代码路径。所以 banner 反映的是真实后端。默认值的来源在 `isaaclab_tasks/core/cartpole/cartpole_common.py` L53：`default: NewtonCfg = newton_mjwarp`。

## 抽查实现方原件（`scratch/accomplish/tga01/`）

- **F1**：`f1_viz.log` L125 `[WARNING] Unknown root extra 'rerun,viser'. … Skipping.`，L134 `rc=0`。源码 `install.py` L861–L869 的 `visualizer` 分支把整个 selector 当作一个名字，L711 是 `split_install_items`。一致。
- **F3**：`f3_cpu.log` 是 `unrecognized arguments: --cpu`（rc=2），`f3_device_cpu.log` 的 banner 是 `Device cpu`（rc=0）。一致。
- **F5**：路线 C 里，`physics=physx` 与 `ovphysx` 在补装之前都报 `ModuleNotFoundError: No module named 'ovphysx'`；补装后 banner 是 `physx (ovphysx)`，能训练；`isaacsim_physx` 报 "Isaac Sim is not installed or not found on PYTHONPATH"。一致。
- **F6**：`f6_applauncher_convert.log` 有 `AppLauncher is deprecated; use isaaclab.app.launch_simulation.`，8.5 的统计行是 mimic 0、过滤对 7、组合错误 0。一致。
- **F8**：我环境里 warp 1.17.0 的 `config.py` L115 是 `LaunchArrayAccessMode.RELAXED`。一致。
- **表 3 原件**：五个 `*.summary` 的起止时间差是 60 / 22 / 26 / 29 / 22 s，显存峰值 756 / 756 / 3286 / 3286 / 756 MiB，RSS 峰值 2960 / 2542 / 4950 / 4991 / 2501 MiB。各日志的 `Training time` 是 28.47 / 12.52 / 16.59 / 16.51 / 11.14 s，奖励与 banner 都与表一致。两次计时前的 `nvidia-smi` 快照都没有进程。`warpcache_a` 有 30 MB，`~/.cache/newton` 有 394 MB。
- **路线 A 的包数**：`a_sync.log` 是 "Installed 207 packages"，`a_sync_isaacsim2.log` 是 "Installed 85 packages"。一致。

## 来源

- 1.5 的 permalink 都按 v3.0.0 逐个打开起止行，范围与脚注描述对得上：`installation.rst` L22–L81、L83–L149、L153–L281、L285–L411、L415–L589、L561–L562、L593–L606；`isaaclab_docs.py` L248–L267、L314–L339；`install.py` L78–L96（找不到 cmake 才 `sudo apt-get`）；`pyproject.toml` L22、L113、L180–L183、L229–L238；`isaaclab.sh` L11；`assets.py` L430、L563。
- 正文里的几处细节也核过：
  - L83–L149 里有"at least 32 GB RAM, 16 GB VRAM"与"Isaac Sim 5.1 and older are unsupported"；
  - L285–L411 里有"`mimic` and `teleop` submodules plus the default Newton, RL, and visualizer dependencies"；
  - `newton` 选择器那句提示原文在 `install.py` L848。
- **Isaac Sim 6.2 Requirements 页**（2026-10-23 取回）：Linux 测试驱动 595.58.03；有警告"Ubuntu 22.04 support in Isaac Sim is deprecated and will be removed in a future release"。一致。
- **6.2.0 Release Notes**：有"Updated Isaac Sim to Kit SDK 110.4.0"，与 1.1 的 `[^kit62]` 一致。
- **v3.0.0 发布页**（GitHub API）：`prerelease: false`，正文含"This release targets Isaac Sim 6.2, Python 3.12, PyTorch 2.11 with CUDA 13.0"，以及 `--cpu`、`--headless` 两条。与 1.1、1.2 的引用一致。

## 页面检查

- **1.5**：
  - 驱动按两个口径分开写（Isaac Lab 下限 580.65.06，Isaac Sim 6.2 测试版本 595.58.03），各有来源；
  - wheel 路线写明未实测；
  - EA 的说法只出现在"EA 时如何"的对照句里；
  - 汉字 2873（含脚注）、2687（不含），≤ 3500。
- **1.1 / 1.2**：只改了 3.0 与 6.x 部分。1.2 写成"主线暂仍为 5.1 + 2.3.2，是否切换正在评估"，没有替用户下结论。新增的 Windows ≥ 580.88、x86_64 / aarch64 两条，与 `installation.rst` L98–L103 一致。
- **示例**：`verify_install_30.py` 头注改为 v3.0.0、RTX 5090、2026-10-23；新增"torch 必须是 CUDA 13 的构建"一项检查。三种环境的输出我都跑过（见上表）。
- **构建**：快照 `4c53d2f`（`scratch/examine/snap02a`），`-W` 通过（`strict_build_ga01.log`）。

## 问题

| # | 位置 | 问题 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|---|
| 1 | 1.5 表 4"Warp 内核缓存"一行："本站 5.1 环境用 1.18.0，3.0 正式版用 1.17.0，各自一个子目录" | 本机 `~/.cache/warp/` 下只有 `1.16.0`、`1.17.0`、`1.7.1`、`1.8.2`，没有 `1.18.0`。5.1 环境的 pip 层确实有 `warp-lang` 1.18.0（两边环境都是），但 Kit 加载的是自带的扩展 `omni.warp.core-1.8.2`（`isaacsim/extscache/omni.warp.core-1.8.2+lx64`）。缓存里的 `1.8.2` 子目录与它对应（推断，依据是版本号相同） | `ls ~/.cache/warp/`；两个 5.1 环境的 `importlib.metadata.version('warp-lang')` 与 extscache 目录 | 改为"本站 5.1 环境里 Kit 用自带的 omni.warp.core 1.8.2（子目录 `1.8.2`），3.0 正式版用 1.17.0"。若想提 pip 层的 1.18.0，写明它在本站的运行里没有生成缓存子目录 | 低 |

**建议 1（不作问题）**：坑六"推断是它占着锁"，可以补上依据，但仍标推断，因为没有单独做对照：
- 等锁的文件是 `wheels-v6/…/isaacsim-extscache-kit/6.2.0.0-…lock`（`a_sync_isaacsim.log`）；
- 实现方从 16:59:25 等到 17:04:25；
- 同一时段，校验方的路线 B 正在装同一个包 `isaacsim[all,extscache]==6.2.0.0`。按 `install_b.log` 的结束时间（17:06:43）和各步用时（389 s / 5 s / 94 s）倒推，这一步约在 16:58:35–17:05:04。

另外，"本站另一个 session"就是校验方，可以照实写。

## 第 2 轮复核

- **问题 1**：表 4 改为"5.1 环境里 Kit 用自带的 omni.warp.core 1.8.2（子目录 `1.8.2`），3.0 正式版用 1.17.0"，与 `~/.cache/warp/` 和 extscache 目录一致。
- **建议 1**：坑六补了锁文件名和时段重合两条依据，原因仍标推断。
  - 措辞小建议（不阻塞）："校验方"是本站内部的叫法，读者看不懂。可以改成"本站同时在另一个环境里装同一个……"。这是我上一轮建议照实写造成的，合并时顺手改即可。
- 快照 `2f47a1a`，`-W` 通过（`strict_build_ga01_r2.log`）。

结论：**通过**。
