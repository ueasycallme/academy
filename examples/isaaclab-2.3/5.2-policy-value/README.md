# 5.2 策略与价值：看一眼 actor 与 critic

对应页面：`docs/5-rl/5.2-policy-value.md`。

按官方 Cartpole 的 RSL-RL agent 配置（`CartpolePPORunnerCfg.policy`）建一个 `rsl_rl.modules.ActorCritic`，打印：

- actor / critic 的结构与参数量；
- 对固定观测 `[0, 0.2, 0, 0]`（摆杆偏 0.2 rad）输出的动作均值、标准差；
- 训练时的采样动作（4 个环境各采一次）、回放时的 `act_inference`；
- critic 给出的价值。

可选 `--checkpoint` 加载训练好的检查点，与刚初始化的网络对比。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/5.2-policy-value/inspect_actor_critic.py --headless
```

检查点来自 4.16 的训练命令（在 Isaac Lab 仓库根目录运行，约 20 秒）：

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless --max_iterations 100
python examples/isaaclab-2.3/5.2-policy-value/inspect_actor_critic.py --headless --checkpoint <IsaacLab>/logs/rsl_rl/cartpole/<时间戳>/model_99.pt
```

## 预期输出（本站实测，每种两次运行逐字一致）

刚初始化（种子 42）：

```text
obs_groups {'policy': ['policy'], 'critic': ['policy']}，动作维度 1
actor：MLP(Linear(4→32), ELU, Linear(32→32), ELU, Linear(32→1))    # 实际输出为多行，此处压缩
参数量：actor 1249，critic 1249，另有标准差参数 1 个
观测 [0, 0.2, 0, 0] → 动作均值 -0.1951，标准差 1.0000
  训练时采样 4 次（4 个环境）：[1.269, -0.519, 0.579, 1.394]
  回放时 act_inference：-0.1951（即均值）
  critic 给出的价值：+0.0539
```

加载本站训练得到的 `model_99.pt`：

```text
观测 [0, 0.2, 0, 0] → 动作均值 -0.6473，标准差 0.0769
  训练时采样 4 次（4 个环境）：[-0.535, -0.672, -0.588, -0.525]
  回放时 act_inference：-0.6473（即均值）
  critic 给出的价值：+1.7035
```

检查点的数值取决于那次训练：GPU 训练并非逐位可复现，自己训练得到的检查点数值会略有不同。但"标准差从 1.0 降到 0.1 以下、采样集中在均值附近、价值明显增大"的规律应当一致。

## 资源与耗时

每次约 8 秒，返回码 0（2026-09-30，RTX 5070，headless）。显存（按进程）：峰值 2343 MiB。测量方法：每 0.5 秒执行一次 `nvidia-smi --query-compute-apps=pid,used_memory --format=csv`，只累加本脚本进程树的用量。环境的 `close()` 会释放 SimulationContext，之后 flush，再关闭 app。
