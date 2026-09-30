# 4.14 Direct 环境：Cartpole 两种写法的行数与速度

对应页面：`docs/4-isaaclab/4.14-direct-env.md`。

两个脚本：

- `count_lines.py`：按关注点（场景、动作、观测、重置、奖励、终止、总配置）统计官方 Cartpole 两种写法的代码行数，不含空行、注释与 docstring。只需普通 Python 3.10+ 和一个含 tag v2.3.2 的 IsaacLab 仓库，不需要 Isaac Sim。
- `bench_cartpole.py`：headless 运行 `Isaac-Cartpole-v0` 或 `Isaac-Cartpole-Direct-v0`，随机动作，先预热 100 步，再计时 1000 步，打印每秒环境步数。

## 运行

```bash
python examples/isaaclab-2.3/4.14-direct-env/count_lines.py --repo /path/to/IsaacLab
```

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.14-direct-env/bench_cartpole.py --headless --task Isaac-Cartpole-v0
python examples/isaaclab-2.3/4.14-direct-env/bench_cartpole.py --headless --task Isaac-Cartpole-Direct-v0
python examples/isaaclab-2.3/4.14-direct-env/bench_cartpole.py --headless --task Isaac-Cartpole-v0 --num_envs 64
python examples/isaaclab-2.3/4.14-direct-env/bench_cartpole.py --headless --task Isaac-Cartpole-Direct-v0 --num_envs 64
```

## 预期输出（本站实测）

`count_lines.py`：

```text
关注点      manager-based  direct
场景                  11       9
动作                   3       4
观测                  10      12
重置                  20      19
奖励                  23      34
终止                   7       7
总配置                 14      29
文件合计               110     129
```

`bench_cartpole.py`（RTX 5070，每种各跑 3 次）：

| 环境数 | Isaac-Cartpole-v0（环境步/s） | Isaac-Cartpole-Direct-v0（环境步/s） |
|---|---|---|
| 1024 | 294,092 / 301,971 / 303,087 | 309,897 / 314,937 / 318,982 |
| 64 | 22,535 / 23,125 / 23,461 | 21,523 / 21,825 / 21,870 |

速度与机器、驱动、后台负载有关，请以相对差别为准。两个版本的终止与重置逻辑不同（见页面），差别不能完全归因于写法。

## 资源与耗时

`bench_cartpole.py` 每次 10–12 秒，返回码 0，1024 个环境时显存占用约 0.5 GB（2026-09-30，headless）。环境的 `close()` 会释放 SimulationContext，之后 flush，再关闭 app。`count_lines.py` 瞬间完成。
