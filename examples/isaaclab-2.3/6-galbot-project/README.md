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

## 目录

```text
6-galbot-project/
├── scripts/
│   ├── fetch_galbot.sh          # 克隆 Galbot 描述仓库并固定 commit
│   ├── galbot_joint_stats.py    # 统计两个预置 URDF 的关节
│   ├── list_envs.py  zero_agent.py  random_agent.py
│   └── rsl_rl/                  # train.py、play.py、cli_args.py（来自模板）
└── source/galbot_academy/
    ├── setup.py  pyproject.toml  config/extension.toml
    └── galbot_academy/
        ├── __init__.py
        ├── assets/              # 资产路径（6.1.1），之后加入机器人配置（6.1.6）
        └── tasks/               # 任务（6.4.1 起）
```
