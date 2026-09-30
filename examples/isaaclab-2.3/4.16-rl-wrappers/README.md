# 4.16 RL 库适配层：训练、回放与支持情况统计

对应页面：`docs/4-isaaclab/4.16-rl-wrappers.md`。

## 1. 统计官方任务对各 RL 库的支持

`count_rl_support.py` 导入 `isaaclab_tasks` 后遍历注册表，统计每个 `Isaac-*` 任务 ID 是否带 `<库>_cfg_entry_point`：

```bash
python examples/isaaclab-2.3/4.16-rl-wrappers/count_rl_support.py --headless
```

预期输出（本站实测，约 4 秒，返回码 0）：

```text
全部：168 个任务 ID；rsl_rl 96，skrl 97，rl_games 62，sb3 10；四者都没有 31
不含 -Play：125 个任务 ID；rsl_rl 57，skrl 69，rl_games 46，sb3 7；四者都没有 27
```

"四者都没有"的 31 个（本站逐个列出核对）：3 个 `Isaac-Humanoid-AMP-*-Direct-v0` 只带 `skrl_amp_cfg_entry_point`；其余 28 个是用 IK 或 RmpFlow 控制的遥操作、模仿学习任务（Stack、Lift、Reach、Open-Drawer 的 IK 版，Agibot、Galbot 的 RmpFlow 版等），只带环境配置，或另带 `robomimic_bc_cfg_entry_point`。

## 2. 训练与回放（官方脚本，在 Isaac Lab 仓库根目录运行）

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless --max_iterations 100
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Cartpole-v0 --headless --num_envs 16   # 持续回放，需手动结束
```

本站实测（RTX 5070，2026-09-30）：

- 训练：返回码 0，含启动 20 秒；`Training time: 12.01 seconds`，`Mean episode length: 300.00`，`Total timesteps: 6553600`。
- 日志目录 `logs/rsl_rl/cartpole/<时间戳>/` 下有 `events.out.tfevents.*`、`model_0.pt`、`model_50.pt`、`model_99.pt`、`params/env.yaml`、`params/agent.yaml`、`git/IsaacLab.diff`。
- 回放：加载 `model_99.pt`，在同一目录下生成 `exported/policy.pt`（16 KB）与 `exported/policy.onnx`（6 KB），之后持续运行，本站在 60 秒时手动结束。

训练使用官方默认的 4096 个环境（与 1.4 的验证命令一致），headless。

显存（**按进程**测量）：训练进程峰值 2905 MiB，连续 3 次相同。

- 测量方法：训练期间每 0.5 秒执行一次 `nvidia-smi --query-compute-apps=pid,used_memory --format=csv`，只累加训练命令（`isaaclab.sh` 及其子进程）的 `used_memory`，取最大值。
- 整卡读数（`--query-gpu=memory.used`）还包含桌面及其他进程的占用，数值更大且随机器状态变化。本站同一次训练的整卡峰值为 3436 MiB（空闲时 491 MiB），校验方测得 5956 MiB，不宜作为示例的显存需求。
