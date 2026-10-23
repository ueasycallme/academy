# T-GA-04 校验报告：8.7 / 8.8 / 8.9 在 3.0 正式版上重测

校验 session：isaac-academy-examine，2026-10-23 至 10-24
结论：**通过**（第 2 轮；第 1 轮的低级问题已修，见文末）

- 计时复现（独占）：8.8 的 Kit / Kit-less 一组与 8.9 的奖励项一组，与页面相差都在 15% 以内。
- 8.7 抽查的三条命令都能跑通；STRICT 的说法复现了；链接与原件都核过。
- 只有 8.9 坑四中有一句把推断写成了事实（问题 1）。

## 计时复现（RTX 5090 32 GB，驱动 580.178.04；按 D-032 独占；日志 `scratch/examine/ga04/t/`）

**测量条件**：
- 实现方回了"可以"，并确认没有 Kit、构建或 Chrome 在跑之后，我才报"开始计时"。
- 开跑前记了两种 `nvidia-smi`（`gpu_before.txt`、`gpu_before_full.txt`）。计算进程只有用户的远程桌面 `awesun_desktop`（pid 1441619，652 MiB）；图形进程有 Xorg、gnome-shell、awesun，以及用户桌面上的 Chrome（实现方另报了 pid 3079，它不是任一 session 开的）。
- 30 s 一次的记录（`gpu_watch.log`）里，awesun 全程都在，没有出现或消失；其余只有被测进程。
- 所以我这组数字是在有 awesun 常驻的条件下测的，页面表 2 那组是在没有它的条件下测的。

**8.8 表 2**（用实现方的 `time_train.py`，拷到我 scratch 的副本；Cartpole，4096 env，100 次迭代；每组先预热 1 次，再测 1 次）：

| 组合 | 我的环境 | 启动到第一次迭代 | 每次迭代（中位） | 表 2 | 差 |
|---|---|---|---|---|---|
| 装 Isaac Sim + `isaacsim_physx` | 校验方路线 B | 8.2 s | 111.7 ms | 8.7 / 9.2 s，111.5 / 109.2 ms | < 2% |
| 装 Isaac Sim + `newton_mjwarp` | 校验方路线 B | 7.5 s | 78.4 ms | 7.2 / 7.6 s，77.7 / 76.7 ms | +1–2% |
| 路线 C + `newton_mjwarp` | 实现方的 `env_ga_c`（只读使用） | 7.2 s | 71.2 ms | 6.9 / 6.7 s，68.4 / 68.6 ms | +4% |

- "只装不用也有代价"在我这组里成立：同为 Newton，装了 Isaac Sim 的环境比路线 C 慢 7.2 ms，页面写约 9 ms，EA 时 7–10 ms，同一量级。
- 我用的是路线 B，不是路线 A。两者都装了 isaacsim 6.2.0.0，所以这一行可以对照。页面把原因标为推断（"两个环境的包与导入路径不同"），写法恰当。

**8.9 表 3**（`bench_reward_warp.py`，实现方的 kitless `model_199.pt`，路线 C，1024 env，1 次）：

| 项 | 我的 | 表 3（1024 行） |
|---|---|---|
| torch 单次中位 | 0.1277 ms | 0.128 / 0.134 ms |
| Warp 单次中位 | 0.0485 ms | 0.049 / 0.049 ms |
| env.step 中位 | 10.26 ms | 10.0 / 10.0 ms |
| 最大绝对误差 | 4.4×10⁻⁶ m | 3.8×10⁻⁶ m（表 2） |

- 都在 15% 以内，不需要双方各再跑一次。
- 第一次调用 0.8 ms（缓存是热的），与页面"有缓存时 0.8 ms"一致。

## 8.7 抽查三条命令（非计时；`scratch/examine/ga04/cli/`）

| 命令 | 结果 |
|---|---|
| `isaaclab train … --frontend warp physics=newton_mjwarp` | rc=0，跑完 2 次迭代 |
| `isaaclab train --task Isaac-Cartpole-Direct …`（不写 `--rl_library`） | rc=0，banner 显示 `RL library rsl_rl`、`Physics newton_mjwarp`，与页面"用任务的 default_agent"一致 |
| `PYTHONPATH=$PWD isaaclab train --rl_library rsl_rl --task Academy-Cartpole-Direct … --external_callback academy_cli_demo.register_tasks physics=isaacsim_physx`（8.7-cli 的 scratch 副本） | rc=0，`Physics isaacsim_physx`，跑完 2 次迭代 |

## 其他核对

- **原件**（`scratch/accomplish/tga04/`）：
  - `time88.out`：每组 warm、1、2 三次的数字与 8.8 表 2、表 3 一致。OVRTX 第一次的 RSS 峰值是 13878 MiB，之后 5.4–5.5 GB。
  - `time89b.out`：4096 两次，`bench_coldr` 那次的第一次调用是 36.8 ms。
  - 两个空缓存目录各 52 MB。`warpcache_empty_210309` 里有 `wp_galbot_academy.tasks.reach.mdp.rewards_warp_*`。
- **STRICT**（8.9 坑三）：实现方的 `strict_test.py` 我在自己的 GA 环境（warp 1.17.0）里跑了一遍。RELAXED、CHECKED 都不报错，结果正确；STRICT 报 `RuntimeError … LaunchArrayAccessMode.STRICT requires every Warp array argument to be allocated on the launch device`。与页面一致。
- **Warp 源码**：warp 1.17.0 的 `config.py` L115 是 RELAXED；`_src/context.py` L10345–L10348 是"不是 RELAXED 才调 `_validate_launch_array_access`"。一致。
- **`bench_reward_warp.py` 的改动**：删去对 `params["asset_cfg"]` 的再次 resolve，并加了注释说明原因。脚本我在路线 C 跑过，rc=0，比对与计时都正常。
- **链接**：3 页都没有 EA 链接；v3.0.0 链接的起止行都在文件内并且对应所述内容，包括 `cli/__init__.py`、`dispatch.py`、`hydra.py` L466、`install.py` L660–L708 / L841–L878 / L861–L869、`sim_launcher.py`、`physics_manager_cfg.py` L55–L90、`rerun_visualizer_cfg.py` 的端口，以及 renderers / visualization / camera / record_video / ecosystem / migrating 各 rst 的范围。
- **egg-info**：项目工作区里的 `8.7-cli/*.egg-info` 已删除。`conf.py` 只是把 `*.egg-info` 排除出示例打包的遍历。`audit-crossref` 问题 0：我自己快照里残留的那份已从草稿克隆删掉，与项目无关。
- **篇幅**（汉字，不含 front matter）：8.7 2792、8.8 2244、8.9 2168，都 ≤ 3500。
- **构建**：快照 `c57f15b`（`scratch/examine/snap02a`），`-W` 通过（`strict_build_ga04.log`）；`audit-examples` 问题 0。

## 问题

| # | 位置 | 问题 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|---|
| 1 | 8.9 坑四（L139）："奖励模块就在这次调用里编译进空缓存（缓存里该模块目录的时间戳在运行中）；此前 Newton 已在同一进程里编译过自己的内核" | 括号里的证据只能说明"在这次运行中"编译，不能说明"在这次调用里"。另外，按缓存目录的时间戳排序，进程 21:03:10 起跑：Newton 的第一个模块在 21:03:15，奖励模块在 21:03:22.7，但 68 个模块里还有不少 MJWarp 内核编译在它之后（最晚 21:03:29.8）。所以"此前 Newton 已编译过自己的内核"只对一部分成立 | `bench_coldr.summary`（21:03:10–21:03:36）；`ls --time-style` 排序 `warpcache_empty_210309/1.17.0/` | 改为"奖励模块是在这次运行中编译进空缓存的（缓存目录时间戳为 21:03:22，进程 21:03:10 起跑），推断就在这次调用里；在它之前同一进程已编译过部分 Newton 内核"。36.8 ms 与 313 ms 之差仍标推断 | 低 |

## 第 2 轮复核

- **问题 1**：8.9 L139 改为"奖励模块是在这次运行中编译进空缓存的（缓存目录时间戳 21:03:22，进程 21:03:10 起跑），推断就在这次调用里；在它之前，同一进程已编译过部分 Newton 内核（还有一些 MJWarp 内核在它之后才编译）"，与缓存目录的时间戳一致。
- **构建**：快照 `bf86968`，`-W` 通过（`strict_build_ga04_r2.log`）。

结论：**通过**。
