# 4.13 Command Manager：给 Cartpole 加一个目标位置指令

对应页面：`docs/4-isaaclab/4.13-command-manager.md`。

`command_demo.py` 在官方 Cartpole（manager-based）上加一个自定义指令项 `CartTargetCommand`：小车沿导轨的目标位置，范围 ±1 m，每 1–2 s 重采样一次。观测用 `generated_commands` 读出，奖励按小车与目标的距离扣分。零动作跑 6 s，跨过 5 s 的超时重置，打印：

- `env.command_manager` 的表；
- 前 4 个环境每次重采样的时刻、新旧目标、新的 `time_left` 与 `command_counter`；
- 重采样那一步，奖励与观测各读到的是新目标还是旧目标；
- 超时重置时写进 `extras["log"]` 的指标；
- 所有环境中由 `time_left` 触发的重采样间隔的范围。

## 运行（在已激活的 Isaac Lab 环境中，本仓库根目录）

```bash
python examples/isaaclab-2.3/4.13-command-manager/command_demo.py --headless
```

可选参数：`--num_envs`（默认 16）、`--seed`（默认 42）。

## 预期输出（节选）

```text
|   0   | cart_target | CartTargetCommand |
step_dt = 0.0167 s；reset 后 command_counter（前 4 个）= [1, 1, 1, 1]
  t=1.083 s  env 2: 目标 +0.224 → -0.283 m，新 time_left 1.225 s，counter 2
  ↳ 这一步奖励读到的目标 +0.224（旧），观测里的目标 -0.283（新）
  ...
  t=5.000 s  env 0: 目标 -0.707 → -0.384 m，新 time_left 1.221 s，counter 1
  t=5.000 s  重置 16 个环境，extras['log']['Metrics/cart_target/error'] = 0.888 m
由 time_left 触发的重采样 44 次，间隔 1.067–2.000 s（配置 1.0–2.0 s，步长 0.0167 s）
```

种子固定，三次运行输出完全一致。耗时约 13 s（含启动），进程显存峰值 2315 MiB（RTX 5070）。

验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2，RTX 5070 12 GB；验证日期 2026-10-08。
