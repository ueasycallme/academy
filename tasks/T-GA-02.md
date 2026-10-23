# T-GA-02 3.0 概念与迁移页升级：8.1 / 8.2 / 8.3 / 8.4 与 A.1 的"3.0 变化"列

状态: 已合并
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

**进度（accomplish，10-23，额度用尽暂停）**：页面还没有改。已查清的事实如下。
- **差异清单**：4 页加 A.1 共引用了 24 个 EA 文件。
  - 搬家：迁移文档 → `docs/source/isaaclab/migrating.rst`；tune_mjwarp → `how-to/solver_tuning_mjwarp.rst`；`_backend_hooks.py` → `backend_hooks.py`。
  - 删除：`concepts/backend_architecture.rst`（内容疑在 `overview/core-concepts/multi_backend_architecture.rst`，未核）、`test_argparser_launch.py`。
  - 其余文件多数有改动，`preset_target.py`、`proxy_array.py`、`find_quaternions.py` 未变。
- **GA 行号**：
  - `backend_utils.py`：FactoryBase L48、`_get_backend` L71、`_get_module_name` L99、`__new__` L146。
  - `simulation_cfg.py`：physics 字段 L114。
  - `hydra.py`：PresetCfg L103、`preset()` L159、匹配逻辑 L310–L335。
  - `physics_manager_cfg.py`：PhysxAutoCfg L55、`_resolve` L68–L95。
  - `sim_launcher.py`：`_get_kit_runtime_sources` L482。
  - `cartpole_common.py`：CartpolePhysicsCfg L30、`default = newton_mjwarp` L53。
- **migrating.rst 各节行号**：Installation 43；Multi-Backend 83（PresetCfg 640、Isaac Sim API 809）；Schema 256；JointDrive 改名 336–385（4.0 删除）；执行器限值 1049（旧名 3.1 删除）、二次截断 1081；ActuatorCollection 1153（GA 新增：`set_joint_position_target` 等弃用 → `actuators.target_command.set_position_index`）；FrameView 1005；Pva 1448；接触力 1548；JointWrench 1601；四元数 1820；ProxyArray 2136/2229；写入拆分 2280；RL 入口 2413；checkpoint 2465；可视化与 headless 2536；Newton 可视化器拆分 2714；录像 2761。
- **`--headless`**
  - migrating.rst L2555 起仍写 `--headless` 与 `--viz` 相互独立，还写 Kit 无头录像要带 `--enable_cameras`。
  - 实测 v3.0.0 里两个参数都不存在：`create_empty.py --headless` 返回 rc=2；`isaaclab train` 的 help 里没有这两个参数。
- **发布页的 EA→GA 条目**（`tga01/rel_v300.md`）：观测噪声 L443、指标返回设备上的张量 L471、`NewtonVisualizerCfg` 拆分 L538、`VideoRecorderCfg` L558、`load_torchscript_model` 抛异常 L583（源码 `isaaclab/utils/io/torchscript.py` L14）。
- **GA 文档用语**
  - Newton 不再标 beta；MJWarp 为 "primary validated solver path"；Kamino 标 experimental。
  - 渲染器预设改为 `newton_renderer` / `ovrtx` / `isaacsim_rtx` / `rtx`。
  - `visualization.rst` L146 仍写 "Most tasks default to a PhysX backend"，与 F4 不符。
- **在跑**：后台 `isaaclab list_envs --show_presets`（路线 A，只占 CPU，timeout 3600），输出到 `scratch/accomplish/tga02/list_envs_presets.txt`，用来统计各任务的默认后端，供 8.1 图 1 的说明用。
- **未做**：8.2 的 Cartpole 换预设重测（GPU）；4 页与 A.1 的改写。

**实现（accomplish，2026-10-23，续）**
- **默认后端统计**：`isaaclab list_envs --show_presets`（路线 A，v3.0.0，用时 3 min，rc=0）列出 139 个注册任务（`tga02/list_envs_presets.txt`），按标 `[default]` 的组合统计：
  - 官方 `Isaac-*` 45 个：Newton 44 个（newton_mjwarp 37、newton_mjwarp_vbd_proxy 6、newton_kamino 1），无预设 1 个（Isaac-Velocity-Rough-G1），默认 isaacsim_physx 的 0 个。
  - `IsaacContrib-*` 94 个：isaacsim_physx 33、无预设 44、Newton 13、其他 4。
  - 8.1 图 1 注照此写，并注明官方 visualization.rst L146 的 "Most tasks default to a PhysX backend" 与 v3.0.0 代码不一致（按设计裁断 ①）。
- **8.2 表 3 在 RTX 5090 上重测**：路线 A，4096 env，100 次迭代，种子 42，每个预设 3 次，原件在 `tga02/p82/`。
  - isaacsim_physx：19–21 s，训练 11.1–11.2 s，0.11 s/迭代，3286 MiB，4.8 GB。
  - newton_mjwarp：17–19 s，8.6–8.7 s，0.08 s，756 MiB，2.4 GB。
  - newton_kamino：30–50 s，21.7–36.9 s（第一次含 Warp 编译），0.21 s，918 MiB，2.4–3.4 GB。
  - physx / ovphysx：都报 `No module named 'ovphysx'`。
  - 不是按 D-032 走"开始计时 / 计时结束"的独占测量，表注照实写。
- **四页改写要点**
  - 提示框改为"基于 v3.0.0 正式版"（note），verified / updated / 版本说明同步，permalink 全部改为 v3.0.0 并逐个核对行号。
  - 8.1：去掉 Newton 的 beta 标签（正式版文档不再分级；MJWarp 为 primary validated，Kamino 为实验性）；时间线补正式版；补一句定位本站没讲的 Isaac Capture、LEAPP、可变形体、浏览器演示。
  - 8.2：成熟度一列删除并注明；补渲染器预设名（`isaacsim_rtx` / `ovrtx` / `newton_renderer` / `rtx`）与 `list_envs --show_presets`；`_backend_hooks.py` 改名为 `backend_hooks.py`。
  - 8.3：Newton 1.6.1、mujoco-warp 3.12.0；调参文档改指 how-to/solver_tuning_*（新增 MPM）；表 3 只留 Cartpole（GA 数字），Galbot 一行改为引 8.5（由 T-GA-03 重测）。
  - 8.4 表 1：全部行号改指 `isaaclab/migrating.rst`。
    - 新增 7 行：AppLauncher → launch_simulation、`--cpu` → `--device cpu`、`--viz newton` / `NewtonVisualizerCfg` 拆分、`set_joint_position_target` → `actuators.target_command`（迁移文档 L1153）、观测噪声回调、指标为设备张量、`load_torchscript_model` 抛 RuntimeError。
    - 无头运行一行按设计裁断 ②：不教 `--headless` / `--enable_cameras`，写明迁移文档 L2536–2607 与发布页的说法与 v3.0.0 代码不一致。实测：`create_empty.py --headless` rc=2；`isaaclab train --help` 里没有这两个参数。
    - 本站 8.5 实测的 4 行标"EA"。
  - A.1："3.0 变化"列改了 AppLauncher、set_joint_position_target、ImplicitActuatorCfg、GaussianNoiseCfg 四行。
- **篇幅**（含表）：8.1 1803、8.2 2367、8.3 1864、8.4 3064。gen_placeholders 跑过；-W 通过。
- **给 T-GA-05（写入 8.6）的"文档与代码不一致"**：① visualization.rst L146 的默认 PhysX 说法；② migrating.rst L2536–2607 与发布页的 `--headless` / `--enable_cameras`；③ `isaaclab train --help` 把 `--rl_library` 写成必填，但省略也能跑（T-GA-01 附记）。
- **补充（accomplish，10-23 19:25）**：校验方发现 19:14 起 GPU 上常驻用户的远程桌面进程 `awesun_desktop`（pid 1339815，652 MiB）。p82 的 summary 显示，Kamino 第 2、3 次与 physx / ovphysx 各次开跑时 procs=1，前面各次为 0。8.2 表 3 的注已照实改写；以后计时开跑前会记下进程名。

**校验（examine，2026-10-23，第 1 轮）**：退回，1 条低级问题，同轮可修，见 `reviews/T-GA-02.md`。
- 8.2 换预设在校验方路线 B 复现，与表 3 一致（显存 3286 / 756 / 918 MiB，迭代 0.11 / 0.08 / 0.21 s；physx 报缺 ovphysx）。
- 8.1 图注的默认后端统计，我独立解析 list_envs 的结果相同（官方 45 个里 Newton 44 个、PhysX 0 个）。
- 5 页的 v3.0.0 链接与 8.4 表 1 的 40 个 migrating.rst 行号逐个核过；新增 7 行与发布页一致。快照 639a38a，-W 通过；篇幅都 ≤ 2673。
- 表 3 注已据实写明 awesun 远程桌面进程（19:14:28 起常驻）。
- 问题 1（低）：8.2 `[^auto]` 写 `physics_manager_cfg.py` L68–L95，但 v3.0.0 的这个文件只有 90 行，应改为 L68–L90（链接改 #L55-L90）。

**实现第 2 轮（accomplish，10-23）**：8.2 [^auto] 行号改为 L68–L90 / #L55-L90（文件共 90 行）。构建等 T-GA-03 计时结束后再跑。

**校验（examine，2026-10-23，第 2 轮）**：通过。8.2 [^auto] 已改为 L68–L90（#L55-L90）；快照 17d1b09，-W 通过。
