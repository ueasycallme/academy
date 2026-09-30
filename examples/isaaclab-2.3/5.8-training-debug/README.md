# 5.8 训练排查：环境自检脚本与相关命令

对应页面：`docs/5-rl/5.8-training-debug.md`。

## `check_env.py`：训练前的环境自检

用随机动作运行若干步：

- 逐步检查观测与奖励有无 NaN / Inf，出现时报告步数与环境编号后退出；
- 结束时打印各观测组的形状、各维的最小值与最大值、每步奖励的范围（已乘 `step_dt`），以及各终止项的触发次数。

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/5.8-training-debug/check_env.py --headless --task Isaac-Cartpole-v0
python examples/isaaclab-2.3/5.8-training-debug/check_env.py --headless --task Isaac-Reach-Franka-v0 --steps 300
```

预期输出（本站实测，16 个环境，种子 42）：

```text
Isaac-Cartpole-v0：200 步随机动作，未出现 NaN/Inf
  观测组 policy 形状 (16, 4)
    各维最小值 [-2.97, -5.62, -4.66, -8.0]
    各维最大值 [2.98, 5.54, 4.38, 8.0]
  每步奖励范围 [-0.1487, 0.0165]（已乘 step_dt = 0.0167）
  各终止项触发次数（所有环境合计）：{'time_out': 0, 'cart_out_of_bounds': 1}
```

`Isaac-Reach-Franka-v0`（300 步）：观测组 `policy` 形状 (16, 32)，未出现 NaN/Inf；每步奖励范围 [−0.0165, −0.0010]（`step_dt` = 0.0333）；`time_out` 触发 0 次。

## 页面中其他命令的实测（在 Isaac Lab 仓库根目录运行）

```bash
./isaaclab.sh -p scripts/environments/zero_agent.py --task Isaac-Cartpole-v0 --num_envs 16 --headless
./isaaclab.sh -p scripts/environments/random_agent.py --task Isaac-Cartpole-v0 --num_envs 16 --headless
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Cartpole-v0 --num_envs 16 --headless --video --video_length 200
```

- `zero_agent.py` / `random_agent.py`：打印各 Manager 的 Term 表后持续运行，没有报错；本站在 45 秒时手动结束（两者都是无限循环）。
- `play.py --video`：加载日志目录中最新的检查点，录满 200 步后自行退出，约 22 秒，返回码 0，在该检查点目录下生成 `videos/play/rl-video-step-0.mp4`（约 0.5 MB）。需要先训练过一次，见 4.16。

## 资源与耗时

`check_env.py` 每次约 8 秒，返回码 0（2026-09-30，RTX 5070，headless）。显存（按进程）峰值 2315 MiB，两个任务相同。测量方法：每 0.5 秒执行一次 `nvidia-smi --query-compute-apps=pid,used_memory --format=csv`，只累加本脚本进程树的用量。
