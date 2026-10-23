# T-GA-03 校验报告：Galbot 在 3.0 正式版上（8.5 / 8.10 重训、重评、重转换）

校验 session：isaac-academy-examine，2026-10-23
结论：**通过**（第 1 轮；1 条建议，不阻塞）

- 三个检查点在校验方自己的 GA 环境里各重评一次，结果都落在页面给出的值或范围内。
- 关节顺序、Newton 冒烟训练都复现了；计时原件符合 D-032 补注（007938b）。
- 页面数字与原始日志逐项对得上。

## 复现（RTX 5090 32 GB，驱动 580.178.04；非计时；日志 `scratch/examine/ga03/`）

**环境与用法**：
- 用校验方的路线 B GA 环境（`envGA/env_isaaclab30_ga`：isaacsim 6.2.0.0、Isaac Lab v3.0.0 检出）。
- 示例包拷到 `ga03/pkg` 后用 `PYTHONPATH` 指过去，照 README"外部任务不需要安装"的用法。这个包没有 `pyproject` / `setup.py`，卡上写的"`pip install -e`"不适用。
- 资产用实现方的 `tga03/gen`：`galbot_fixed_base_30` 是在 6.2 上重转的。
- 开跑前记了 `nvidia-smi`（`gpu_before.txt`、`gpu_before_full.txt`）。

| 项 | 命令 | 结果 | 页面 |
|---|---|---|---|
| PhysX s42 → PhysX | `eval_reach.py --checkpoint …/physx_s42/model_999.pt physics=isaacsim_physx` | 5.36 cm / 46.6% / 0.063 rad | 8.5 表 2、表 4，8.10 表 2：5.36 / 46.6% / 0.063，一致（PhysX 逐位相同） |
| Newton s42 → Newton | `… newton_s42 … physics=newton_mjwarp` | 3.49 cm / 74.3% / 0.155 rad | 3.49–3.56 / 74.2%–74.6% / 0.151–0.157，落在范围内 |
| 2.3 转换后 → PhysX | `--checkpoint model23_as30.pt --load_models_only --cmd_quat_wxyz physics=isaacsim_physx` | 2.75 cm / 81.5% / 0.067 rad；日志中的环境路径是 `envGA/env_isaaclab30_ga` | 2.75 / 81.5% / 0.067，一致 |
| 关节顺序 | `print_ordering.py` 两个后端 | 都是 33 个关节；`right_arm_joint2` 的序号 PhysX 为 10、Newton 为 21 | 8.10 表 1，一致 |
| 冒烟 | `isaaclab train … --task Galbot-Reach --external_callback galbot_academy.register_tasks --max_iterations 10 --seed 42 physics=newton_mjwarp` | rc=0，第 9/10 次迭代平均奖励 -1.27；第一次启动即成功 | 示例包在 GA 上能导入并训练 |

**设计方要求多核的一点（2.3 转换后与 EA 逐位相同）**：
- 实现方的 `eval_c23w_on_px_*.log` 里，环境路径都是 `IsaacLab-3.0-GA/.venv`（Kit 的 user config 位于 `…/IsaacLab-3.0-GA/.venv/…/Kit/IsaacLab/3.0/`）。日志里没有 EA 检出（`IsaacLab-3.0/`）的路径。
- 日志本身不打印 isaacsim 版本号。不过那个 `.venv` 就是 T-GA-01 F7 记录的 isaacsim 6.2.0.0 环境。
- 我在另一个独立的 GA 环境里重评，得到同样的 2.75 / 81.5% / 0.067，所以"逐位相同"不是用错环境造成的。
- 8.10 L75 由此推出"3.0 的 PhysX 在这个任务上的行为与 2.3 基本一致，策略差距更可能在训练一侧"，标了推断，并写明这一对照只排除了 PhysX 本身。写法恰当。

**Newton 41% → 74%**：按设计意见（D-035 第 4 条），写成"EA 时为 41%，本站未查原因"即可，不要求查因。8.5 L103 写"< 5 cm 从 41% 升到 74%"，L106 写"差异原因没有查"，符合。L103 的"快约 3.8 倍、主机内存少 4.2 GB、显存多 2.2 GB"按表 2 算出来是 1.38/0.36 = 3.83、7.0 − 2.8、(5566 − 3332)/1024 = 2.18 GiB，一致。

## 原件核对（`scratch/accomplish/tga03/`）

- **评估**：24 份 `eval_*.log` 逐份读了中位数、< 5 cm、姿态、最大误差，与 8.5 表 2、表 4 和 8.10 表 2 的每一格一致。
  - PhysX→Newton 的最大误差 71.96–148.00 cm，Newton→Newton 10.15–10.71 cm，2.3 原样 65.55 cm，c23w→PhysX 11.94 cm，c23w→Newton 200.87–215.50 cm。
  - PhysX 上 3 次评估逐位相同。
- **Wilson 区间**（n = 768）我重算了：358 → 43.1%–50.2%；0 → 0%–0.5%；626 → 78.6%–84.1%；PhysX→Newton 三次合起来 23.6%–31.5%；c23w→Newton 三次合起来 3.1%–7.8%。都与 8.10 表 2 一致。
- **计时**：
  - `train_physx43.summary` 19:48:32–20:11:55 = 1403 s，3332 MiB，RSS 7163 MiB；
  - `train_newton42.summary` 20:12:26–20:18:38 = 372 s，5566 MiB，RSS 2891 MiB；
  - "启动与收尾"18 s、11 s 与"墙上时间 − 训练用时"一致；
  - 两场的 `gpu_before_*.txt` 都是空的，`gpu_watch_train_*.log` 每 30 s 一条，分别 46 条、12 条，每条都只有训练进程本身；
  - s42 那场作废的时间线在 `NOTE_timing.txt` 里：awesun 在开跑时还在，19:33:09 的第一条 30 s 记录里已经没有它。
- **Newton 启动次数**：13 次 = 冒烟 1、关节顺序 1、训练 1、评估 9（3 个检查点 × 3）、阶跃 1。没有任何 `*.try2.log`，0 次崩溃成立。8.10 坑四的"8 次"是顺序 1、阶跃 1、两个检查点各 3 次评估，也对得上。

## 来源与页面

- **链接**：8.5、8.10 的 IsaacLab 链接都已改指 v3.0.0（0 个 EA 链接），起止行都在文件内并且对应所述内容：
  - `hydra.py` L442–L490 `resolve_task_config`（取代已删除的 `hydra_task_config`）；
  - `train_rsl_rl.py` L69–L83；`string.py` L486–L501；`commands_cfg.py` L152；
  - `transfer_policies_between_physx_and_newton.rst` L19–L65、L101–L119、L335–L435、L436–L450；
  - `solver_differences.rst` L131–L238；`prepare_asset_for_newton.rst` L32–L47。
  - EA 时单独的 ordering 文档在正式版里并进了 transfer 文档，脚注已写明。
- **图 1**（`8.10-step-compare.png`）：1200×630，`plot_step_30.py` 仍是 13 pt / 150 dpi、图例 12 pt，与 T-8.10 校验时相同（约 18.5 px，≥ 12 px，D-025）。
- **示例**：`audit-examples` 问题 0；`convert_galbot_30.py` 的 GPU 写在 README 里，按 D-029 豁免。
- **篇幅**（汉字，不含 front matter）：8.5 3128、8.10 2511，都 ≤ 3500。8.5 已接近上限。
- **构建**：快照 `83a8317`（`scratch/examine/snap02a`），`-W` 通过（`strict_build_ga03.log`）。

## 建议（不阻塞）

**建议 1**：8.5 表 3 注有一处重复。"每次的日志单独保存"出现了两次，后一处在括号里，括号里的"含冒烟、训练、评估三种启动"与前面列的 5 类也不一致。可以删掉括号。

**附带发现（不属于本卡）**：工作区里出现了未跟踪的 `examples/isaaclab-3.0/8.7-cli/academy_cli_demo.egg-info/`，创建于 20:35，应该是 T-GA-04 期间 `pip install -e` 留下的。`.gitignore` 没有忽略它，`audit-crossref` 把它报为孤儿文件。合并前要么删掉，要么不 `git add`。
