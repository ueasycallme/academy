# 4.3 configclass 演示

对应页面：`docs/4-isaaclab/4.3-configclass.md`。

只操作配置，不创建仿真；但 `isaaclab.utils` 会导入 `pxr`，所以仍通过 AppLauncher 以 headless 启动 Kit。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.3-configclass/configclass_demo.py --headless
```

## 预期输出（节选）

```text
== 可变默认值 ==
a.gains = [1.0, 2.0, 3.0], b.gains = [1.0, 2.0]
== replace / to_dict ==
c.name = c, a.name = a, c.to_dict() = {'gains': [1.0, 2.0, 3.0], 'name': 'c'}
== MISSING 与 validate ==
TypeError: Missing values detected in object DemoCfg for the following fields:
  - name
== Cartpole 环境配置的嵌套结构（前三层）==
decimation = 2, sim.dt = 0.008333333333333333, scene.num_envs = 4096
...
== 实例化之后再覆盖（Hydra 命令行覆盖走的也是 from_dict）==
decimation = 4, sim.render_interval = 2
```

每次创建 `DemoCfg` 实例（包括 `replace`）都会打印一行"用户的 __post_init__ 先执行"。

## 资源与耗时

不占显存（不创建仿真）。本站实测（2026-09-30，RTX 5070）约 4 秒，返回码 0；经管道运行时输出完整。

## 命令行覆盖（页面中的 Hydra 示例）

在 Isaac Lab 仓库根目录：

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless \
    env.scene.num_envs=64 env.rewards.pole_pos.weight=-2.0 agent.max_iterations=5 agent.num_steps_per_env=8
```

约 10 秒完成，训练目录 `logs/rsl_rl/cartpole/<时间>/params/env.yaml` 与 `agent.yaml` 中可以看到覆盖后的值。
