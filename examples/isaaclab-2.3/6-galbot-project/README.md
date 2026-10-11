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

## 6.4.1：单臂 reach

任务包在 `source/galbot_academy/galbot_academy/tasks/manager_based/reach/`，注册 `Galbot-Reach-v0` 与 `Galbot-Reach-Play-v0`（训练用的 agent 配置在 6.5.1 加入）。

```bash
python scripts/list_envs.py                                                  # 列出两个任务
python scripts/check_reach_targets.py --headless                             # 目标可达性（IK）
python scripts/reach_smoke.py --headless                                     # 零动作冒烟检查
python scripts/check_env.py --headless --task Galbot-Reach-v0 --steps 400    # 随机动作自检
python scripts/random_agent.py --task Galbot-Reach-v0 --num_envs 16 --headless   # 无限循环，看到 Term 表后手动结束
```

预期输出关键行（本站实测）：

```text
收敛（位置 < 0.01 m，姿态 < 0.05 rad）：98.1%                                  # check_reach_targets，约 11 s，2945 MiB
第 360 步共有 64 个环境超时重置（应为全部 64 个）                               # reach_smoke，约 24 s，2317 MiB
第二个回合开头，右臂关节相对默认值：最小 -0.200，最大 +0.200 rad（reset 事件为 ±0.2）
非任务关节（不含夹爪）在回合后半段离默认值最远 0.0340 rad
Galbot-Reach-v0：400 步随机动作，未出现 NaN/Inf                                 # check_env，约 25 s，2315 MiB
  每步奖励范围 [-0.0071, -0.0007]（已乘 step_dt = 0.0333）
```

## 6.4.2：域随机化

`Galbot-Reach-DR-v0`（以及 `-Play-v0`）在 `Galbot-Reach-v0` 上加了 startup 的质量、增益、armature 随机化，初始速度和观测噪声，配置在 `tasks/manager_based/reach/reach_dr_env_cfg.py`。

```bash
python scripts/check_dr.py --headless                                       # 读回随机化后的参数
python scripts/check_env.py --headless --task Galbot-Reach-DR-v0 --steps 400
```

`check_dr.py` 的预期输出关键行（种子 0，约 10 秒，按进程显存 2315 MiB）：

```text
  右臂连杆质量 / 标称：0.9045 … 1.0994（设定 ×[0.9, 1.1]）
  右臂刚度 / 1600：0.8041 … 1.1971；阻尼 / 80：0.8026 … 1.1889（设定 ×[0.8, 1.2]）
  右臂 armature：0.0001 … 0.0049 kg·m²（设定 +[0, 0.005]）
  第二次 reset 后右臂：位置偏移 -0.1938 … 0.1875 rad（设定 ±0.2），速度 -0.0992 … 0.0983 rad/s（设定 ±0.1）
  观测 joint_pos 项的噪声：-0.0092 … 0.0097（设定 ±0.01），enable_corruption = True
  -Play 配置：enable_corruption = False；arm_mass = None，arm_gains = None，arm_armature = None；reset_robot_joints 保留 = True
```

## 6.5.1：训练 reach

PPO 配置在 `tasks/manager_based/reach/agents/rsl_rl_ppo_cfg.py`（照搬官方 Franka reach）。`Galbot-Reach-v0` 在任务里把右臂刚度、阻尼覆盖为 1600 / 80，课程学习的动作变化率惩罚终值为 -0.001（原因见 6.5.1）。

```bash
python scripts/rsl_rl/train.py --task Galbot-Reach-v0 --headless --seed 42          # 约 26 分钟，按进程显存 3041 MiB
python scripts/eval_reach.py --headless --checkpoint logs/rsl_rl/galbot_reach/<运行>/model_999.pt
python scripts/plot_training.py logs/rsl_rl/galbot_reach/<运行 1> <运行 2> --out generated/train/reach_curves.png
tensorboard --logdir logs/rsl_rl/galbot_reach
```

预期（本站实测，RTX 5070，1024 个环境）：每次迭代约 1.52 s，1000 次迭代 1540–1548 s；同一种子两次训练逐位相同。`eval_reach.py` 对 model_999 的结果：

```text
seed 42：位置误差：中位数 2.73 cm，90% 分位 6.31 cm，< 2 cm 32.2%，< 5 cm 80.9%
seed 43：位置误差：中位数 2.91 cm，90% 分位 5.80 cm，< 2 cm 25.5%，< 5 cm 83.7%
```

合格线：中位数 ≤ 3 cm 且 < 5 cm ≥ 80%。不要只用最后一个检查点，用 `eval_reach.py` 比较几个（6.5.1 表 4）。

## 6.5.2：超参数对照

本节新增：`Galbot-Reach-DR-v0` / `-DR-Play-v0` 的 rsl_rl 入口（`reach/__init__.py`）；`eval_reach.py` 的 `--action_scale`（评估改过动作尺度的策略时必须与训练一致）。

每组用 Hydra 命令行只改一项，500 次迭代，评估 model_499：

```bash
T="scripts/rsl_rl/train.py --task Galbot-Reach-v0 --headless --seed 42 --max_iterations 500"
python $T --run_name base_s42
python $T --run_name env256_s42   --num_envs 256
python $T --run_name env4096_s42  --num_envs 4096
python $T --run_name scale025_s42 env.actions.arm_action.scale=0.25
python $T --run_name scale100_s42 env.actions.arm_action.scale=1.0
python $T --run_name std005_s42   env.rewards.end_effector_position_tracking_fine_grained.params.std=0.05
python $T --run_name std020_s42   env.rewards.end_effector_position_tracking_fine_grained.params.std=0.2
python $T --run_name ent001_s42   agent.algorithm.entropy_coef=0.01
python scripts/rsl_rl/train.py --task Galbot-Reach-DR-v0 --headless --seed 42 --max_iterations 500 --run_name dr_s42

python scripts/eval_reach.py --headless --checkpoint logs/rsl_rl/galbot_reach/<运行>/model_499.pt [--action_scale 0.25]
python scripts/eval_reach.py --headless --task Galbot-Reach-DR-v0 --num_envs 256 --checkpoint ...   # 在带随机化的任务上评估
```

预期（本站实测，RTX 5070；中位数 / < 5 cm）：基线 2.87 cm / 79.7%（种子 43：3.30 / 78.8%）；env256 6.09 / 37.8%；env4096 5.09 / 49.2%；scale0.25 14.07 / 7.6%；scale1.0 2.39 / 93.9%；std0.05 3.86 / 69.5%；std0.2 4.36 / 56.9%；熵系数 0.01 1.38 / 100%（种子 43：1.65 / 99.9%）；域随机化 2.99 / 89.3%。每组约 13 分钟（env4096 约 23 分钟），显存约 3 GB（env4096 约 5 GB）。基线一组与 6.5.1 种子 42 的前 500 次迭代逐位相同。容量：8192 个环境显存约 7.6 GB 放得下，但在 16 GB 主机内存下启动阶段可能内存不足（见 6.5.2 表 6）；16384 个环境显存不足。

熵系数 0.01 按主线预算训满 1000 次后，两个种子的 model_999 都不合格（5.59 cm / 45.2%、6.45 cm / 37.5%），主线保持 0.001，见 6.5.2"训练预算与消融结论"（D-028）。

## 6.5.3：实验管理

`scripts/collect_runs.py` 离线汇总多次训练（只需 PyYAML 与 tensorboard，不启动 Isaac Sim）：

```bash
python scripts/collect_runs.py logs/rsl_rl/galbot_reach --base <基线运行目录名> [--filter <目录名包含的字符串>]
```

输出 Markdown 表：运行、种子、迭代、检查点数、相对基线的配置改动（由 `params/agent.yaml`、`env.yaml` 逐项比较得出）、训练日志末 20 次的位置误差。对 6.5.2 那批运行的输出见页面。运行命名约定 `--run_name <改动>_s<种子>`，见 6.5.3 表 3。

## 6.6.1：回放与录视频

回放 6.5.1 种子 42 的检查点（务必写完整路径，否则会加载最新的运行，见 6.6.1 坑一）：

```bash
CK=logs/rsl_rl/galbot_reach/<6.5.1 种子 42 的运行>/model_999.pt
python scripts/rsl_rl/play.py --task Galbot-Reach-Play-v0 --checkpoint $CK                                  # 带界面，关窗口退出
python scripts/rsl_rl/play.py --task Galbot-Reach-Play-v0 --headless --video --video_length 360 --checkpoint $CK   # 录 12 s 视频后退出
python scripts/eval_reach.py --headless --checkpoint $CK
python scripts/check_export.py $CK     # 离线核对 exported/policy.pt 与 policy.onnx
```

预期（本站实测，RTX 5070）：
- 视频：`<运行>/videos/play/rl-video-step-0.mp4`，359 帧，30 fps，1280×720，约 1.2 MB；用时 37 s，显存峰值 4.8 GB，主机内存峰值 8.4 GB。
- 评估：除"位置误差：均值 3.29 cm，最大 11.29 cm"一行（6.6.1 新增）外，与 6.5.1 相同。
- `check_export.py`：TorchScript 与检查点 actor 的输出最大差为 0；ONNX 结构检查通过，输入 `obs` [1, 28]，输出 `actions` [1, 7]。

## 6.4.3：lift（未达标，待续）

新增：`scenes/lift.py`、`tasks/manager_based/lift/`（注册 `Galbot-Lift-v0`、`Galbot-Lift-Play-v0`）、`scripts/check_grasp.py`、`scripts/eval_lift.py`、`scripts/plot_lift_groups.py`。

```bash
python scripts/check_grasp.py --headless                    # 抓取物理检查（16 个环境，约 20 s）
python scripts/check_grasp.py --headless --keep_open        # 对照：夹爪不闭合
python scripts/check_grasp.py --headless --accel_sweep      # 等效加速度扫描
python scripts/rsl_rl/train.py --task Galbot-Lift-v0 --headless --num_envs 2048 --seed 42   # 1500 次迭代，约 70 分钟
python scripts/eval_lift.py --headless --checkpoint logs/rsl_rl/galbot_lift/<运行>/model_1499.pt
python scripts/plot_lift_groups.py logs/rsl_rl/galbot_lift/<运行 1> … --out generated/train/lift_groups.png
```

预期（本站实测，RTX 5070，2026-10-09）：
- `check_grasp.py`：`夹住（滑移 < 1 cm）16/16`、`从下令闭合到夹到方块 1.62 s`；`--keep_open` 为 `0/16`；`--accel_sweep` 四个方向都是 `在 32.0 m/s² 内都没有滑脱`。
- 训练：2048 个环境时每次迭代约 3 s，按进程显存约 3.3 GB，主机内存约 7.1 GB。配置文件里的默认环境数是 1024（第 6 部分的默认上限），训练时用 `--num_envs 2048`。
- 评估（当前配置，种子 42，model_1499）：`成功率 0.0%`。按 6.4.3 页的合格线（≥ 70%）未达标，页面"待续"一节列了后续候选。

## 6.2.3：批量克隆与性能

修改：`scripts/scene_bench.py`（新增克隆用时、首次 reset、一个物理步的"写入 / 步进 / 更新"拆分、分阶段 RSS、MemAvailable 最低值，以及单因素开关；6.2.1 的原有输出不变）。

```bash
python scripts/scene_bench.py --headless --num_envs 2048                        # 基线
python scripts/scene_bench.py --headless --num_envs 2048 --no_self_collision    # 单因素：关自碰撞
python scripts/scene_bench.py --headless --num_envs 2048 --no_filter            # 单因素：filter_collisions=False
python scripts/scene_bench.py --headless --num_envs 2048 --no_replicate         # 单因素：replicate_physics=False
python scripts/scene_bench.py --headless --num_envs 2048 --env_spacing 1.0
python scripts/scene_bench.py --headless --num_envs 2048 --table
python scripts/scene_bench.py --headless --num_envs 1024 --task_env --debug_vis off   # Galbot-Reach-v0 的 env.step 计时
```

预期（本站实测，RTX 5070、16 GB 主机内存，2026-10-09），2048 个环境：`建场景 7.x s（其中克隆 5.9 s），reset 3.2 s；每个物理步 19.0 ms（拆分：写入 0.7 / 步进 18.2 / 更新 0.1 ms）`；RSS 约 6.3 GiB，按进程显存 3717 MiB。4096 个环境的 RSS 约 10 GiB，在 16 GB 主机上擦边（页面表 5）；开跑前先看 `free -g`。

## 6.2.2：腕部相机与传感器

新增：`scenes/sensors.py`（`make_sensor_scene_cfg()`：在 lift 场景上按开关加右腕相机、TCP→方块的 FrameTransformer、两个指尖的接触传感器）、`scripts/check_sensors.py`、`scripts/plot_wrist_camera.py`。不改训练配置。

```bash
python scripts/check_sensors.py --headless --enable_cameras                       # 验证模式（4 个环境，约 25 s），图像存到 generated/sensors/
python scripts/check_sensors.py --headless --bench none --num_envs 256            # 代价：无传感器
python scripts/check_sensors.py --headless --bench frame --num_envs 256           # 代价：lift 自带的 ee_frame
python scripts/check_sensors.py --headless --bench contact --num_envs 256         # 代价：两个指尖接触传感器
python scripts/check_sensors.py --headless --enable_cameras --bench cam64 --num_envs 256   # 代价：64×64 TiledCamera（rgb + depth）
python scripts/plot_wrist_camera.py --in_dir generated/sensors --out generated/sensors/wrist_camera.png   # 页面图 1
```

预期（本站实测，RTX 5070，2026-10-09）：
- 验证模式：`相机位置 … 最大偏差（全部环境）0.000 mm`；`图中红色像素 … 重心 (u, v) = (74.7, 73.0)`，与上一行的投影 `(74.7, 73.7)` 相差不到 1 像素；`ee_frame：env_0 TCP 相对机器人根 [0.684, -0.071, 1.409] m`；接触力在"张开、钉住方块"阶段为 `0.00/0.00 N`，"松开方块、只靠夹持"阶段末约 `11.55/9.34 N`。按进程显存约 4.7 GB，主机内存约 6.6 GB。
- 代价模式：见 6.2.2 页表 2。

## 7.2：性能分析

新增：`scripts/profile_env.py`（Galbot-Reach-v0 的 env.step 计时、物理所占时间、torch 显存统计与按进程显存的对照；`--cprofile` 在脚本内做 cProfile）、`scripts/summarize_trace.py`（汇总 Kit CPU profiler 写出的 Chrome trace，只用标准库）。

```bash
python scripts/profile_env.py --headless --num_envs 1024
python scripts/profile_env.py --headless --num_envs 1024 --cprofile generated/profile/env_step.prof
python scripts/rsl_rl/train.py --task Galbot-Reach-v0 --headless --max_iterations 10 --kit_args \
  "--/app/profilerBackend=cpu --/app/profileFromStart=1 --/plugins/carb.profiler-cpu.plugin/saveProfile=1 --/plugins/carb.profiler-cpu.plugin/compressProfile=0 --/plugins/carb.profiler-cpu.plugin/filePath=/tmp/kit_trace.json"
python scripts/summarize_trace.py /tmp/kit_trace.json --top 20
py-spy record --idle -r 50 -o flame.svg -- python scripts/rsl_rl/train.py --task Galbot-Reach-v0 --headless --max_iterations 30
```

预期（本站实测，RTX 5070，2026-10-10）：`profile_env.py` 打印 `每个环境步 58.6 ms，其中物理（4 次 sim.step）52.4 ms`、`memory_allocated 9 MiB … nvidia-smi 按进程 2977 MiB`；`--cprofile` 的第一行是 `fetch_results`（约占 88%）；`summarize_trace.py` 中 `PhysX simulate` 平均约 13.7 ms。py-spy 需另装（本站 0.4.2）。

## 7.3：调试

```bash
python scripts/debug_step.py --headless                # 1 个环境、零动作 3 步，逐项打印观测、奖励、指令，检查 NaN
python scripts/debug_step.py --headless --breakpoint   # 第 1 步后停进 pdb
python scripts/debug_step.py --headless --debugpy      # 在 127.0.0.1:5678 等 VS Code attach（需 pip install debugpy）
```

预期（本站实测）：`环境数 1，step_dt 0.0333 s，动作维数 7`；第 1 步总奖励 −0.0030，等于各奖励项之和（−0.0897）× step_dt；`观测中有 NaN：{'policy': False}`。用时约 17 s，显存 2.3 GB，主机内存 3.4 GB。

## 6.7.2：ROS 2 闭环

新增：`ros2/reach_policy_node.py`（策略节点）、`scripts/run_ros2_sim.py`（仿真端）。两个进程用不同的 ROS 2 环境，**不要混用**：

- 节点：Ubuntu 22.04 的系统 ROS 2 Humble（Python 3.10）。onnxruntime 装在一个继承系统包的 venv 里，numpy 固定在 1.x：pip 默认会装 numpy 2.x，并遮住系统的 numpy 1.21。Humble 的消息包是按 numpy 1.x 构建的，保险起见不用 2.x（未测 2.x 是否真的出错）。
- 仿真端：Isaac Sim 自带的 Humble 库（3.10 表 1 的三个环境变量），**不要** source 系统 Humble。

```bash
# 一次性：节点用的 venv
/usr/bin/python3 -m venv --system-site-packages ~/policy_venv
~/policy_venv/bin/pip install onnxruntime==1.20.1 numpy==1.26.4

RUN=logs/rsl_rl/galbot_reach/<6.5.1 种子 42 的运行>     # 先按 6.6.1 用 play.py 导出 exported/policy.onnx
# 终端 A（节点）
source /opt/ros/humble/setup.bash
~/policy_venv/bin/python ros2/reach_policy_node.py --ros-args -p onnx:=$RUN/exported/policy.onnx
# 终端 B（仿真端），60 s 内要有节点订阅，否则报错退出
export ROS_DISTRO=humble RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:<isaacsim 包目录>/exts/isaacsim.ros2.bridge/humble/lib
python scripts/run_ros2_sim.py --headless --mode ros2 --episodes 64 --checkpoint $RUN/model_999.pt              # 加 --delay 1 / --delay 3 做延迟对照
python scripts/run_ros2_sim.py --headless --mode inproc --episodes 64 --checkpoint $RUN/model_999.pt            # 进程内对照，不需要节点
```

预期（本站实测，RTX 5070，64 回合 = 192 个样本，种子 0，每次墙上 808–827 s）：

| 方式 | 中位数 | < 5 cm | 往返延迟中位数；超时 |
|---|---|---|---|
| inproc | 3.27 cm | 80.7% | — |
| ros2 | 3.34 cm | 79.2% | 0.48 ms；0 / 23040 |
| ros2 --delay 1 | 4.39 cm | 60.4% | 0.48 ms；0 / 23040 |
| ros2 --delay 3 | 7.57 cm | 19.3% | 0.48 ms；0 / 23040 |

ros2 模式加了 `--checkpoint` 时，会多打印一行"外部节点动作与进程内 torch 策略的最大差：1.91e-06"，大于 10⁻⁵ 就说明接口有错（6.7.2 坑一）。仿真端进程显存 5058 MiB、主机内存 6.9 GB（inproc 为 2327 MiB、3.6 GB）。

## 6.4.6：pick-place 示范（脚本化示教）

新增：`tasks/manager_based/pick_place/`（注册 `Galbot-PickPlace-IK-Rel-v0`、`Galbot-PickPlace-IK-Rel-Mimic-v0`）、`scripts/record_pick_place.py`、`scripts/check_mimic_interface.py`、`scripts/replay_pick_place.py`、`scripts/sweep_grasp_pose.py`。

```bash
python scripts/sweep_grasp_pose.py --headless                         # 抓取姿态扫描（表 2），约 11 分钟
python scripts/record_pick_place.py --headless --no_export --num_demos 20 --max_attempts 20   # 只测成功率
python scripts/record_pick_place.py --headless --num_demos 10 --dataset_file ./datasets/galbot_pick_place.hdf5
python scripts/check_mimic_interface.py --headless --dataset_file ./datasets/galbot_pick_place.hdf5
python scripts/replay_pick_place.py --headless --enable_cameras --demo demo_0 --out_dir ./videos/pick_place
# 坑一、坑二的对照：换回原版 IK 动作项 / 打开机器人重力
python scripts/record_pick_place.py --headless --no_export --num_demos 10 --max_attempts 10 --stock_ik
python scripts/record_pick_place.py --headless --no_export --num_demos 10 --max_attempts 10 --robot_gravity
```

预期（本站实测，RTX 5070，2026-10-11）：

- 成功率：`[rec] 成功 20 / 尝试 20（100%）`，示范长度 482–640 步；`--stock_ik` 为 0 / 10（全部 hover 段超时），`--robot_gravity` 为 0 / 10（9 次 lift 段超时）。
- 录制：`[rec] 成功 10 / 尝试 10（100%）`，墙上 248 s，进程显存 2401 MiB，主机内存 3.7 GB，文件约 3.2 MB。
- 接口检查：每条 `grasp 首次为真在第 132 步；重放结束 success=True；动作往返最大差 ≤ 7.5e-08`，最后 `开环重放后仍然成功：10 / 10`。
- 重放：`demo_0：514 帧，640×360`，进程显存 4646 MiB，主机内存 7.1 GB；`--width 1280` 在 16 GB 主机上被内存保护停掉。

## 6.4.7：Mimic 生成与 BC 训练

新增：`scripts/run_isaaclab_script.py`（让 Isaac Lab 自带脚本认识本项目任务）、`scripts/mimic_pipeline.sh`（标注、生成、训练、评估）、`scripts/eval_bc_pick_place.py`（评估并给失败分类）、`scripts/plot_mimic_data.py`（图 1、图 2）；任务包里的 `agents/robomimic/bc_rnn_low_dim.json`。

```bash
export ISAACLAB=<Isaac Lab 2.3.2 克隆>
NUM_GEN=300 EPOCHS=2000 bash scripts/mimic_pipeline.sh annotate generate train
export CKPT=logs/robomimic/Galbot-PickPlace-IK-Rel-v0/<实验名>/<时间戳>/models/model_epoch_2000.pth
bash scripts/mimic_pipeline.sh play
python scripts/eval_bc_pick_place.py --headless --checkpoint $CKPT --num_rollouts 30
python scripts/plot_mimic_data.py --source ./datasets/galbot_pick_place.hdf5 --generated ./datasets/galbot_pick_place_generated.hdf5 \
    --train_log logs/robomimic/Galbot-PickPlace-IK-Rel-v0/<实验名>/<时间戳>/logs/log.txt --out_dir generated/mimic
# 只核流程：NUM_GEN=20 EPOCHS=2 ROLLOUTS=20
```

预期（本站实测，RTX 5070，2026-10-11）：

- 标注：`Exported 10 (out of 10) annotated episodes.`，4 min 15 s；加 `--device cpu` 是 0 / 10。
- 生成 300 条：`300/301 (99.7%) successful demos generated by mimic`，7 min 0 s，文件 99 MB。CPU 上标注、生成时日志里大量的 `[Error] PhysX error: ... Body must be non-kinematic!` 来自重置事件给运动学放置垫写速度，无害（GPU 上不出现）。
- 训练 2000 epoch：23 min 48 s，最后一个 epoch 的 `"Loss": -31.79`。
- 评估：`Successful trials: 38, out of 100 trials`，约 58 min；`eval_bc_pick_place.py` 30 回合：`[eval] 成功 11 / 30`，约 18 min。

## 6.7.1：策略导出

新增：`scripts/export_policy.py`（不启动 Isaac Sim，复用 Isaac Lab 的导出器）、`scripts/bench_policy.py`（一致性与延迟）、`scripts/make_policy_spec.py`（接口说明）、`ros2/policy_spec.py`（节点侧核对；`reach_policy_node.py` 加了 `-p spec:=`，带它在 ROS 2 下启动节点：未验证（本站 session 未在 ROS 2 下实跑））；`eval_reach.py` 加了 `--record_obs`。onnxruntime 要装进 Isaac Lab 的环境：`pip install onnxruntime==1.20.1`。

```bash
RUN=logs/rsl_rl/galbot_reach/<运行>
python scripts/export_policy.py $RUN/model_999.pt --dynamic-batch                      # → $RUN/deploy/policy.pt、policy.onnx
python scripts/make_policy_spec.py --headless --checkpoint $RUN/model_999.pt           # → $RUN/deploy/policy_spec.json
python scripts/eval_reach.py --headless --num_envs 2 --checkpoint $RUN/model_999.pt --record_obs traj.npz
python scripts/bench_policy.py consistency $RUN/model_999.pt --traj traj.npz
python scripts/bench_policy.py latency $RUN/model_999.pt
python ros2/policy_spec.py $RUN/deploy/policy.onnx $RUN/deploy/policy_spec.json        # 节点侧的核对，可单独运行
```

预期（本站实测，2026-10-11，i7-14700KF + RTX 5070）：

- 导出：`[export] 观测 28 维 → 动作 7 维；归一化：Identity`；不加 `--dynamic-batch` 时，ONNX 的计算图与 `play.py` 导出的相同。
- 接口说明：`[spec] … 观测 28 维（joint_pos 7, joint_vel 7, pose_command 7, actions 7），动作 7 维，控制 30.0 Hz`。
- 一致性：TorchScript 与检查点差 0；ONNX 在评估轨迹上最大差 1.43e-06。
- 延迟（中位数）：onnxruntime CPU 批 1 约 3.4 μs，torch CPU 1 线程批 1 约 9 μs，torch GPU 批 1 约 29 μs。torch 默认线程数、批 64 的结果不稳定（20 或 64 μs），见 6.7.1 坑三。
- `policy_spec.py`：`spec ok: [('joint_pos', 0, 7), …], action 7 @ 30.0 Hz`。

## 6.6.2：定量评估与失败案例分析

新增：`scripts/eval_report.py`（读逐样本 CSV，出区间、切片、失败模式、阈值敏感性的表与图 1，不需要 Isaac Sim）；`eval_reach.py` 加了 `--csv`、`--widen_targets`，`eval_bc_pick_place.py` 加了 `--csv`，原有打印不变。

```bash
CK=logs/rsl_rl/galbot_reach/<运行>/model_999.pt
for s in 0 1 2; do python scripts/eval_reach.py --headless --checkpoint $CK --seed $s --csv s$s.csv; done
python scripts/eval_reach.py --headless --checkpoint $CK --seed 0 --task Galbot-Reach-DR-v0 --csv dr.csv
python scripts/eval_reach.py --headless --checkpoint $CK --seed 0 --widen_targets 0.05 --csv wide.csv
python scripts/eval_bc_pick_place.py --headless --checkpoint <model_epoch_2000.pth> --num_rollouts 100 --csv bc100.csv   # 约 58 分钟
python scripts/eval_report.py --reach s0.csv s1.csv s2.csv --reach_dr dr.csv --reach_wide wide.csv --bc bc100.csv \
    --bc_source ./datasets/galbot_pick_place.hdf5 --out_dir generated/eval
```

预期（本站实测，2026-10-11，RTX 5070）：

- reach 每次约 30 s，种子 0 的打印与 6.6.1 逐位相同（中位数 2.73 cm，< 5 cm 80.9%）；种子 1、2 的中位数为 2.92、2.99 cm。
- 开域随机化：中位数 2.95 cm；目标范围外扩 5 cm：中位数 3.92 cm，< 5 cm 63.3%。
- `eval_report.py`：合并 2304 个样本，< 5 cm 为 81.3%（79.6–82.8）；失败 431 个，其中"停住没到" 15 个、"还在动" 416 个。
- BC 100 回合：`[eval] 成功 38 / 100`，与 6.4.7 的 `play.py` 逐回合相同；`eval_report.py --bc_source` 按方块起点切片：源示范覆盖范围内 47.4%，范围外 25.6%。

## 6.7.3：sim2real 清单

新增：`scripts/sim2real_report.py`。它读 6.7.1 的 `policy_spec.json` 与 URDF，打印关节名序、限位、动作换算、控制频率、超时策略；给了 `--traj` 时，再用评估轨迹算关节目标会不会越限。不需要 Isaac Sim。

```bash
python scripts/sim2real_report.py --spec logs/rsl_rl/galbot_reach/<运行>/deploy/policy_spec.json \
    --urdf ../../../third_party/galbot_one_golf_description/urdf/galbot_one_golf_fixed_base.urdf --traj traj.npz
```

预期（本站实测，2026-10-11）：控制 30.0 Hz；7 个右臂关节的 URDF 速度上限都是 1.5 rad/s。用 256 个环境的轨迹（`eval_reach.py --num_envs 256 --record_obs traj.npz --record_envs 256`）：`越限（256 个环境 × 359 步）：按步 16182 / 91904（17.6%）；按环境 245 / 256（95.7%）`，越限的是 joint2、4、6、7。

## 6.3.1：物理参数调优

新增：`scripts/sweep_physics.py`（稳定性探针）、`scripts/plot_sweep.py`（画图，不需要 Isaac Sim）、`scripts/pick_place_teacher.py`（示教控制器，从 `record_pick_place.py` 抽出，录制行为不变）。

```bash
python scripts/sweep_physics.py --headless                                  # 主线默认，20 次抓取，约 8 分钟
python scripts/sweep_physics.py --headless --dt 1/240 --decimation 8        # 每次只改一项：--pos_iters / --vel_iters / --contact_offset / --rest_offset
python scripts/sweep_physics.py --headless --mode buffers --num_envs 1024 --gpu_max_rigid_patch_count 4096 --gpu_max_rigid_contact_count 16384
python scripts/plot_sweep.py --dt <dt 各组日志> --iters <迭代各组日志> --out sweep.png
```

预期（本站实测，2026-10-11）：主线默认 `[sweep] 汇总：成功 20 / 20；成功回合的滑移 中位 0.50 cm、最大 0.85 cm`、`每控制步墙上时间 中位 42.56 ms`；开头打印机器人与方块的生效偏移（默认 `接触 1.36–5.26 mm，静止 0.00–0.00 mm（184 个形状）`）。buffers 模式 1024 个环境配小缓冲时，日志出现 `Contact buffer overflow detected` 与 `Patch buffer overflow detected`。

## 6.4.4：用 Direct 方式重写 reach

新增：`tasks/direct/reach/`（注册 `Galbot-Reach-Direct-v0`）、`scripts/compare_direct_manager.py`；`eval_reach.py`、`profile_env.py` 可用 `--task Galbot-Reach-Direct-v0`。

```bash
python scripts/compare_direct_manager.py record --headless --task Galbot-Reach-v0 --out m.npz
python scripts/compare_direct_manager.py record --headless --task Galbot-Reach-Direct-v0 --out d.npz
python scripts/compare_direct_manager.py diff m.npz d.npz
python scripts/compare_direct_manager.py lines            # 不需要 Isaac Sim
python scripts/rsl_rl/train.py --task Galbot-Reach-Direct-v0 --headless --seed 42 --run_name seed42
python scripts/eval_reach.py --headless --task Galbot-Reach-Direct-v0 --checkpoint logs/rsl_rl/galbot_reach_direct/<运行>/model_999.pt
```

预期（本站实测，2026-10-11）：`diff` 各行为 `全程最大 0；全程 ≤ 1e-05`，`超时：一致，发生在第 [360] 步`；`lines` 的文件合计 154 / 186；评估 `中位数 2.73 cm，90% 分位 6.31 cm，< 2 cm 32.2%，< 5 cm 80.9%`，与 Manager 版种子 42 相同。

## 6.1.7：资产版本管理

新增：`scripts/asset_manifest.py`（写 / 校验 `generated/<变体>/MANIFEST.json`，不需要 Isaac Sim）、`assets/conversion.py`（转换参数，从 `convert_galbot.py` 移来）、`assets/manifest.py`。`convert_galbot.py` 转换末尾自动写清单；`assets/galbot.py` 被导入时校验固定底座版的清单，不一致只发 `UserWarning`。

```bash
python scripts/convert_galbot.py --headless       # 末行多一行：资产清单：…/generated/galbot_fixed_base/MANIFEST.json
python scripts/asset_manifest.py verify           # 一致时退出码 0
python scripts/asset_manifest.py write            # 给已有的生成目录补写清单
```

预期（本站实测，2026-10-11）：`[manifest] 一致：来源、工具链、参数、文件都与清单相同`。改了 `assets/conversion.py` 的参数而没重新转换时，会列出 `参数 post_processing.mimic_natural_frequency：1000.0 → 500.0` 这类差异，退出码 1。

## 7.4：测试与 CI

新增：`tests/`（`unit/` 无 GPU、`gpu/` 冒烟与确定性回归、`regression/` 区间回归）、`pytest.ini`、`tests/requirements-ci.txt`；`ros2/policy_spec.py` 的 `onnxruntime` 改为在命令行入口里导入。

```bash
python3 -m pytest tests -q                                   # 系统 Python：只跑无 GPU 层
$PY -m pytest tests/gpu -m "not slow" -q                     # Isaac 的 Python：冒烟
$PY -m pytest tests/gpu -m slow -q                           # 确定性回归（指纹在 tests/gpu/golden_ppo.json）
GALBOT_REACH_CKPT=<model_999.pt> $PY -m pytest tests/regression -q   # 区间回归：必须单独一次调用，同进程已起 Kit 时会跳过
```

预期（本站实测，2026-10-11）：`13 passed, 1 skipped`（系统 Python）；`3 passed, 1 deselected`（冒烟）；确定性与区间回归各 1 passed。换机器后指纹用例会跳过，可用 `GALBOT_RECORD_GOLDEN=1` 重新记录。系统 pytest 加载插件出错时，加 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`。

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
│   ├── scene_bench.py           # reach 场景与吞吐（6.2.1）、批量克隆与性能（6.2.3）
│   ├── check_reach_targets.py   # reach 目标的可达性（6.4.1）
│   ├── reach_smoke.py  check_env.py   # reach 冒烟检查与环境自检（6.4.1）
│   ├── profile_env.py  summarize_trace.py   # 性能分析：env.step 计时与内存读数、汇总 Kit trace（7.2）
│   ├── check_sensors.py  plot_wrist_camera.py   # 腕部相机、FrameTransformer、接触传感器的验证与代价，画图 1（6.2.2）
│   ├── check_dr.py              # 域随机化读回检查（6.4.2）
│   ├── eval_reach.py  plot_training.py   # 评估检查点、画训练曲线（6.5.1）
│   ├── run_ros2_sim.py          # ROS 2 闭环仿真端、进程内对照（6.7.2）
│   ├── record_pick_place.py  check_mimic_interface.py  replay_pick_place.py  sweep_grasp_pose.py   # pick-place 示范（6.4.6）
│   ├── run_isaaclab_script.py  mimic_pipeline.sh  eval_bc_pick_place.py  plot_mimic_data.py   # Mimic 生成与 BC（6.4.7）
│   ├── export_policy.py  bench_policy.py  make_policy_spec.py   # 策略导出、一致性与延迟、接口说明（6.7.1）
│   ├── eval_report.py           # 读逐样本 CSV 出评估表与图（6.6.2）
│   ├── sim2real_report.py       # 打印要核对的接口常量与目标越限情况（6.7.3）
│   ├── sweep_physics.py  plot_sweep.py  pick_place_teacher.py   # 物理参数稳定性探针与画图、示教控制器（6.3.1）
│   ├── compare_direct_manager.py   # Manager 版与 Direct 版 reach 的逐步比对、行数统计（6.4.4）
│   ├── asset_manifest.py        # 写 / 校验生成资产的清单（6.1.7）
│   ├── list_envs.py  zero_agent.py  random_agent.py
│   └── rsl_rl/                  # train.py、play.py、cli_args.py（来自模板）
├── tests/  pytest.ini          # 无 GPU / 冒烟 / 回归三层测试（7.4）
├── ros2/reach_policy_node.py    # 策略节点：系统 Humble + onnxruntime（6.7.2）
├── ros2/policy_spec.py          # 核对 policy_spec.json，节点启动时调用，可单独运行（6.7.1）
└── source/galbot_academy/
    ├── setup.py  pyproject.toml  config/extension.toml
    └── galbot_academy/
        ├── __init__.py
        ├── assets/              # 资产路径（6.1.1）、自碰撞过滤对 physics.py（6.1.4）、驱动参数表 drives.py（6.1.5）、机器人配置 galbot.py（6.1.6）、转换参数 conversion.py 与清单 manifest.py（6.1.7）
        ├── scenes/              # 场景配置：reach.py（6.2.1）、lift.py（6.4.3）、sensors.py（6.2.2）
        └── tasks/               # 任务（6.4.1 起）：manager_based/reach/、lift/（6.4.3）、pick_place/（6.4.6）；direct/reach/（6.4.4）
```
