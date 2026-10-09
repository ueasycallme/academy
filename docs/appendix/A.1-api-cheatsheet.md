---
title: Isaac Lab 常用 API 速查表
updated: 2026-10-09
sources_checked: 2026-10-09
---

# Isaac Lab 常用 API 速查表

**怎么用这一页**：只收本站正文讲过或示例里用过的 Isaac Lab API，按用途分组。每行给出用途、最常用的两三个参数或字段、v2.3.2 源码里的定义位置，以及本站讲它的页面。没收的 API 查官方 API 文档：<https://isaac-sim.github.io/IsaacLab/v2.3.2/source/api/index.html>。最后一列"3.0 变化"只填 [8.4 迁移指南](../8-frontier/8.4-migration-23-30.md) 里列到的改动，其余写"未核对"。

## 分组速查

**启动**

| API | 用途 | 常用参数 / 字段 | 定义（v2.3.2） | 本站 | 3.0 变化 |
|---|---|---|---|---|---|
| `AppLauncher` | 解析命令行参数并启动 Isaac Sim | `--headless`、`--enable_cameras`、`--device` | [L43](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/app/app_launcher.py#L43) | [3.2](../3-isaacsim/3.2-simulation-app.md) | 未核对 |

**仿真**

| API | 用途 | 常用参数 / 字段 | 定义（v2.3.2） | 本站 | 3.0 变化 |
|---|---|---|---|---|---|
| `SimulationCfg` | 物理步长、设备、PhysX 参数 | `dt`、`device`、`physx` | [L349](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/sim/simulation_cfg.py#L349) | [4.4](../4-isaaclab/4.4-simulation-context.md) | 未核对 |
| `PhysxCfg` | PhysX 求解器与 GPU 缓冲区 | `solver_type`、`gpu_*` | [L20](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/sim/simulation_cfg.py#L20) | [4.4](../4-isaaclab/4.4-simulation-context.md) | 移到 `isaaclab_physx.physics` |
| `SimulationContext` | 仿真的单例：步进、渲染、重置 | `step()`、`reset()` | [L45](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/sim/simulation_context.py#L45) | [4.4](../4-isaaclab/4.4-simulation-context.md) | 未核对 |

**场景**

| API | 用途 | 常用参数 / 字段 | 定义（v2.3.2） | 本站 | 3.0 变化 |
|---|---|---|---|---|---|
| `InteractiveSceneCfg` | 声明场景里的资产与传感器 | `num_envs`、`env_spacing`、`replicate_physics` | [L12](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/scene/interactive_scene_cfg.py#L12) | [4.5](../4-isaaclab/4.5-interactive-scene.md) | 未核对 |
| `InteractiveScene` | 按配置生成、克隆并统一读写各环境 | `scene["robot"]`、`env_origins` | [L47](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/scene/interactive_scene.py#L47) | [4.5](../4-isaaclab/4.5-interactive-scene.md) | 未核对 |
| `SceneEntityCfg` | 在 Term 参数里指定实体与关节、刚体子集 | `name`、`joint_names`、`body_names` | [L21](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/scene_entity_cfg.py#L21) | [4.5](../4-isaaclab/4.5-interactive-scene.md) | 未核对 |

**资产**

| API | 用途 | 常用参数 / 字段 | 定义（v2.3.2） | 本站 | 3.0 变化 |
|---|---|---|---|---|---|
| `AssetBaseCfg` | 资产配置的基类：路径、生成方式、初始状态 | `prim_path`、`spawn`、`init_state` | [L16](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/assets/asset_base_cfg.py#L16) | [4.6](../4-isaaclab/4.6-assets.md) | `init_state.rot` 改为 XYZW |
| `ArticulationCfg` | 机器人配置：USD、初始关节、执行器 | `init_state.joint_pos`、`actuators` | [L16](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/assets/articulation/articulation_cfg.py#L16) | [6.1.6](../6-galbot/1-asset/6.1.6-articulation-cfg.md) | 未核对 |
| `Articulation` | 关节体资产：读状态、写目标 | `data`、`find_joints()`、`find_bodies()` | [L41](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/assets/articulation/articulation.py#L41) | [4.6](../4-isaaclab/4.6-assets.md) | 未核对 |
| `ArticulationData.joint_pos` | 关节位置 | 形状 (num_envs, num_joints) | [L754](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/assets/articulation/articulation_data.py#L754) | [4.6](../4-isaaclab/4.6-assets.md) | 返回 `ProxyArray`，用 `.torch` |
| `ArticulationData.root_pos_w` | 根在世界系的位置 | 形状 (num_envs, 3) | [L1016](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/assets/articulation/articulation_data.py#L1016) | [4.6](../4-isaaclab/4.6-assets.md) | 返回 `ProxyArray` |
| `ArticulationData.body_pos_w / body_quat_w` | 各刚体在世界系的位置、朝向 | 按 `find_bodies()` 的索引取 | [L1056](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/assets/articulation/articulation_data.py#L1056) | [4.6](../4-isaaclab/4.6-assets.md) | `ProxyArray`；四元数 XYZW |
| `Articulation.set_joint_position_target` | 写关节位置目标（下一次写入仿真时生效） | `target`、`joint_ids`、`env_ids` | [L1079](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/assets/articulation/articulation.py#L1079) | [4.6](../4-isaaclab/4.6-assets.md) | 未核对 |
| `Articulation.write_joint_state_to_sim` | 直接改关节位置、速度（重置时用） | `position`、`velocity`、`env_ids` | [L561](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/assets/articulation/articulation.py#L561) | [4.6](../4-isaaclab/4.6-assets.md) | 拆成 `_index` / `_mask` |
| `Articulation.write_root_pose_to_sim` | 直接改根的位姿 | `root_pose`、`env_ids` | [L399](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/assets/articulation/articulation.py#L399) | [4.6](../4-isaaclab/4.6-assets.md) | 拆成 `_index` / `_mask` |
| `RigidObjectCfg / RigidObject` | 单个刚体资产 | `data.root_pos_w` | [L34](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/assets/rigid_object/rigid_object.py#L34) | [4.6](../4-isaaclab/4.6-assets.md) | `data.*` 返回 `ProxyArray` |
| `UsdFileCfg` | 从 USD 文件生成资产 | `usd_path`、`rigid_props`、`articulation_props` | [L74](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/sim/spawners/from_files/from_files_cfg.py#L74) | [2.3](../2-usd-kit/2.3-layers-composition.md) | 未核对 |
| `ArticulationRootPropertiesCfg` | Articulation 根的属性：自碰撞、求解迭代 | `enabled_self_collisions`、`solver_position_iteration_count` | [L15](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/sim/schemas/schemas_cfg.py#L15) | [6.1.4](../6-galbot/1-asset/6.1.4-collision-mass-inertia.md) | 旧名为弃用别名；拆成通用基类 + PhysX 子类 |
| `UrdfConverterCfg / UrdfConverter` | URDF 转 USD | `asset_path`、`fix_base`、`joint_drive` | [L14](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/sim/converters/urdf_converter_cfg.py#L14) | [6.1.2](../6-galbot/1-asset/6.1.2-import-urdf.md) | 未核对 |

**执行器**

| API | 用途 | 常用参数 / 字段 | 定义（v2.3.2） | 本站 | 3.0 变化 |
|---|---|---|---|---|---|
| `ImplicitActuatorCfg` | 由 PhysX 求解的 PD 驱动 | `joint_names_expr`、`stiffness`、`damping` | [L19](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/actuators/actuator_pd_cfg.py#L19) | [4.7](../4-isaaclab/4.7-actuators.md) | `effort_limit_sim` 等字段改名 |
| `IdealPDActuatorCfg` | 在 Python 侧算力矩的显式 PD | `effort_limit` | [L35](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/actuators/actuator_pd_cfg.py#L35) | [4.7](../4-isaaclab/4.7-actuators.md) | 显式执行器的力矩会被求解器再截断一次 |

**环境与 Manager 配置**

| API | 用途 | 常用参数 / 字段 | 定义（v2.3.2） | 本站 | 3.0 变化 |
|---|---|---|---|---|---|
| `ManagerBasedRLEnvCfg` | Manager-based 环境的总配置 | `decimation`、`episode_length_s`、`sim` | [L15](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/manager_based_rl_env_cfg.py#L15) | [4.3](../4-isaaclab/4.3-configclass.md) | 未核对 |
| `ManagerBasedRLEnv` | 按配置组合各 Manager 的环境 | `step()`、`reset()`、`*_manager` | [L25](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L25) | [4.9](../4-isaaclab/4.9-manager-based-env.md) | 未核对 |
| `DirectRLEnv` | 子类直接实现各环节的环境 | `_get_observations()` 等 | [L45](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/direct_rl_env.py#L45) | [4.14](../4-isaaclab/4.14-direct-env.md) | 未核对 |
| `ObservationGroupCfg / ObservationTermCfg` | 观测组与观测项 | `func`、`noise`、`history_length` | [L199](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/manager_term_cfg.py#L199) | [4.10](../4-isaaclab/4.10-observation-action.md) | 未核对 |
| `JointPositionActionCfg` | 关节位置动作 | `joint_names`、`scale`、`use_default_offset` | [L44](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/actions/actions_cfg.py#L44) | [4.10](../4-isaaclab/4.10-observation-action.md) | 未核对 |
| `RewardTermCfg` | 奖励项 | `func`、`weight`、`params` | [L311](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/manager_term_cfg.py#L311) | [4.11](../4-isaaclab/4.11-reward-termination-curriculum.md) | 未核对 |
| `TerminationTermCfg` | 终止项 | `func`、`time_out` | [L339](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/manager_term_cfg.py#L339) | [4.11](../4-isaaclab/4.11-reward-termination-curriculum.md) | 未核对 |
| `CurriculumTermCfg` | 课程项 | `func`、`params` | [L128](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/manager_term_cfg.py#L128) | [4.11](../4-isaaclab/4.11-reward-termination-curriculum.md) | 未核对 |
| `EventTermCfg` | 事件项（重置、随机化） | `func`、`mode`、`params` | [L251](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/manager_term_cfg.py#L251) | [4.12](../4-isaaclab/4.12-event-randomization.md) | 未核对 |
| `CommandTermCfg / UniformPoseCommandCfg` | 目标位姿指令 | `body_name`、`ranges`、`resampling_time_range` | [L133](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/commands/commands_cfg.py#L133) | [4.13](../4-isaaclab/4.13-command-manager.md) | 指令中的四元数为 XYZW |

**常用 mdp 函数**

| API | 用途 | 常用参数 / 字段 | 定义（v2.3.2） | 本站 | 3.0 变化 |
|---|---|---|---|---|---|
| `mdp.joint_pos_rel / joint_vel_rel` | 相对默认姿态的关节位置 / 速度 | `asset_cfg` | [L212](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/observations.py#L212) | [4.10](../4-isaaclab/4.10-observation-action.md) | 未核对 |
| `mdp.last_action` | 上一步动作 | — | [L657](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/observations.py#L657) | [4.10](../4-isaaclab/4.10-observation-action.md) | 未核对 |
| `mdp.generated_commands` | 读出指令作为观测 | `command_name` | [L675](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/observations.py#L675) | [4.13](../4-isaaclab/4.13-command-manager.md) | 未核对 |
| `mdp.action_rate_l2 / joint_vel_l2` | 动作变化率、关节速度惩罚 | `asset_cfg` | [L252](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/rewards.py#L252) | [6.4.1](../6-galbot/4-task/6.4.1-reach.md) | 未核对 |
| `mdp.time_out` | 超时终止 | — | [L31](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/terminations.py#L31) | [4.11](../4-isaaclab/4.11-reward-termination-curriculum.md) | 未核对 |
| `mdp.modify_reward_weight` | 到指定步数时改奖励权重 | `term_name`、`weight`、`num_steps` | [L24](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/curriculums.py#L24) | [4.11](../4-isaaclab/4.11-reward-termination-curriculum.md) | 未核对 |
| `mdp.reset_joints_by_offset` | 在默认姿态上加随机偏移重置关节 | `position_range`、`velocity_range` | [L1278](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/events.py#L1278) | [4.12](../4-isaaclab/4.12-event-randomization.md) | 未核对 |
| `mdp.reset_scene_to_default` | 把场景恢复到默认状态 | `reset_joint_targets` | [L1360](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/events.py#L1360) | [4.12](../4-isaaclab/4.12-event-randomization.md) | 未核对 |
| `mdp.randomize_rigid_body_mass / randomize_actuator_gains` | 质量、执行器增益的域随机化 | `mass_distribution_params`、`operation` | [L286](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/events.py#L286) | [6.4.2](../6-galbot/4-task/6.4.2-domain-randomization.md) | 未核对 |

**工具**

| API | 用途 | 常用参数 / 字段 | 定义（v2.3.2） | 本站 | 3.0 变化 |
|---|---|---|---|---|---|
| `configclass` | 把类变成可嵌套、可覆盖的配置 | `replace()`、`validate()` | [L31](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/utils/configclass.py#L31) | [4.3](../4-isaaclab/4.3-configclass.md) | 未核对 |
| `math.quat_from_euler_xyz` | 欧拉角转四元数 | `roll`、`pitch`、`yaw` | [L274](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/utils/math.py#L274) | [8.4](../8-frontier/8.4-migration-23-30.md) | 输出改为 XYZW |
| `math.combine_frame_transforms` | 两个坐标变换相乘（如根系 → 世界系） | `t01`、`q01`、`t12`、`q12` | [L801](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/utils/math.py#L801) | [6.2.1](../6-galbot/2-scene/6.2.1-workbench-scene.md) | 四元数按 XYZW |
| `VisualizationMarkers` | 在场景里画标记（目标、坐标系） | `visualize(translations, orientations)` | [L55](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/markers/visualization_markers.py#L55) | [7.3](../7-infra/7.3-debugging.md) | 未核对 |
| `GaussianNoiseCfg` | 给观测加高斯噪声 | `mean`、`std` | [L56](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/utils/noise/noise_cfg.py#L56) | [4.10](../4-isaaclab/4.10-observation-action.md) | 未核对 |

**RL 适配层与任务工具**

| API | 用途 | 常用参数 / 字段 | 定义（v2.3.2） | 本站 | 3.0 变化 |
|---|---|---|---|---|---|
| `RslRlOnPolicyRunnerCfg` | rsl_rl 训练配置 | `num_steps_per_env`、`max_iterations`、`obs_groups` | [L231](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_rl/isaaclab_rl/rsl_rl/rl_cfg.py#L231) | [4.16](../4-isaaclab/4.16-rl-wrappers.md) | 训练入口改为 `isaaclab train` |
| `RslRlPpoAlgorithmCfg` | PPO 超参数 | `learning_rate`、`entropy_coef`、`gamma` | [L76](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_rl/isaaclab_rl/rsl_rl/rl_cfg.py#L76) | [5.3](../5-rl/5.3-ppo.md) | 未核对 |
| `RslRlVecEnvWrapper` | 把环境接成 rsl_rl 的接口 | `clip_actions` | [L14](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_rl/isaaclab_rl/rsl_rl/vecenv_wrapper.py#L14) | [4.16](../4-isaaclab/4.16-rl-wrappers.md) | 未核对 |
| `isaaclab_rl.rsl_rl.exporter` | 导出策略（只含 actor）；play.py 调用 | `path`、`filename` | [L25](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_rl/isaaclab_rl/rsl_rl/exporter.py#L25) | [6.6.1](../6-galbot/6-eval/6.6.1-play-replay.md) | 未核对 |
| `parse_env_cfg` | 按任务名取环境配置 | `num_envs`、`device` | [L120](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_tasks/isaaclab_tasks/utils/parse_cfg.py#L120) | [4.15](../4-isaaclab/4.15-task-registration.md) | 未核对 |
| `get_checkpoint_path` | 按运行名、检查点名找文件 | `run_dir`、`checkpoint` | [L160](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_tasks/isaaclab_tasks/utils/parse_cfg.py#L160) | [6.6.1](../6-galbot/6-eval/6.6.1-play-replay.md) | 改为统一的 `--checkpoint` |

*表 1–9：按用途分组。"定义"一栏链接到 v2.3.2 源码中类或函数的定义行；`mdp.*` 指 `isaaclab.envs.mdp`，`math.*` 指 `isaaclab.utils.math`。*

## 常见组合

这一节回答：几个最常用的操作，代码怎么写？

```python
# 取某个刚体（如末端）在世界系的位姿：先按名字找索引，再从 data 里取（4.6）
body_ids, _ = robot.find_bodies("right_arm_link7")
pos, quat = robot.data.body_pos_w[:, body_ids[0]], robot.data.body_quat_w[:, body_ids[0]]   # 四元数 (w, x, y, z)
```

```python
# 设关节位置目标：只写进缓存，下一次 write_data_to_sim() 时交给执行器（4.6 表 2）
joint_ids, _ = robot.find_joints("right_arm_joint[1-7]")
robot.set_joint_position_target(target, joint_ids=joint_ids)
```

```python
# 重置若干环境的关节：直接写状态，跳过物理（4.6 表 2；常用于 reset 事件）
robot.write_joint_state_to_sim(joint_pos, joint_vel, env_ids=env_ids)   # joint_pos / joint_vel 形状 (len(env_ids), 关节数)
```

```python
# 读当前指令，以及某个环境的各项奖励值（4.13、7.3）
cmd = env.command_manager.get_command("ee_pose")             # 根坐标系下的 (x, y, z, qw, qx, qy, qz)
terms = env.reward_manager.get_active_iterable_terms(0)       # [(名字, [值]), …]，值未乘 dt
```

```python
# 在 Term 参数里只取右臂关节（4.5、6.4.1）
asset_cfg = SceneEntityCfg("robot", joint_names=["right_arm_joint[1-7]"])
```

*以上片段取自对应页面的讲解与示例，变量名略有简化。3.0 中的写法见 8.4（数据要加 `.torch`，四元数改为 XYZW，写入方法改名）。*

## 维护规则

正文页第一次讲到一个本表没有的 Isaac Lab API 时，写页的会话在对应分组里加一行：名字（行内代码）、一句话用途、不超过三个常用参数、v2.3.2 定义行的 permalink（指向 `class` 或 `def` 那一行）、本站页面。"3.0 变化"一栏只按 8.4 填，8.4 更新时一并更新这一栏。不收本站没用过的 API。

## 延伸阅读

- 官方 API 文档（v2.3.2）：<https://isaac-sim.github.io/IsaacLab/v2.3.2/source/api/index.html>
- 仓库结构：[4.2](../4-isaaclab/4.2-repo-map.md)；Isaac Sim 侧的 API：[3.11](../3-isaacsim/3.11-api-map.md)

## 版本说明

本页基于 Isaac Lab 2.3.2，3.0 的变化只列 8.4 涉及的部分，见 [8.6 版本追踪](../8-frontier/8.6-version-tracking.md)。
