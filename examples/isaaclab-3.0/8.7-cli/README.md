# 8.7 `isaaclab` 命令行：外部任务注册的最小示例

对应页面：`docs/8-frontier/8.7-isaaclab-cli.md`。

`academy_cli_demo` 是一个最小的外部任务包：把 Isaac Lab 自带的 Cartpole（Direct）换名注册成 `Academy-Cartpole-Direct`，用来演示怎么把自己的任务挂进 `isaaclab train / play`。

| 文件 | 说明 |
|---|---|
| `academy_cli_demo/tasks.py` | `gym.register(id="Academy-Cartpole-Direct", …)`，环境类与配置复用 `isaaclab_tasks.core.cartpole` |
| `academy_cli_demo/__init__.py` | `register_tasks()`：供 `--external_callback` 调用，返回 None；`register_tasks_returning_empty()`：反例，返回 `[]`（页面坑一） |
| `pyproject.toml` | 第二种挂法：`isaaclab.tasks` 入口点组。本站没有安装它，未验证 |

## 运行

在 Isaac Lab 3.0 环境中（本站用 1.5 路线 A，`source <IsaacLab-3.0>/.venv/bin/activate`），在本目录执行：

```bash
export OMNI_KIT_ACCEPT_EULA=YES
PYTHONPATH=$PWD isaaclab train --rl_library rsl_rl --task Academy-Cartpole-Direct --num_envs 64 --max_iterations 2 \
    --external_callback academy_cli_demo.register_tasks physics=isaacsim_physx
# 反例：physics= 被丢掉，回到任务默认的 newton_mjwarp
PYTHONPATH=$PWD isaaclab train --rl_library rsl_rl --task Academy-Cartpole-Direct --num_envs 64 --max_iterations 2 \
    --external_callback academy_cli_demo.register_tasks_returning_empty physics=isaacsim_physx
```

## 预期输出

启动摘要表里的 `Physics` 一行：第一条是 `isaacsim_physx`，第二条是 `newton_mjwarp`。训练跑 2 次迭代后正常结束，日志在 `logs/rsl_rl/cartpole_direct/<时间戳>_<run_name>/`（相对于当前目录）。

本站实测时用的是 `physics=physx`：返回 None 的那次摘要为 `physx (ovphysx)`，因为没装 `ov[ovphysx]`，随即报 `ModuleNotFoundError`（页面坑二）；返回 `[]` 的那次为 `newton_mjwarp`。上面两条命令（`physics=isaacsim_physx`）也各跑过一次，摘要分别是 `isaacsim_physx` 与 `newton_mjwarp`，2 次迭代都正常结束（2026-10-12）。

## 需求与时长

- 显存：本站没有记录按进程峰值（这些是 2 次迭代的短跑，不作资源测量）。
- 每条约 10–40 s（含启动；Newton 后端较快，Isaac Sim PhysX 要启动 Kit，较慢）。

## 本站实测环境

Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0（pip，`isaacsim` 6.1.0.0），Python 3.12，RTX 5090 32 GB，驱动 580.178.04，2026-10-12。
