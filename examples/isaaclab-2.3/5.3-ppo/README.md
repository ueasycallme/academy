# 5.3 PPO 工作流程：训练 Cartpole 并读日志

对应页面：`docs/5-rl/5.3-ppo.md`。

训练用官方脚本；`parse_rsl_log.py` 从保存下来的终端输出中抽取页面表 2 的指标，以及"平均回合长度第一次达到 300"的迭代。

## 运行

在 Isaac Lab 仓库根目录运行（主线环境），把终端输出存成文件：

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless --seed 42 > train.log 2>&1
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless --seed 42 agent.algorithm.clip_param=0.02 > train_clip002.log 2>&1
python examples/isaaclab-2.3/5.3-ppo/parse_rsl_log.py train.log
python examples/isaaclab-2.3/5.3-ppo/parse_rsl_log.py train_clip002.log --iters 149
```

## 预期输出（本站实测）

默认设置（4096 个环境，150 次迭代，`Training time: 18.32 seconds`）：

```text
共 150 次迭代
 迭代 | Mean reward | Mean episode length | noise std | time_out / out_of_bounds
    0 |        0.13 |               12.78 |      1.00 | 0.03 / 0.00
   10 |       -3.27 |               86.16 |      0.90 | 0.14 / 0.81
   30 |        3.40 |              214.33 |      0.63 | 0.07 / 0.93
   50 |        4.91 |              300.00 |      0.44 | 0.74 / 0.26
  100 |        4.94 |              300.00 |      0.08 | 1.00 / 0.00
  149 |        4.91 |              298.35 |      0.05 | 1.00 / 0.00
平均回合长度第一次 ≥ 299.0 的迭代：45
```

`clip_param=0.02`：

```text
  149 |        4.87 |              300.00 |      0.78 | 0.99 / 0.01
平均回合长度第一次 ≥ 299.0 的迭代：123
```

学习率不打印到终端。页面引用的学习率变化取自 TensorBoard 的 `Loss/learning_rate`：第 2 次迭代为 0.01，第 75 次约 0.000878，全程在 1e-5 到 1e-2 之间。

## 资源与耗时

训练约 25 秒（含启动），其中训练 18 秒，返回码 0（2026-09-30，RTX 5070，headless）。显存（按进程）：峰值 2905 MiB，测量方法见 4.16 的 README。`parse_rsl_log.py` 瞬间完成，不需要 GPU。
