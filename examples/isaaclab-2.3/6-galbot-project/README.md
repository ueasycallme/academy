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
- `--variant wheeled` 转换轮式 URDF 作对照（78 个刚体）。
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
galbot.usd：关节 33，刚体 34，根固定 True
left_arm_joint1 生效的 stiffness 400.0 N·m/rad，damping 40.0，力矩上限 60.0 N·m
保持零位 5 s：驱动关节最大偏离 0.0355 rad（right_arm_joint2），根高度变化 +0.0000 m，数值有限 True
right_gripper_joint 目标 0.8 → 实际 +0.8018，mimic 最大跟随误差 0.0038 rad

galbot_one_golf.usda：关节 77，刚体 78，根固定 True
left_arm_joint1 生效的 stiffness 5729578.0 N·m/rad，damping 572957.8，力矩上限 1000.0 N·m
保持零位 5 s：驱动关节最大偏离 0.0029 rad（right_gripper_joint），根高度变化 +0.0000 m，数值有限 True
right_gripper_joint 目标 0.8 → 实际 +0.8017，mimic 最大跟随误差 0.0006 rad
```

对轮式 URDF 的转换结果（`generated/galbot_wheeled/galbot.usd`）运行时出现 NaN，见 6.1.3。

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
│   ├── list_envs.py  zero_agent.py  random_agent.py
│   └── rsl_rl/                  # train.py、play.py、cli_args.py（来自模板）
└── source/galbot_academy/
    ├── setup.py  pyproject.toml  config/extension.toml
    └── galbot_academy/
        ├── __init__.py
        ├── assets/              # 资产路径（6.1.1），之后加入机器人配置（6.1.6）
        └── tasks/               # 任务（6.4.1 起）
```
