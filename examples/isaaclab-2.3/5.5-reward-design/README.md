# 5.5 奖励设计：改一项奖励权重的对比实验

对应页面：`docs/5-rl/5.5-reward-design.md`。

在官方 Cartpole 上用命令行覆盖改一项奖励权重，其余不变（4096 个环境，150 次迭代，种子 42）。奖励权重不是由其他字段派生的，所以用 Hydra 覆盖是安全的（关于派生字段见 4.3 常见坑三）。日志用 5.3 的 `parse_rsl_log.py` 解析。

## 运行

在 Isaac Lab 仓库根目录运行（主线环境）：

```bash
T="scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless --seed 42"
./isaaclab.sh -p $T > base.log 2>&1
./isaaclab.sh -p $T env.rewards.pole_pos.weight=-10.0 > polepos10.log 2>&1
./isaaclab.sh -p $T env.rewards.alive.weight=0.0 > alive0.log 2>&1
./isaaclab.sh -p $T env.rewards.alive.weight=-1.0 > aliveneg.log 2>&1
for f in base polepos10 alive0 aliveneg; do python examples/isaaclab-2.3/5.3-ppo/parse_rsl_log.py $f.log --iters 50 149; done
```

## 预期输出（本站实测，节选）

| 日志 | 第 149 次迭代：Mean reward / 回合长度 / noise std / 超时:越界 | 回合长度首次 ≥ 299 |
|---|---|---|
| base | 4.91 / 298.35 / 0.05 / 1.00:0.00 | 第 45 次 |
| polepos10 | 4.66 / 297.56 / 0.18 / 0.98:0.02 | 第 107 次 |
| alive0 | −0.12 / 81.51 / 0.14 / 0.01:0.99 | 未达到 |
| aliveneg | −0.22 / 6.90 / 0.54 / 0.00:1.00 | 未达到 |

第 149 次迭代的 `Episode_Reward/alive`：base 0.9957，polepos10 0.9901，alive0 0.0000，aliveneg −0.0194；`Episode_Reward/pole_pos`：base −0.0076，polepos10 −0.0447。

每种设置各训练一次。同机、同版本、同种子下训练结果逐字节可复现（见 5.2 的 README），换机器后数值可能不同，但各行的差别方向应当一致。

## 资源与耗时

返回码均为 0（2026-09-30，RTX 5070，headless）。`Training time`：base 18.3 秒；另外三次各约 38.5 秒，推断是运行时机器上有其他 GPU 任务。训练耗时不影响表中的数值。显存：base 即 5.3 的默认训练，按进程峰值 2905 MiB；另外三次只改了奖励权重，未单独测量显存。
