# 4.7 Actuator 模型：阶跃响应对比

对应页面：`docs/4-isaaclab/4.7-actuators.md`。

同一个 Cartpole 小车关节分别使用 `ImplicitActuatorCfg` 与 `IdealPDActuatorCfg`，跟踪 1 m 的位置阶跃目标，打印若干时刻的小车位置。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.7-actuators/actuator_step_demo.py --headless --model implicit
python examples/isaaclab-2.3/4.7-actuators/actuator_step_demo.py --headless --model ideal_pd
python examples/isaaclab-2.3/4.7-actuators/actuator_step_demo.py --headless --model implicit --kp 20000 --kd 200 --dt 0.02
python examples/isaaclab-2.3/4.7-actuators/actuator_step_demo.py --headless --model ideal_pd --kp 20000 --kd 200 --dt 0.02
python examples/isaaclab-2.3/4.7-actuators/actuator_step_demo.py --headless --overlap    # 预期报 ValueError
```

## 预期输出（本站实测，小车位置，单位 m）

| 设置 | t = 0.1 s | 0.25 s | 0.5 s | 2.0 s |
|---|---|---|---|---|
| implicit，Kp 200，Kd 20，dt 1/120 | 0.424 | 0.987 | 0.997 | 0.968 |
| ideal_pd，同上 | 0.459 | 1.001 | 0.992 | 0.979 |
| implicit，Kp 20000，Kd 200，dt 0.02 | 1.082 | 1.000 | 1.000 | 1.000 |
| ideal_pd，同上 | 1.838 | 1.080 | 0.955 | 0.876 |

- 大增益、大步长时显式 PD 振荡，隐式稳定。
- `ideal_pd` 运行时，写入 PhysX 的刚度与阻尼都是 0。
- `ideal_pd` 大增益时打印的"施加的最大力"为 1000 N：显式模型内按 `effort_limit` 截断，未设置时取 USD 中的值；脚本只设了 `effort_limit_sim=400`。
- `--overlap`：`ValueError: Multiple matches for 'slider_to_cart': '.*' and 'slider_.*'!`（脚本因异常退出，Kit 仍返回 0，请看输出）。

## 资源与耗时

显存占用很小。每次约 6–9 秒（2026-09-30，RTX 5070，headless）；经管道运行时输出完整。脚本按退出三步释放 SimulationContext → flush → close。
