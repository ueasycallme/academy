# galbot_academy：Isaac Academy 第 6 部分主线项目

一台机器人（Galbot One Golf）从资产到训练出第一个策略的完整项目，随第 6 部分各页逐步增长。对应页面从 `docs/6-galbot/1-asset/6.1.1-galbot-repo.md` 开始。

- 验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2 + rsl-rl-lib 3.1.2
- 验证日期：2026-09-30；GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04

## 来源

项目骨架由 Isaac Lab v2.3.2 的模板生成器生成（见 4.18）。生成时的选择：外部项目，名称 `galbot_academy`，Manager-based 单智能体，RSL-RL 的 PPO。在此基础上精简：

- **删除**：模板的占位任务（Cartpole）、`.vscode/`、Docker 与代码风格配置、`ui_extension_example.py`、项目级 `pyproject.toml`、`docs/CHANGELOG.rst`。
- **修改**：
  - `galbot_academy/__init__.py` 不再导入 `tasks` 与 UI 扩展，使纯 Python 工具不启动 Isaac Sim 也能用；任务由各脚本显式 `import galbot_academy.tasks` 注册，模板生成的脚本本来就是这样。
  - `scripts/list_envs.py` 的过滤条件由"ID 含 `Template-`"改为"ID 以 `Galbot-` 开头"：本项目的任务 ID 统一用 `Galbot-` 前缀；而只写"含 `Galbot-`"会把 Isaac Lab 自带的 `Isaac-Stack-Cube-Galbot-*` 也列出来。
  - `config/extension.toml` 的标题与描述。
- **新增**（6.1.1）：`galbot_academy/assets/paths.py`、`scripts/fetch_galbot.sh`、`scripts/galbot_joint_stats.py`、`.gitignore`。
- **新增**（6.1.2）：`scripts/convert_galbot.py`、`scripts/check_galbot_usd.py`。
- **新增**（6.1.3）：`scripts/compare_usd.py`、`scripts/hold_pose.py`。

## 资产：Galbot One Golf 描述仓库

- 仓库：<https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description>
- 固定 commit：`2d496b053f0d4e9e2688f59fac66022f447226be`（2026-09-11）
- 许可：Apache License 2.0，版权归原作者（GalaxyGeneralRobotics）。本项目**不分发**其任何文件，读者用脚本自行克隆。

目录约定（`galbot_academy/assets/paths.py`）：

| 用途 | 环境变量 | 默认值 |
|---|---|---|
| Galbot 描述仓库 | `GALBOT_DESCRIPTION_DIR` | `<项目根>/third_party/galbot_one_golf_description` |
| 本项目生成的资产（转换得到的 USD 等，不提交） | `GALBOT_GENERATED_DIR` | `<项目根>/generated` |

## 安装与验证（6.1.1 结束时）

在项目根目录、用装有 Isaac Lab 的 Python 环境执行：

```bash
bash scripts/fetch_galbot.sh                     # 克隆并固定到 2d496b0，约 6 秒，约 76 MB
python -m pip install -e source/galbot_academy
python scripts/galbot_joint_stats.py             # 不需要 Isaac Sim
python scripts/list_envs.py                      # 此时还没有任务，表格为空（脚本内部固定 headless）
```

`galbot_joint_stats.py` 的预期输出（节选）：

```text
== galbot_one_golf.urdf：连杆 104，关节 103，按类型 {'fixed': 26, 'revolute': 33, 'continuous': 44}
  底盘主动轮          4 个可动关节
  全向轮被动滚子       40 个可动关节
  腿 / 躯干升降       5 个可动关节
  头              2 个可动关节
  右臂             7 个可动关节
  右夹爪            6 个可动关节（其中 mimic 5 个，独立自由度 1）
  ...
== galbot_one_golf_fixed_base.urdf：连杆 64，关节 63，按类型 {'fixed': 30, 'revolute': 33}
```

`list_envs.py` 返回码 0，约 4 秒，打印空表。把输出重定向到文件时，请设置 `PYTHONUNBUFFERED=1`，否则表格可能在 `simulation_app.close()` 前来不及写出。

## 6.1.2：URDF → USD

```bash
python scripts/convert_galbot.py --headless       # 固定底座版 URDF + fix_base，输出 generated/galbot_fixed_base/galbot.usd
python scripts/check_galbot_usd.py --headless     # 仿真检查：保持零位、夹爪 mimic 联动
```

预期输出（本站实测，转换约 6 秒、检查约 8 秒，返回码 0）：

```text
Generated USD file: <项目根>/generated/galbot_fixed_base/galbot.usd
mimic 关节 10 个：naturalFrequency = 1000.0，dampingRatio = 1.0
galbot.usd（fixed_base）：关节 33，刚体 34，根固定 True
保持零位 2 s：驱动关节最大偏离 0.0355 rad（right_arm_joint2），平均 0.0050 rad
right_gripper_joint 目标 0.8 → 实际 +0.8018
  right_gripper_r_inner_knuckle_joint    -0.8045（期望 -0.8018）
  right_gripper_r_finger_joint           +0.7999（期望 +0.8018）
  right_gripper_l_knuckle_joint          +0.7999（期望 +0.8018）
  right_gripper_l_inner_knuckle_joint    +0.7980（期望 +0.8018）
  right_gripper_l_finger_joint           -0.8026（期望 -0.8018）
```

- 转换日志中有 30 条 `DEPRECATION WARNING: Merging bodies with inertia is deprecated`，以及 `Unresolved reference … </visuals/head_link1>` 警告，均属预期。
- `--variant wheeled` 转换轮式 URDF 作对照（78 个刚体）。它的根同样是固定的，**仿真时要离地放置或不放地面**，否则滚子一开始就压进地面 3.2 cm，保持零位时出现 NaN（6.1.2 表 4）：

  ```bash
  python scripts/hold_pose.py --headless --usd generated/galbot_wheeled/galbot.usd --z 0.05     # 或 --no_ground
  ```

  预期输出（约 16 秒，按进程显存 2315 MiB）与固定底座版相同：`驱动关节最大偏离 0.0355 rad（right_arm_joint2）…数值有限 True`、`实际 +0.8018，mimic 最大跟随误差 0.0038 rad`。不加 `--z` 时输出 `数值有限 False`。滚子的小阻尼（0.1）是经验性设置，不是防 NaN 的手段。
- 检查脚本按进程测得的显存峰值为 2315 MiB。
- **转换失败时进程返回码仍可能为 0**，请以 `Generated USD file` 一行与输出文件是否存在为准。

## 6.1.3：厂商 USD 与自导入 USD 的对比

```bash
python scripts/compare_usd.py                     # 只需 usd-core；比较厂商 USD 与 generated/ 下的两份转换结果
python scripts/hold_pose.py --headless --usd generated/galbot_fixed_base/galbot.usd
python scripts/hold_pose.py --headless --usd third_party/galbot_one_golf_description/usd/galbot_one_golf.usda --fix_root
```

`compare_usd.py` 需要先运行 6.1.2 的两种 variant 转换（`--variant wheeled` 也要转一次）。`hold_pose.py` 的预期输出（本站实测，约 14–25 秒，返回码 0，按进程显存 2315 MiB）：

```text
galbot.usd：关节 33，刚体 34，根固定 True，根高度 0.0 m，地面 True
left_arm_joint1 生效的 stiffness 400.0 N·m/rad，damping 40.0，力矩上限 60.0 N·m
保持零位 5 s：驱动关节最大偏离 0.0355 rad（right_arm_joint2），根高度变化 +0.0000 m，数值有限 True
right_gripper_joint 目标 0.8 → 实际 +0.8018，mimic 最大跟随误差 0.0038 rad

galbot_one_golf.usda：关节 77，刚体 78，根固定 True，根高度 0.0 m，地面 True
left_arm_joint1 生效的 stiffness 5729578.0 N·m/rad，damping 572957.8，力矩上限 1000.0 N·m
保持零位 5 s：驱动关节最大偏离 0.0029 rad（right_gripper_joint），根高度变化 +0.0000 m，数值有限 True
right_gripper_joint 目标 0.8 → 实际 +0.8017，mimic 最大跟随误差 0.0006 rad
```

对轮式 URDF 的转换结果（`generated/galbot_wheeled/galbot.usd`），根固定在 z=0 且有地面时滚子压进地面，会出现 NaN（滚子阻尼不是原因）；加 `--z 0.05` 或 `--no_ground` 即稳定，结果与固定底座版相同，见 6.1.2。

## 6.1.4：碰撞体、质量与惯量

本页修改了 `convert_galbot.py`（转换后写入自碰撞过滤对），**请先重新运行一次 6.1.2 的转换**，输出里应多出一行 `自碰撞过滤对 7 对`。

```bash
python scripts/inspect_inertia.py                                        # 只需 usd-core
python scripts/render_collisions.py --headless --enable_cameras          # 输出 generated/render/galbot_{visuals,collisions}.png
python scripts/check_contacts.py --headless                              # 自碰撞关
python scripts/check_contacts.py --headless --self_collision --no_filter # 开，去掉过滤对（对照）
python scripts/check_contacts.py --headless --self_collision             # 开，带过滤对（本项目的做法）
python scripts/check_contacts.py --headless --contact_offset 0.02 --poses 0  # 验证 spawn 阶段 collision_props 不生效
python scripts/probe_stuck_joint.py --headless                         # 复现"臂卡住"；可加 --no_sleep / --kick 0.05 / --vel_limit_at5 100 / --effort_scale_at5 10
```

`inspect_inertia.py` 的预期输出关键行：

```text
全机 95.184 kg（URDF 全部连杆合计 95.184 kg）；按部件：底盘与躯干底座 31.73，腿 / 躯干升降 44.71，头 2.38，左臂 8.12，左夹爪 0.06，右臂 8.12，右夹爪 0.06
碰撞体合计 184 个：{'convexHull': 144, 'Sphere': 40}
```

`check_contacts.py --self_collision` 的预期输出（本站实测，约 160 秒，返回码 0，按进程显存 2379 MiB）：

```text
自碰撞 True；接触传感器覆盖 34 个刚体
生效的接触偏移 0.0014–0.0053 m，静止偏移 0.0000–0.0000 m（184 个形状）
[1] 第 1 步有接触的刚体对：无
[2] 零位 2 s：最大偏离 0.0355 rad（right_arm_joint2），末 0.5 s 最大 |关节速度| 0.1331 rad/s，接触 无
[3] 右臂随机姿态 20 组：有接触 3 组；数值有限 True；末 0.5 s 最大 |关节速度| 9.079 rad/s
    臂关节最大跟踪误差：无接触的姿态 1.4503 rad，有接触的姿态 1.1105 rad
    出现接触的刚体对（姿态数）：{'base_link–right_arm_link7': 1, 'base_link–right_gripper_r_knuckle_link': 1, 'head_link2–right_arm_link7': 1}
[4] 右夹爪目标 1.703（上限）→ 实际 1.7023；夹爪各关节末 0.5 s 最大 |速度| 0.1205 rad/s；接触 无
```

- 不开自碰撞时（约 90 秒，2315 MiB），第 [3] 段"有接触 0 组"，末段最大关节速度 1.500 rad/s；`--no_filter` 时第 [1] 段即报 `head_link2–leg_link5`。
- `--contact_offset 0.02` 时日志有一条 `Could not perform 'modify_collision_properties'` 的 WARNING，读回的接触偏移仍为 0.0014–0.0053 m。
- `probe_stuck_joint.py` 基线的最后一行为 `8 s 后右臂最大误差 1.4491 rad（right_arm_joint3）`；加 `--vel_limit_at5 100` 或 `--effort_scale_at5 10` 时为 `0.0817 rad（right_arm_joint1）`。每次约 65–90 秒，按进程显存 2315 MiB。
- 渲染脚本约 12 秒，按进程显存 1459 MiB。

## 6.1.5：关节驱动参数

驱动参数表在 `source/galbot_academy/galbot_academy/assets/drives.py`，`make_actuators()` 把它组装成各组 `ImplicitActuatorCfg`（6.1.6 引用）。

```bash
python scripts/step_response.py --headless --seconds 3 --csv generated/step/implicit.csv   # 6 组增益的阶跃响应
python scripts/plot_step.py generated/step/implicit.csv --out generated/step/step_response.png
python scripts/step_response.py --headless --seconds 3 --actuator ideal --gains "100:10,400:10,400:40,400:120,1600:80,4000:200,20000:200,20000:2000"
python scripts/step_response.py --headless --seconds 3 --effort 1000      # 力矩上限改用厂商 USD 的 1000
python scripts/step_response.py --headless --seconds 3 --vel_limit 100    # 放开速度上限
python scripts/gravity_torques.py --headless                              # 64 组姿态的重力力矩与保持
python scripts/probe_joint_vel.py --headless                              # 静止时的关节速度读数；可加 --robot franka / --no_gravity / --device cpu / --dt 0.0166667
```

`step_response.py` 默认参数的预期输出（本站实测，每次约 11 秒，返回码 0，按进程显存 2315 MiB）：

```text
right_arm_joint2：implicit，阶跃 0.5 rad，dt 0.0083 s，力矩上限 60 N·m，速度上限 1.5 rad/s，数值有限 True
stiffness  damping    上升 s    超调 %    调节 s     稳态误差 rad     末段波动 rad     最大力矩
      100       10   0.333    13.2   1.333      +0.1137       0.0012     50.6
      400       10   0.283     9.7   0.583      +0.0315       0.0000     60.0
      400       40   0.300     2.0   0.417      +0.0317       0.0000     60.0
      400      120   0.617     0.0   1.133      +0.0321       0.0000     60.0
     1600       80   0.267     0.8   0.367      +0.0082       0.0000     60.0
     4000      200   0.267     0.1   0.383      +0.0034       0.0000     60.0
```

`gravity_torques.py` 的预期输出关键行（约 12 秒，按进程显存 2317 MiB）：

```text
leg_joint2                169.0    162.93    295.92             40
right_arm_joint2           60.0     13.73     22.34              0
arms         0.0355   0.0043    0.0413   0.0807  right_arm_joint1（第 24 台）：4.7 / 60.0 N·m
```

- `probe_joint_vel.py` 默认参数的末行：`末时刻 right_arm 各关节 |v|：joint1 0.0529，joint2 0.0088，joint3 0.0348，joint4 0.0230，…`，t = 6 s 时 `max|v| 0.1961  max|raw| 0.1961  max|fd| 0.0000`；加 `--no_gravity` 时全为 0。每次约 20 秒，按进程显存 2315 MiB。
- 日志中的 `Not all actuators are configured` 警告不应出现：参数表的各组加上 `mimic` 组覆盖了全部 33 个关节。

## 6.1.6：机器人配置 GALBOT_ONE_GOLF_CFG

配置在 `source/galbot_academy/galbot_academy/assets/galbot.py`（需在 Isaac Sim 启动后导入）：

```python
from galbot_academy.assets.galbot import GALBOT_ONE_GOLF_CFG
robot = GALBOT_ONE_GOLF_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
```

```bash
python scripts/check_actuator_groups.py                 # 只需 usd-core：每个关节恰好被一组执行器匹配
python scripts/verify_galbot_cfg.py --headless          # 4 台，保持默认姿态 + 右臂关节目标
python scripts/verify_galbot_cfg.py --headless --demo overlap_across   # 演示：跨组重叠不报错
python scripts/verify_galbot_cfg.py --headless --demo overlap_within   # 演示：组内重叠报 Multiple matches
python scripts/verify_galbot_cfg.py --headless --demo bad_default      # 演示：默认姿态越限
python scripts/verify_galbot_cfg.py --headless --demo missing_usd      # 演示：USD 不存在
python scripts/verify_galbot_cfg.py --headless --demo unfix_root       # 演示：fix_root_link=False 关不掉固定根
```

`check_actuator_groups.py` 的预期输出：

```text
可动关节 33 个；各组匹配数：{'legs': 5, 'head': 2, 'arms': 14, 'grippers': 2, 'mimic': 10}
结果：每个关节恰好被一组匹配
```

`verify_galbot_cfg.py` 的预期输出关键行（本站实测，求解器迭代 16 / 1，约 13 秒，返回码 0，按进程显存 2315 MiB）：

```text
fixed：4 台，关节 33，刚体 34，根固定 True
保持默认姿态 3 s：数值有限 True，根高度变化 0.0000 m
  误差最大的 5 个关节：right_arm_joint1 0.0527，leg_joint5 0.0344，left_arm_joint1 0.0278，leg_joint2 0.0160，right_arm_joint3 0.0127
  重力力矩 / 力矩上限 最大的 3 个：leg_joint3 0.49，leg_joint5 0.45，right_arm_joint1 0.33
right 臂关节目标（默认 ± 0.3 rad）3 s 后：最大误差 0.0525 rad，平均 0.0118 rad，数值有限 True
```

- 末段夹爪关节的速度读数为 0.1–0.2 rad/s，而位置不变（6.1.5"静止时的速度读数"），不是配置错误。
- 演示模式各打印一行：`没有报错。right_arm_joint1 在 PhysX 中的 stiffness = 1.0`、`ValueError: Multiple matches …`、`ValueError: The following joints have default positions out of the limits`、`FileNotFoundError: USD file not found …`、`RuntimeError: Failed to create articulation …`。
- 轮式变体 `GALBOT_ONE_GOLF_WHEELED_CFG` 需要先运行 `python scripts/convert_galbot.py --headless --variant wheeled --floating_base`，再运行 `verify_galbot_cfg.py --headless --variant wheeled`。它能生成、能站住，但静置时被动滚子转速达到数百 rad/s（已知问题，留给 6.4.5），本部分不用它。

## 6.2.1：reach 场景

场景在 `source/galbot_academy/galbot_academy/scenes/reach.py`：`GalbotReachSceneCfg`（地面、灯光、机器人），以及带桌面的 `GalbotReachTableSceneCfg`。TCP 的定义（`REACH_EE_BODY` 与偏移）在 `assets/galbot.py`。

```bash
python scripts/workspace.py --headless --batches 64 --voxel 0.1 --min_count 10   # 右臂可达范围
python scripts/scene_bench.py --headless --num_envs 16                           # 也可 256 / 1024；加 --table 用带桌面的场景
```

`workspace.py` 的预期输出关键行（约 11 秒，按进程显存 2785 MiB）：

```text
默认姿态下 TCP 相对根：[0.668, -0.085, 1.463] m
所有刚体离根的最大水平距离：1.138 m（定 env_spacing 用）
建议的目标采样范围（每个 10 cm 体素至少 10 个样本）：x [0.25, 0.85]，y [-0.65, -0.15]，z [1.10, 1.50] m（相对根）
```

`scene_bench.py` 的预期输出（本站实测，RTX 5070，项目配置的求解器迭代 16 / 1；加 `--solver_iters 32 1` 为 60 / 52 / 44）：

| 环境数 | 每秒物理步 | 按进程显存 | 每次总时长 |
|---|---|---|---|
| 16 | 104–105 | 2315 MiB | 约 20 s |
| 256 | 90 | 2455 MiB | 约 23 s |
| 1024 | 74 | 2987 MiB | 约 30 s |

另有关键行 `保持默认姿态 2 s：最大关节误差 0.0527 rad，数值有限 True`，加 `--table` 时不变。

## 6.1.6b：求解器迭代次数

```bash
python scripts/scene_bench.py --headless --num_envs 1024 --solver_iters 32 1     # 另两档：16 1、8 0
python scripts/step_response.py --headless --seconds 3 --solver_iters 32 1
python scripts/gravity_torques.py --headless --solver_iters 32 1
python scripts/probe_stuck_joint.py --headless --solver_iters 32 1               # 可加 --vel_limit_at5 2 或 --effort_scale_at5 1.2
```

1024 环境的每秒物理步：32 / 1 为 44，16 / 1 为 74–75，8 / 0 为 118–120。其余指标见 6.1.6 表 2。项目配置采用 16 / 1。

## 目录

```text
6-galbot-project/
├── scripts/
│   ├── fetch_galbot.sh          # 克隆 Galbot 描述仓库并固定 commit
│   ├── galbot_joint_stats.py    # 统计两个预置 URDF 的关节
│   ├── convert_galbot.py        # URDF → USD（6.1.2）
│   ├── check_galbot_usd.py      # 仿真检查转换结果（6.1.2）
│   ├── compare_usd.py           # 比较两份 USD（6.1.3）
│   ├── hold_pose.py             # 保持零位的稳定性测试（6.1.3）
│   ├── inspect_inertia.py       # 质量、惯量、碰撞体清单（6.1.4）
│   ├── render_collisions.py     # 渲染视觉网格与碰撞体（6.1.4）
│   ├── check_contacts.py        # 自碰撞与接触实验（6.1.4）
│   ├── probe_stuck_joint.py     # 复现"臂卡住"（6.1.4）
│   ├── step_response.py  plot_step.py   # 单关节阶跃响应与作图（6.1.5）
│   ├── gravity_torques.py       # 重力力矩与保持（6.1.5）
│   ├── probe_joint_vel.py       # 静止时的关节速度读数（6.1.5）
│   ├── check_actuator_groups.py # 执行器分组互斥检查（6.1.6）
│   ├── verify_galbot_cfg.py     # 验证机器人配置（6.1.6）
│   ├── workspace.py             # 手臂可达范围（6.2.1）
│   ├── scene_bench.py           # reach 场景与吞吐（6.2.1）
│   ├── list_envs.py  zero_agent.py  random_agent.py
│   └── rsl_rl/                  # train.py、play.py、cli_args.py（来自模板）
└── source/galbot_academy/
    ├── setup.py  pyproject.toml  config/extension.toml
    └── galbot_academy/
        ├── __init__.py
        ├── assets/              # 资产路径（6.1.1）、自碰撞过滤对 physics.py（6.1.4）、驱动参数表 drives.py（6.1.5）、机器人配置 galbot.py（6.1.6）
        ├── scenes/              # 场景配置（6.2.1 起）
        └── tasks/               # 任务（6.4.1 起）
```
