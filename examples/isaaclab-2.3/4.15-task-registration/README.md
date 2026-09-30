# 4.15 任务注册：`Academy-Cartpole-v0`

对应页面：`docs/4-isaaclab/4.15-task-registration.md`。

```text
4.15-task-registration/
├── academy_tasks/
│   ├── __init__.py        # gym.register：Academy-Cartpole-v0 与 Academy-Cartpole-Play-v0
│   └── cartpole_cfg.py    # 继承官方 CartpoleEnvCfg，pole_pos 权重改为 -2.0；_PLAY 版 16 个环境
└── run_task.py            # 查注册表 → parse_env_cfg → gym.make → step，打印每一步的结果
```

这只是演示：`run_task.py` 通过 `sys.path` 导入同目录的 `academy_tasks`。正式项目应做成可安装的扩展包，见 4.18。官方 Cartpole 默认 4096 个环境，脚本在超过 1024 时改为 64 个。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.15-task-registration/run_task.py --headless
python examples/isaaclab-2.3/4.15-task-registration/run_task.py --headless --task Academy-Cartpole-Play-v0
python examples/isaaclab-2.3/4.15-task-registration/run_task.py --headless --no_import
python examples/isaaclab-2.3/4.15-task-registration/run_task.py --headless --no_import --task academy_tasks:Academy-Cartpole-v0
```

页面"列出与查看任务"一节的输出来自（在 Isaac Lab 仓库根目录运行）：

```bash
./isaaclab.sh -p scripts/environments/list_envs.py --keyword Cartpole
```

## 预期输出（本站实测）

默认：

```text
注册表中有 Academy-Cartpole-v0：True
配置类 academy_tasks.cartpole_cfg.AcademyCartpoleEnvCfg，num_envs 4096，pole_pos 权重 -2.0
num_envs 改为 64 运行
gym.make 返回 OrderEnforcing，env.unwrapped 是 ManagerBasedRLEnv
action_space (64, 1)，single_action_space (1,)
observation_space['policy'] (64, 4)
step 返回：
  obs        {policy: Tensor(64, 4) torch.float32 cuda:0}
  rew        Tensor(64,) torch.float32 cuda:0
  terminated Tensor(64,) torch.bool cuda:0
  truncated  Tensor(64,) torch.bool cuda:0
  extras     {log: {Episode_Reward/alive: Tensor() …, Episode_Termination/time_out: float, …}}
```

`--task Academy-Cartpole-Play-v0`：配置类为 `academy_tasks.cartpole_cfg.AcademyCartpoleEnvCfg_PLAY`，`num_envs 16`。

`--no_import`，以及 `--no_import --task academy_tasks:Academy-Cartpole-v0`：

```text
注册表中有 Academy-Cartpole-v0：False
parse_env_cfg 失败：NameNotFound: Environment `Academy-Cartpole` doesn't exist. Did you mean: `Isaac-Cartpole`?
```

后一条说明：Isaac Lab 的 `parse_env_cfg` 会先去掉 `模块:` 前缀再查注册表，所以这种写法不会触发导入。

`list_envs.py --keyword Cartpole`：共 32 行，其中

```text
| 28 | Isaac-Cartpole-v0 | isaaclab.envs:ManagerBasedRLEnv | isaaclab_tasks.manager_based.classic.cartpole.cartpole_env_cfg:CartpoleEnvCfg |
```

## 资源与耗时

显存占用很小。`run_task.py` 每次 4–8 秒，`list_envs.py` 约 4 秒，返回码均为 0（2026-09-30，RTX 5070，headless）。环境的 `close()` 会释放 SimulationContext，之后 flush，再关闭 app。
