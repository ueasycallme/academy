# T-GA-02 校验报告：8.1 / 8.2 / 8.3 / 8.4 与 A.1 的"3.0 变化"列升级到 v3.0.0

校验 session：isaac-academy-examine，2026-10-23
结论：**通过**（第 2 轮；第 1 轮的低级问题已修，见文末）

- 8.2 换预设已复现，8.1 图 1 与 F4 一致；新增与改写的来源大都核过。
- 唯一的问题是 8.2 一个脚注的行号超出了文件长度（问题 1）。
- 校验期间发现 GPU 上有用户的远程桌面进程，已据实写进 8.2 表 3 注（见"表 3 的测量条件"）。

## 复现：8.2 Cartpole 换预设（RTX 5090 32 GB，驱动 580.178.04；非计时；校验方路线 B；日志 `scratch/examine/envGA/ga02/`）

命令与页面相同：`isaaclab train --rl_library rsl_rl --task Isaac-Cartpole-Direct --max_iterations 100 --seed 42 physics=<预设>`，每个预设跑 1 次。

| 预设 | 墙钟 | 训练用时 | 每次迭代 | 按进程显存峰值 | 主机 RSS 峰值 | 最后一轮 | 表 3 |
|---|---|---|---|---|---|---|---|
| `isaacsim_physx` | 20.0 s | 11.78 s | 0.11 s | 3286 MiB | 4966 MiB | 4.95 / 300 | 19–21 s / 11.1–11.2 s / 0.11 s / 3286 MiB / 4.8 GB |
| `newton_mjwarp` | 17.2 s | 8.89 s | 0.08 s | 756 MiB | 2566 MiB | 4.94 / 300 | 17–19 s / 8.6–8.7 s / 0.08 s / 756 MiB / 2.4 GB |
| `newton_kamino` | 30.5 s | 21.72 s | 0.21 s | 918 MiB | 2554 MiB | 4.93 / 300 | 30–50 s / 21.7–36.9 s / 0.21 s / 918 MiB / 2.4–3.4 GB |
| `physx` | 2.3 s，rc=1 | — | — | — | 890 MiB | `ModuleNotFoundError: No module named 'ovphysx'` | 失败 |

- 显存、每次迭代用时、失败方式与表 3 一致；Kamino 落在表 3 范围内（我的环境里 Warp 内核早已编译过）。
- PhysX 训练用时比表 3 多约 0.6 s。我这次不独占，且 GPU 上有远程桌面进程（见下），不作比较。

**表 3 的测量条件**：我每次开跑前都用 `nvidia-smi` 计数，结果都 ≥ 1。查出来是 `/usr/local/awesun/bin/awesun_desktop`（用户的远程桌面，常驻约 652 MiB，`lstart` 为 19:14:28）。
- 实现方 `p82/*.summary` 的 `procs=` 一栏：Kamino 第 1 次之前都是 0；从 Kamino 第 2 次（19:14:51 开跑）起都是 1，时间与 awesun 的启动对得上。
- 原表注写"开跑前 GPU 上没有其他进程"，不成立；实现方已改为"从 Kamino 第 2 次起，GPU 上另有一个常驻的远程桌面进程（约 650 MiB），对数字的影响没有单独测"。现在的写法成立。
- `gpu_before.txt` 只在开头记了一次，但 `run.sh` 在每次 summary 的首行都记了 `procs=`，所以每次开跑前的情况都有据可查。

## 8.1 图 1 与默认后端

- **图注**："45 个官方 `Isaac-*` 任务里 44 个默认 Newton（37 个 `newton_mjwarp`），没有一个默认 Isaac Sim PhysX"。我自己解析了 `tga02/list_envs_presets.txt`（139 个任务，按 `[default]` 一行的 `physics=` 统计），结果是：
  - 官方任务：`newton_mjwarp` 37、`newton_mjwarp_vbd_proxy` 6、`newton_kamino` 1、无 physics 预设 1；
  - `IsaacContrib-*` 94 个：`isaacsim_physx` 33、Newton 13、其余 48（实现方分成"无预设 44 + 其他 4"）。
  - 与图注一致。
- **与 F4 一致**：三个实测任务都是 `newton_mjwarp`（T-GA-01 校验）；Cartpole 的默认值在 `cartpole_common.py` L53。
- 8.1 L126、L132 改为"官方任务多数默认 Newton；社区贡献任务里不少默认 `isaacsim_physx`"，与统计一致。
- 官方 `visualization.rst` L146 仍写"Most tasks default to a PhysX backend"，页面照实指出它与 v3.0.0 代码不一致，已交给 T-GA-05 写进 8.6。

## 来源核对（逐个打开 v3.0.0 的起止行）

- **5 页的 IsaacLab 链接**：0 个 `v3.0.0-EA`；8.1 有 13 个 `v3.0.0` 链接，8.2 有 15 个，8.3 有 4 个，8.4 有 14 个。A.1 的 3.0 列只有文字，没有新链接。
  - 起止行都在文件内并且对应所述内容，除了问题 1。
  - 抽看的有：`backend_utils.py` L48–L146；`hydra.py` L103–L177、L310–L335；`simulation_cfg.py` L114；`sim_launcher.py` L482–L499、L595；`app_launcher.py` L41–L50（弃用警告）；`torchscript.py` L14–L37（抛 `RuntimeError`；EA 版 L40 是 `return None`）；`preset_target.py` L35–L66；`math.py` L157（xyzw）。
- **8.4 表 1 的 `migrating.rst` 行号**（40 个起止行，逐个打开）：各行都从对应的 `.. rubric::` 开始，到下一节之前的空行结束。
  - 例如：L43 Installation、L121 Multi-Backend、L640 PresetCfg、L809 Isaac Sim API、L1049 执行器名、L1153 ActuatorCollection、L1820 四元数、L2136 ProxyArray、L2280 写入拆分、L2413 RL 入口、L2465 检查点参数、L2536 Visualizer CLI and Headless、L2714 Newton 可视化器拆分、L2761 录像。
  - L1081–L1088 是执行器一节里讲"二次截断"的那一段，L1088 原文有"clipped a second time by the solver"。
- **新增的 7 行**与发布页（`tga01/rel_v300.md`）的对应条目一致：
  - L443 观测噪声回调（"no longer creates a defensive copy"）；
  - L471 指标改为零维设备张量；
  - L538 `NewtonVisualizerCfg` 拆分；
  - L558 `VideoRecorderCfg`；
  - L583 `load_torchscript_model` 抛 `RuntimeError`；
  - `migrating.rst` L2733 写明 `--viz newton` 是"deprecated alias"。
  - `actuator_collection.py` L715 有 `set_position_index`，`base_articulation.py` L3238 的 `set_joint_position_target` 仍在。
- **A.1**：`--headless`、`--enable_cameras` 在 v3.0.0 的 `isaaclab/app/` 里已不存在（grep 0 处），`set_joint_position_target` 的去向与上面一致。四行与 8.4 同步。
- **8.1 L118**（本站未展开的几项）：Isaac Capture、LEAPP 导出、可变形体与粒子、浏览器演示，在发布页 L212–L213、L203、L74 都能找到。

## 页面检查

- 页顶提示框、`verified:`、版本说明都改成了 v3.0.0；8.1 的 `verified:` 写明"默认物理后端实测过，其余断言未逐条实测"。
- **篇幅**（汉字，不含 front matter，含脚注）：8.1 1743、8.2 2164、8.3 1570、8.4 2673，都 ≤ 3500（D-027）。
- **构建**：快照 `639a38a`（`scratch/examine/snap02a`），`-W` 通过（`strict_build_ga02.log`）。

## 问题

| # | 位置 | 问题 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|---|
| 1 | 8.2 脚注 `[^auto]`："`_resolve_physx_auto_cfg` L68–L95"，链接 `physics_manager_cfg.py#L55-L95` | v3.0.0 的 `physics_manager_cfg.py` 只有 90 行，函数在 L68–L90（L90 是 `return selected`）。L95 是 EA 时的行号，没跟着改 | `wc -l`；`nl` 原文 | 改为 L68–L90，链接改为 `#L55-L90` | 低 |

## 第 2 轮复核

- **问题 1**：8.2 `[^auto]` 已改为 `_resolve_physx_auto_cfg` L68–L90，链接改为 `#L55-L90`，与 v3.0.0 的 `physics_manager_cfg.py`（90 行）一致；页面不再有 L95。
- **构建**：快照 `17d1b09`，`-W` 通过（`strict_build_ga02_r2.log`）。构建是在实现方说"计时结束"之后跑的。

结论：**通过**。
