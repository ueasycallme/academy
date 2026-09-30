# 4.10 Observation / Action Manager：改观测与动作

对应页面：`docs/4-isaaclab/4.10-observation-action.md`。

继承官方 Cartpole 配置：

- `policy` 组的 `joint_pos_rel` 加高斯噪声（std 0.05），打开 `enable_corruption`，末尾追加 `last_action`；
- 另建不加噪声的 `critic` 组；
- 可选把动作项换成 `JointPositionActionCfg(scale=0.5)`。

脚本用固定动作 1.0 运行 60 个环境步，打印观测 / 动作空间、原始与处理后的动作、小车位置，以及两组观测的差。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.10-observation-action/obs_action_demo.py --headless
python examples/isaaclab-2.3/4.10-observation-action/obs_action_demo.py --headless --action position
python examples/isaaclab-2.3/4.10-observation-action/obs_action_demo.py --headless --action position --kp 1000
python examples/isaaclab-2.3/4.10-observation-action/obs_action_demo.py --headless --no_noise
```

## 预期输出（本站实测）

```text
观测空间 Dict('policy': Box(-inf, inf, (5,), float32), 'critic': Box(-inf, inf, (4,), float32))
各组的 Term 与维度 {'policy': ['joint_pos_rel', 'joint_vel_rel', 'last_action'], 'critic': ['joint_pos_rel', 'joint_vel_rel']} {'policy': [(2,), (2,), (1,)], 'critic': [(2,), (2,)]}
动作空间 Box(-inf, inf, (1,), float32)，动作项 ['joint_effort']
原始动作 [1.0] → 处理后 [100.0]
```

| 运行方式 | 处理后动作 | env 0 小车位置 | policy 与 critic 的最大差 |
|---|---|---|---|
| 默认 | 100.0 | 随起点变化 | 约 0.13 |
| `--action position` | 0.5 | −0.224 → −0.295（不跟随，执行器刚度为 0） | 约 0.10 |
| `--action position --kp 1000` | 0.5 | 0.055 → 0.469（趋向 0.5） | 约 0.13 |
| `--no_noise` | 100.0 | 随起点变化 | 0.0000 |

小车起点由重置事件随机决定，位置数值每次不同；处理后动作、形状和 `--no_noise` 时的 0 是确定的。

## 资源与耗时

显存占用很小。每次运行约 7–9 秒，返回码 0（2026-09-30，RTX 5070，headless）。环境的 `close()` 会释放 SimulationContext，之后 flush，再关闭 app。
