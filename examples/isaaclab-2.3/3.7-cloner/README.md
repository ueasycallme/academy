# 3.7 场景组装与 Cloner：示例

对应页面：`docs/3-isaacsim/3.7-cloner.md`。

验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04；2026-10-09。

## clone_bench.py

场景：每个环境一台 Cartpole 加一个 0.2 kg 的小方块。计时模式打印建场景用时（括号里是 `Cloner.clone()` 的累计用时）、`sim.reset()` 用时、每个物理步的耗时（不渲染），以及 `env_1` 在 USD 里是继承 `env_0` 还是复制。

```bash
python clone_bench.py --headless --num_envs 1024
python clone_bench.py --headless --num_envs 1024 --no_replicate       # replicate_physics=False
python clone_bench.py --headless --num_envs 1024 --no_fabric          # use_fabric=False
python clone_bench.py --headless --num_envs 1024 --clone_in_fabric
python clone_bench.py --headless --num_envs 1024 --stage_in_memory
python clone_bench.py --headless --num_envs 8 --probe edit            # 改 env_0 的 USD 质量，看传到哪里
python clone_bench.py --headless --num_envs 8 --probe edit --no_replicate
python clone_bench.py --headless --num_envs 8 --probe filter          # env_spacing = 0，碰撞过滤开
python clone_bench.py --headless --num_envs 8 --probe filter --no_filter
```

预期输出（关键行，本站实测）：

```text
[CLONE] env_1：继承 ['/World/envs/env_0']，Prim 规格层数 2；env_1/Cube 存在 True，自身在根层有规格 False
[BENCH] num_envs 1024 replicate_physics True use_fabric True clone_in_fabric False stage_in_memory False：建场景 2.xx s（其中克隆 0.1xx s），reset 0.46 s，每个物理步 1.6x ms；数值有限 True
[EDIT] reset 后再把 env_0 的 USD 质量改为 5.0、步进 10 步：env_1 的 USD 质量 5.0，PhysX 中各环境的质量 [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
[FILTER] filter_collisions=True，env_spacing=0：1.5 s 后方块离平均位置的水平距离 最大 0.0 cm，高度 0.050–0.050 m
```

各环境数与各开关的完整结果见页面表 2、表 3。建场景的总用时波动较大（本站与校验方的实测在 1.7–5.5 s 之间），请对照克隆、reset 与每步耗时。按进程显存：1024 个环境 2445 MiB，4096 个环境 2903 MiB。
