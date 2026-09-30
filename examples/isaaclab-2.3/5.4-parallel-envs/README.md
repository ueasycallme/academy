# 5.4 并行环境数扫描：Cartpole 在 64 / 256 / 1024 / 4096 个环境下训练

对应页面：`docs/5-rl/5.4-parallel-envs.md`。

`sweep_num_envs.py` 依次调用 Isaac Lab 的 `scripts/reinforcement_learning/rsl_rl/train.py` 训练官方 Cartpole（headless，种子 42，`num_steps_per_env` 保持官方的 16），只改 `--num_envs` 与 `--max_iterations`。对每次训练：

- 按进程测量显存峰值：每 0.5 秒执行一次 `nvidia-smi --query-compute-apps=pid,used_memory`，只累加训练命令的进程树；
- 从终端输出中取环境步/s 与每次迭代耗时的中位数；
- 找出平均回合长度第一次 ≥ 299 的迭代及其 `Time elapsed`。

脚本本身不启动 Isaac Sim，需要 `psutil`（主线环境已有）与 `nvidia-smi`。

## 运行

用主线环境的 Python 运行（已激活 `env_isaaclab`，`isaaclab.sh` 能找到正确的解释器）：

```bash
python examples/isaaclab-2.3/5.4-parallel-envs/sweep_num_envs.py --isaaclab /path/to/IsaacLab --log_dir /tmp/sweep
```

默认配置为 `64:3000 256:1200 1024:400 4096:150`（num_envs:max_iterations），各次训练的终端输出存为 `train_<num_envs>.log`。

## 预期输出（本站实测）

```text
num_envs | 批量 | 环境步/s（中位数） | 每次迭代 s（中位数） | 首次达到阈值：迭代 / 墙上 s | 训练总时长 s | 显存峰值 MiB（按进程） | 返回码
      64 |   1024 |             11,269 |                0.090 |                   130 / 12 |        281.2 |                   2353 | 0
     256 |   4096 |             43,224 |                0.090 |                     76 / 7 |        116.6 |                   2355 | 0
    1024 |  16384 |            157,746 |                0.100 |                     62 / 6 |         43.0 |                   2489 | 0
    4096 |  65536 |            593,735 |                0.110 |                     45 / 5 |         17.4 |                   2905 | 0
```

墙上时间来自日志的 `Time elapsed`，精度 1 秒，不含启动。吞吐与每次迭代耗时受机器负载影响；同时运行其他 GPU 任务时，数值会偏低。

## 资源与耗时

2026-09-30，RTX 5070，headless。四档合计约 8 分钟，其中 64 个环境那一档最长（3000 次迭代，训练 281 秒）。显存按进程测量，峰值 2353–2905 MiB。
