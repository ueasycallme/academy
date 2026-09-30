# 校验环境记录

- 记录日期：2026-09-30
- 记录者：isaac-academy-examine

## 硬件与驱动
- GPU：NVIDIA GeForce RTX 5070，12 GB（12227 MiB）
- 驱动：580.178.04
- OS：Linux 6.8.0-138-generic（Ubuntu 22.04，系统 Python 3.10.12）

## Isaac Sim / Isaac Lab
| 项 | 值 |
|---|---|
| Python 环境 | `~/wuql_ws/isaac_sim/isaac_sim_h1/.venv`（uv 创建，Python 3.11） |
| isaacsim（pip） | 5.1.0.0 |
| torch | 2.7.0+cu128（CUDA 12.8，`cuda.is_available()=True`，arch 含 sm_120） |
| Isaac Lab 源码 | `~/wuql_ws/isaac_sim/IsaacLab`，`git describe` = `v2.3.2`（commit 37ddf6268），`VERSION` = 2.3.2 |
| 扩展版本 | isaaclab 0.54.2 / isaaclab_tasks 0.11.12 / isaaclab_rl 0.4.7 / isaaclab_assets 0.2.4 / isaaclab_mimic 1.0.16 / isaaclab_contrib 0.0.2（与 v2.3.2 源码 `extension.toml` 一致） |
| RL 库 | rsl_rl_lib 3.1.2（未见 skrl / rl_games / SB3） |

## 已知问题（未修复，只记录）
1. **editable 安装路径失效**：venv 中 isaaclab* 的 editable 安装指向 `/home/wuql/wuql_ws/IsaacLab/source/...`，该目录已不存在（仓库应已移到 `~/wuql_ws/isaac_sim/IsaacLab`）。直接 `import isaaclab` 得到空的 namespace 包（`__file__ is None`）。
   - 校验时的绕行方式（不改环境）：运行时设置
     `PYTHONPATH=$L/source/isaaclab:$L/source/isaaclab_tasks:$L/source/isaaclab_rl:$L/source/isaaclab_assets:$L/source/isaaclab_contrib:$L/source/isaaclab_mimic`（`L=~/wuql_ws/isaac_sim/IsaacLab`）。
   - 永久修复需要在该 venv 里重新 `pip install -e` 各 source 包，属于修改用户环境，留给用户决定。
2. **EULA**：该 venv 首次 import isaacsim 会交互询问 EULA；校验运行时用进程级环境变量 `OMNI_KIT_ACCEPT_EULA=YES`。
3. shell 默认带 ROS 2 Humble 的 `PYTHONPATH`（/opt/ros/humble/...）。跑站点构建时用 `env -u PYTHONPATH`，避免 ROS 包混入。

## 冒烟测试
- 命令：`OMNI_KIT_ACCEPT_EULA=YES PYTHONPATH=<见上> python scripts/tutorials/00_sim/create_empty.py --headless`
- 结果：AppLauncher 选用 `cuda:0`，加载 `apps/isaaclab.python.headless.kit`，SimulationContext 创建成功并进入仿真循环（该脚本为无限循环，确认运行后手动结束）。首次启动（含着色器/扩展缓存）约数分钟。

## 站点构建环境
- `isaac_tutor/.venv`（Python 3.10.12，`include-system-site-packages = false`）
- 另用 uv 在 scratch 目录按 `requirements-docs.txt` 新建干净 venv 复现构建，结果一致。
