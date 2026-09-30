# 4.18 扩展模板：精简后的 `academy_demo` 项目

对应页面：`docs/4-isaaclab/4.18-extension-template.md`。

`academy_demo/` 由 Isaac Lab **v2.3.2** 的模板生成器（`tools/template/`）生成，2026-09-30。生成时的选择：外部项目，名称 `academy_demo`，Manager-based 与 Direct 两种单智能体写法，RSL-RL 的 PPO。与交互式 `./isaaclab.sh --new` 中做同样的选择等价；本站为了复现，直接调用了 `tools/template/generator.py` 的 `generate()`，传入的字典如下：

```python
{
    "external": True,
    "path": "<父目录>",
    "name": "academy_demo",
    "workflows": [{"name": "manager-based", "type": "single-agent"}, {"name": "direct", "type": "single-agent"}],
    "rl_libraries": [{"name": "rsl_rl", "algorithms": ["ppo"]}],
}
```

## 精简了什么

- **删除**：Direct 任务、`.vscode/`、仓库级配置文件（`pyproject.toml`、`.gitignore`、`.pre-commit-config.yaml` 等）、`source/academy_demo/docs/`、`scripts/zero_agent.py` 与 `random_agent.py`、项目 README。
- **修改**：只改了一处，`tasks/manager_based/academy_demo/agents/rsl_rl_ppo_cfg.py` 中的 `experiment_name` 由模板的 `"cartpole_direct"` 改为 `"academy_demo"`。
- **其余文件**与生成结果逐字相同。`scripts/rsl_rl/` 下是模板从 Isaac Lab 复制来的官方脚本，只多一行 `import academy_demo.tasks`。

## 运行

先把 `academy_demo/` 复制到仓库之外的位置（editable 安装会在源码目录下生成 `*.egg-info`），然后在该目录中、用装有 Isaac Lab 的 Python 环境执行：

```bash
python -m pip install -e source/academy_demo
python scripts/list_envs.py
python scripts/rsl_rl/train.py --task=Template-Academy-Demo-v0 --headless --num_envs 1024 --max_iterations 20
```

## 预期输出（本站实测）

- `pip install -e`：约 2 秒，返回码 0。
- `list_envs.py`：约 5 秒，返回码 0。表中 1 行：

  ```text
  | 1 | Template-Academy-Demo-v0 | isaaclab.envs:ManagerBasedRLEnv | academy_demo.tasks.manager_based.academy_demo.academy_demo_env_cfg:AcademyDemoEnvCfg |
  ```

- `train.py`：约 10 秒，返回码 0；`Total timesteps: 327680`（1024 × 16 × 20），日志写入当前目录下的 `logs/rsl_rl/academy_demo/<时间戳>/`。

## 资源与耗时

2026-09-30，RTX 5070，headless。模板任务是 Cartpole，1024 个环境，训练 20 次迭代约 3 秒（不含启动）。

显存（按进程测量）：训练进程峰值 2489 MiB，两次运行相同。测量方法：每 0.5 秒执行一次 `nvidia-smi --query-compute-apps=pid,used_memory --format=csv`，只累加训练命令及其子进程的 `used_memory`，取最大值。
