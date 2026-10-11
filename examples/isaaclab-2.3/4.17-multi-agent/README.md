# 4.17 多智能体环境：示例

验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（skrl 2.1.0）；验证日期 2026-10-11；RTX 5070 12 GB。讲解见 [4.17 多智能体环境](../../../docs/4-isaaclab/4.17-multi-agent.md)。

```bash
python marl_shapes.py --headless          # 双摆：MARL 与拼成单智能体两种用法的形状；rsl_rl 封装的报错
# 短训（在 Isaac Lab 仓库根目录）：--algorithm 选 IPPO / MAPPO / PPO
python scripts/reinforcement_learning/skrl/train.py --task Isaac-Cart-Double-Pendulum-Direct-v0 --headless --algorithm MAPPO --max_iterations 100 --seed 42
```

预期（本站实测）：`拼成单智能体：obs {policy: (16, 7)}；动作 (16, 2)`；三种算法各训 100 次迭代，用时 11–15 s，按进程显存约 3 GB。
