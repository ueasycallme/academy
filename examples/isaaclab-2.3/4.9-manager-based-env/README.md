# 4.9 Manager-based 环境：继承官方 Cartpole 配置

对应页面：`docs/4-isaaclab/4.9-manager-based-env.md`。

继承 `CartpoleEnvCfg`，在 `__post_init__` 中先调用父类，再把 `pole_pos` 奖励权重改为 −2.0，并加一个自定义奖励 Term `cart_center`（小车离轨道中心的距离，权重 −0.1）。用随机动作运行 100 步，打印各 Manager 的信息。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.9-manager-based-env/custom_cartpole.py --headless --num_envs 16
```

页面"动手"一节的另两条命令在 Isaac Lab 仓库根目录运行：

```bash
./isaaclab.sh -p scripts/environments/random_agent.py --task Isaac-Cartpole-v0 --num_envs 16 --headless   # 一直运行，需 Ctrl+C
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless \
    env.scene.num_envs=64 env.decimation=4 agent.max_iterations=2    # 预期打印 render interval 警告
```

## 预期输出（本站实测）

```text
|   5   | cart_center |   -0.1 |          ← Reward Manager 表中出现第 6 项
动作维度 1，观测组 {'policy': (4,)}
奖励 Term：['alive', 'terminating', 'pole_pos', 'cart_vel', 'pole_vel', 'cart_center']
obs['policy'] 形状 (16, 4)，reward 形状 (16,)
环境 0 本步的各奖励项（func × weight，未乘 dt；计入总奖励时再乘 dt）：
  alive           1.00000
  ...
```

- 各奖励项的数值取决于随机动作，每次不同；`alive` 恒为 1.0。
- `pole_pos` 表中权重为 −2.0（原值 −1.0）。
- 训练命令打印 `The render interval (2) is smaller than the decimation (4)` 警告：命令行覆盖在 `__post_init__` 之后生效，`render_interval` 没有跟着 decimation 更新。

## 资源与耗时

显存占用很小。示例约 8–9 秒，返回码 0；训练命令（2 次迭代）约 10 秒。2026-09-30 在 RTX 5070 上 headless 运行。环境的 `close()` 会释放 SimulationContext，之后 flush，再关闭 app。
