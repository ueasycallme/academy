# 4.4 SimulationContext 与 SimulationCfg：参数演示

对应页面：`docs/4-isaaclab/4.4-simulation-context.md`。

一个 10 cm 的方块从 10 m 高处自由下落 1 秒（场景中没有地面），打印资产 `data` 与 USD 属性中的高度。`dt`、`render_interval`、`gravity`、`use_fabric` 可以通过命令行修改。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.4-simulation-context/sim_cfg_demo.py --headless
python examples/isaaclab-2.3/4.4-simulation-context/sim_cfg_demo.py --headless --no_fabric
python examples/isaaclab-2.3/4.4-simulation-context/sim_cfg_demo.py --headless --device cpu
python examples/isaaclab-2.3/4.4-simulation-context/sim_cfg_demo.py --headless --dt 0.005 --gravity -1.62
```

## 预期输出（默认参数）

```text
device=cuda:0 use_fabric=True dt=0.0083 steps=120
sim time 1.017 s
data.root_pos_w z = 4.889 m  (张量在 cuda:0)
USD xformOp:translate z = 10.000 m
理论值 z = 5.095 m
```

- `data` 中的高度为 4.889 m，与 122 步半隐式积分的结果一致：10 − g·dt²·n(n+1)/2，n = 122。仿真时间 1.017 s，比 120 步多约 2 步，来自 `reset()` 过程。"理论值"按连续公式 10 − ½g·1² 计算，两者之差是离散化造成的。
- USD 属性始终为 10 m：Isaac Lab 的体验文件设置了 `physics.updateToUsd = false`，与 `use_fabric`、设备无关。

## 资源与耗时

显存占用很小（单个刚体）。本站实测（2026-09-30，RTX 5070，headless）：四种参数组合各约 4–5 秒，均返回码 0；经管道运行时输出完整。脚本按退出三步释放 SimulationContext → flush → close。
