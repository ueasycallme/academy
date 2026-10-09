# T-A.1 校验报告：Isaac Lab 常用 API 速查表

- 校验日期：2026-10-09
- 校验 session：isaac-academy-examine
- 范围：`docs/appendix/A.1-api-cheatsheet.md`
- 核对脚本：`reviews/scripts/T-A.1-check-defs.py`。对每一行执行两项检查：
  1. 用 `git show v2.3.2:<路径>` 取出 permalink 指向的那一行，确认它是该名字的 `class` 或 `def`；
  2. 确认名字出现在所链接的站内页面里。

## 结论：退回

52 行全部核对了一遍，不止抽查的 15 行。定义行、站内页面、常用参数都没有问题。退回只为 3 个 3.0 单元格：它们的出处是 8.1，不是本页声明的 8.4。改几个字即可。

## 问题表

| # | 位置 | 问题 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|---|
| 1 | "3.0 变化"列：`Articulation`（"工厂分发到后端实现，导入不变"）、`ManagerBasedRLEnv` 和 `DirectRLEnv`（"类仍在"） | 导语和维护规则都说这一列"只填 8.4 里列到的改动"，但这三格的内容在 8.4 里找不到，出处是 8.1：L63–64 讲工厂分发，L64 说导入不用改，L96 说两个类仍在 `isaaclab.envs` 里。内容本身是对的，8.1 也有脚注，只是与本页声明的口径不符；任务卡的验收标准是"与 8.4 页一致" | grep 8.4 中的"Articulation\|分发\|ManagerBased\|Direct"，只命中 Schema 与执行器两行 | 二选一：① 导语与维护规则改为"按 8.1、8.4 填"，这三格分别链接 8.1；② 这三格改为"未核对" | 低 |

## 核对结果

**定义行（52/52）**：每个 permalink 行都是对应的 `class X` 或 `def x(`。以下几行容易出错，逐一确认过：

| 行 | 所指的定义 |
|---|---|
| `RigidObjectCfg / RigidObject` | `rigid_object.py` 中的 `class RigidObject` |
| `ObservationGroupCfg / ObservationTermCfg` | `ObservationGroupCfg` |
| `CommandTermCfg / UniformPoseCommandCfg` | `commands_cfg.py` L133 的 `class UniformPoseCommandCfg(CommandTermCfg)` |
| `mdp.modify_reward_weight` | v2.3.2 中是类 `class modify_reward_weight(ManagerTermBase)` |
| `randomize_rigid_body_mass` | 同样是类 |
| `isaaclab_rl.rsl_rl.exporter` | L25 的 `def export_policy_as_onnx(` |

如果名字中有 `/`，指向其中第一个名字。这在表注"类或函数的定义行"的范围内，可以接受。

**站内页面（52/52）**：每行名字中的各段都出现在所链接的页面里。

**常用参数（抽查 10 个，都对得上）**：在 v2.3.2 源码中都找到了对应的参数或字段：

- `get_checkpoint_path(log_path, run_dir, checkpoint, …)`；
- `export_policy_as_onnx(policy, path, normalizer, filename, …)`；
- `RslRlVecEnvWrapper.__init__(env, clip_actions)`；
- `VisualizationMarkers.visualize(translations, orientations, …)`；
- `reset_scene_to_default(…, reset_joint_targets)`；
- `modify_reward_weight` 的 params：`term_name`、`weight`、`num_steps`；
- `randomize_rigid_body_mass` 的 `mass_distribution_params` 与 operation；
- `UrdfConverterCfg` 的 `fix_base`、`joint_drive`，以及基类的 `asset_path`。

**3.0 列与 8.4 的对照**：

- 以下各格都能在 8.4 找到出处：
  - `PhysxCfg` 移到 `isaaclab_physx.physics`：8.4 表 1 L41；
  - Schema 类旧名作为弃用别名：L42；
  - 执行器字段改名：L44；
  - 显式执行器被再截断一次：L45；
  - `write_*` 拆成 `_index` 和 `_mask`：L46 等；
  - `ProxyArray` 与 `.torch`：L81、L138；
  - 四元数 XYZW，含 `quat_from_euler_xyz`：L67；
  - `init_state.rot`：L68；
  - 指令的四元数：L101；
  - `isaaclab train` 与 `--checkpoint`。
- 只有问题 1 中的三格不在 8.4。

**常见组合**：

- 第一段的注释"四元数 (w, x, y, z)"与 2.3.2 的约定一致。
- `set_joint_position_target` 只写缓存，要等 `write_data_to_sim()`，与 4.6 一致。
- `get_active_iterable_terms` 的值是 `_step_reward`，即 func × weight，没有乘 dt。这与校验方在 T-7.3 / T-4.11 核对过的源码一致。

**其他**：

- 官方 API 索引链接返回 200。
- `tools/check_head_build.sh --worktree`（-W）通过。

---

## 第二轮（2026-10-09）：通过

- 问题 1 已修：`Articulation`、`ManagerBasedRLEnv`、`DirectRLEnv` 三格改为"未核对"，与"只按 8.4 填"的口径一致。
- 3.0 列共 52 格：
  - 36 格为"未核对"；
  - 其余 16 格都已在第一轮逐一对上 8.4 的出处（PhysxCfg、Schema 别名、执行器字段、再截断、`_index`/`_mask`、`ProxyArray`、XYZW、`isaaclab train`、`--checkpoint`），本轮这些格没有改动。
- 定义行脚本复跑：52 行中只有 `isaaclab_rl.rsl_rl.exporter` 一行被脚本标出。原因是它写的是模块名，第一轮已核实指向 `export_policy_as_onnx` 的定义，可以接受。
- 上一轮提到的 A.5 xref 警告已修复。`tools/check_head_build.sh --worktree`（-W）通过。
