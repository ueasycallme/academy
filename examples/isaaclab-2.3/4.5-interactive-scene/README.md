# 4.5 InteractiveScene 演示

对应页面：`docs/4-isaaclab/4.5-interactive-scene.md`。

场景含地面、穹顶灯、Cartpole，以及每个环境一个 10 cm 的方块（从 1 m 高处落下）。脚本打印环境路径、`env_origins`、实体名等信息，最后打印 2 秒后各环境方块的高度。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.5-interactive-scene/scene_demo.py --headless --num_envs 16
python examples/isaaclab-2.3/4.5-interactive-scene/scene_demo.py --headless --num_envs 16 --spacing 0              # 所有环境重叠
python examples/isaaclab-2.3/4.5-interactive-scene/scene_demo.py --headless --num_envs 16 --spacing 0 --no_filter  # 关闭环境间碰撞过滤
```

另有 `--ground_global`（地面 `collision_group=-1`）与 `--device cpu`。

## 预期输出（默认参数，节选）

```text
env_ns = /World/envs, env_regex_ns = /World/envs/env_.*
robot prim_path = /World/envs/env_.*/Robot
/World/envs 下的环境 Prim 数 = 16，前三个：['env_0', 'env_1', 'env_2']
env_origins 形状 (16, 3)，前三行：[[6.0, -6.0, 0.0], [6.0, -2.0, 0.0], [6.0, 2.0, 0.0]]
scene.keys() = ['terrain', 'robot', 'cube', 'ground', 'light']
articulations = ['robot']，rigid_objects = ['cube']
robot 关节 = ['slider_to_cart', 'cart_to_pole']，joint_pos 形状 (16, 2)
ground collision_group = 0，env_spacing = 4.0，filter_collisions = True：方块高度 最小 0.050 m，最大 0.050 m
```

本站实测（2026-09-30，RTX 5070，headless）的方块高度：

| 参数 | 最小 | 最大 |
|---|---|---|
| 默认 | 0.050 | 0.050 |
| `--ground_global` | 0.050 | 0.050 |
| `--device cpu` | 0.050 | 0.050 |
| `--spacing 0` | 0.050 | 0.050 |
| `--spacing 0 --device cpu` | 0.050 | 0.050 |
| `--spacing 0 --no_filter` | 0.050 | 0.278 |

`--spacing 0` 时 16 个环境重叠：开启过滤时方块互不影响；关闭过滤后方块互相碰撞、叠在一起。

## 资源与耗时

显存占用很小。每次约 6–7 秒，均返回码 0；经管道运行时输出完整。脚本按退出三步释放 SimulationContext → flush → close。
