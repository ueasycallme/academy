# 4.12 Event Manager：startup / reset / interval 三种时机

对应页面：`docs/4-isaaclab/4.12-event-randomization.md`。

继承官方 Cartpole 配置：

- **startup**：`randomize_rigid_body_mass`，小车与摆杆的质量各乘 [0.5, 1.5] 内的随机数；
- **reset**：沿用官方的 `reset_cart_position`、`reset_pole_position`（在默认关节位置上加随机偏移）；
- **interval**：一个只计数的自定义事件，间隔 1–2 s，分别用逐环境计时（默认）与全局计时（`is_global_time=True`）。

脚本用零动作运行 300 步（5 s），打印各环境的质量、初始关节位置、运行后质量是否改变，以及两个 interval 事件在各环境的触发次数。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.12-event-randomization/event_demo.py --headless
python examples/isaaclab-2.3/4.12-event-randomization/event_demo.py --headless --episode_s 1.0
```

## 预期输出（本站实测，种子 42，重复运行输出一致）

第一条（回合 5 s）：

```text
默认质量 cart / pole：[1.0, 1.0] kg
startup 之后各环境的质量（kg）：
  env 0: cart 1.415  pole 0.883
  env 1: cart 1.459  pole 0.890
  env 2: cart 1.101  pole 0.757
  env 3: cart 1.294  pole 1.441
reset 之后各环境的初始关节位置（slider_to_cart m，cart_to_pole rad）：
  env 0:  0.975   0.361
  env 1: -0.742  -0.598
  env 2:  0.124  -0.705
  env 3:  0.044  -0.411
运行 300 步（5 s），期间重置 8 次；质量是否改变：False
interval 触发次数，逐环境计时：[3, 3, 3, 3, 3, 4, 3, 3]
interval 触发次数，全局计时：  [3, 3, 3, 3, 3, 3, 3, 3]
```

第二条（回合 1 s，短于 interval 间隔下限）：质量与初始位置同上，最后三行为

```text
运行 300 步（5 s），期间重置 40 次；质量是否改变：False
interval 触发次数，逐环境计时：[0, 0, 0, 0, 0, 0, 0, 0]
interval 触发次数，全局计时：  [3, 3, 3, 3, 3, 3, 3, 3]
```

逐环境计时的剩余时间在每次重置时重新采样，回合比间隔短，事件就永远不会触发。

## 资源与耗时

显存占用很小。每次约 8–9 秒，返回码 0（2026-09-30，RTX 5070，headless）。环境的 `close()` 会释放 SimulationContext，之后 flush，再关闭 app。
