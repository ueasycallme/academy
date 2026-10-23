# 8.5 在 3.0 上跑 Galbot reach：示例

对应页面：`docs/8-frontier/8.5-galbot-reach-30.md`。

这是第 6 部分项目 `examples/isaaclab-2.3/6-galbot-project` 的一个**子集**，迁到 Isaac Lab 3.0（最早在 3.0 EA 上迁移，2026-10-23 在 v3.0.0 正式版上重新验证）。只包含 reach 需要的部分：资产配置、reach 场景、reach 任务、PPO 配置、评估脚本。2.3 项目没有改动。

## 环境

| 用途 | 环境 | 版本 |
|---|---|---|
| 训练、评估（3.0） | 1.5 路线 A：v3.0.0 检出里的 `.venv`（uv） | Isaac Lab v3.0.0（commit e3f7d9ff1），Python 3.12.14；isaaclab 28.0.0、isaaclab-physx 8.0.0、isaaclab-newton 9.1.4、isaaclab-rl 1.5.1；isaacsim 6.2.0.0；newton 1.6.1、mujoco-warp 3.12.0、warp-lang 1.17.0；torch 2.11.0+cu130；rsl-rl-lib 5.5.1 |
| 资产转换（PhysX 用） | Isaac Sim 5.1.0 + Isaac Lab 2.3.2（1.4） | isaacsim 5.1.0.0、isaaclab 0.54.2（v2.3.2） |

GPU：NVIDIA GeForce RTX 5090 32 GB，驱动 580.178.04；主机内存 62 GB（2026-10-23）。

## 准备资产

PhysX 预设直接用 6.1.2 转换的 USD（5.1 环境，`examples/isaaclab-2.3/6-galbot-project/scripts/convert_galbot.py`）。Newton 预设用 3.0 的转换器重新转换：

```bash
export PYTHONPATH=<本目录>
export GALBOT_GENERATED_DIR=<生成资产的目录>          # 两次转换都写到这里
export GALBOT_DESCRIPTION_DIR=<Galbot 描述仓库，commit 2d496b0>
export OMNI_KIT_ACCEPT_EULA=YES
python scripts/convert_galbot_30.py                     # 在 3.0 环境里运行
```

## 训练

外部任务不需要安装：用 `PYTHONPATH` 指向本目录，再加 `--external_callback galbot_academy.register_tasks`。3.0 没有 `--headless`，不指定可视化器（`--viz`）时默认无头运行。

```bash
cd <放日志的目录>
isaaclab train --rl_library rsl_rl --task Galbot-Reach --external_callback galbot_academy.register_tasks \
    --seed 42 --run_name physx_s42 physics=isaacsim_physx            # 1024 个环境、1000 次迭代（任务默认）
```

Newton 后端：

```bash
isaaclab train --rl_library rsl_rl --task Galbot-Reach --external_callback galbot_academy.register_tasks \
    --seed 42 --run_name newton_s42 physics=newton_mjwarp
```

接触与约束容量（`nconmax` 400、`njmax` 2000）写在 `tasks/reach/reach_env_cfg.py` 的 `GalbotReachPhysicsCfg.newton_mjwarp` 里，命令行不用另加。Newton 解析 Galbot 时偶发崩溃（段错误、`malloc(): unaligned tcache chunk detected` 或 `MemoryError`，EA 时本站 14 次启动中 7 次；正式版上 13 次启动 0 次），崩了就重跑。

## 复现"5.1 资产在 Newton 下失败"

Newton 预设默认用 3.0 转换的资产；环境变量 `GALBOT_NEWTON_USD` 可以换成别的资产：

```bash
# 原样的 5.1 资产：组合错误
GALBOT_NEWTON_USD=$GALBOT_GENERATED_DIR/galbot_fixed_base/galbot.usd python scripts/check_hold.py physics=newton_mjwarp
# 补上悬空引用后的副本：能跑，但 144 个碰撞体被忽略
cp -r $GALBOT_GENERATED_DIR/galbot_fixed_base $GALBOT_GENERATED_DIR/galbot_fixed_base_patched
python - <<'PY'
import os
from pxr import Sdf
layer = Sdf.Layer.FindOrOpen(os.path.expandvars("$GALBOT_GENERATED_DIR/galbot_fixed_base_patched/configuration/galbot_physics.usd"))
spec = Sdf.CreatePrimInLayer(layer, "/visuals/head_link1")
spec.specifier, spec.typeName = Sdf.SpecifierDef, "Xform"
layer.Save()
PY
GALBOT_NEWTON_USD=$GALBOT_GENERATED_DIR/galbot_fixed_base_patched/galbot.usd python scripts/check_hold.py physics=newton_mjwarp
```

## 评估与自检

```bash
python scripts/check_hold.py physics=isaacsim_physx                                  # 零动作保持 2 s
python scripts/eval_reach.py --checkpoint <运行目录>/model_999.pt physics=isaacsim_physx
```

预期输出与本站实测值见页面。

## 与 2.3 项目的文件对应

| 本目录 | 2.3 项目 | 主要改动 |
|---|---|---|
| `galbot_academy/assets/galbot.py` | `assets/galbot.py` | TCP 偏移四元数改为 XYZW；`PhysxArticulationRootPropertiesCfg`；去掉轮式版；加 Newton 资产路径（可用 `GALBOT_NEWTON_USD` 覆盖） |
| `galbot_academy/assets/drives.py` | `assets/drives.py` | `effort_limit_sim` / `velocity_limit_sim` → `joint_effort_limit` / `joint_velocity_limit` |
| `galbot_academy/assets/paths.py` | `assets/paths.py` | 项目根指向 2.3 项目（复用描述仓库与生成资产） |
| `galbot_academy/assets/physics.py` | `assets/physics.py` | 按名字查找刚体（3.0 转换器生成嵌套结构） |
| `galbot_academy/tasks/reach/` | `tasks/manager_based/reach/` | 任务名去掉 `-v0`；物理预设；`sim.default_visualizer_cfg`；mdp 改为惰性导入；`.torch`；命令类拆成配置与实现两个文件 |
| `galbot_academy/tasks/reach/agents/rsl_rl_ppo_cfg.py` | 同名 | `policy` → `actor` / `critic`（rsl_rl 5.x） |
| `scripts/eval_reach.py` | `scripts/eval_reach.py` | 用 3.0 的预设解析与 `launch_simulation`；指标不变 |
| `scripts/check_hold.py`、`scripts/convert_galbot_30.py` | — | 新增 |

## 8.9：奖励项的 Warp 内核版

`galbot_academy/tasks/reach/mdp/rewards_warp.py` 是 `tcp_position_error` 的 Warp 内核版，签名相同，可在 `RewardsCfg` 里直接替换。`scripts/bench_reward_warp.py` 逐步比对两版并计时，`scripts/warp_pitfalls.py` 演示 dtype / device 不对时的行为（不启动仿真）。本站在 8.8 的 Kit-less 环境（1.5 路线 C）里跑：

```bash
export PYTHONPATH=<本目录> GALBOT_GENERATED_DIR=<生成资产的目录> PYTHONUNBUFFERED=1
python scripts/bench_reward_warp.py --checkpoint <运行>/model_199.pt --num_envs 1024 physics=newton_mjwarp
python scripts/warp_pitfalls.py
```

预期（本站实测，RTX 5090，2026-10-12）：`比对 200 步 × 1024 个环境：最大绝对误差 3.8e-06 m`；`单次调用中位：torch 0.14 ms，Warp 0.047 ms`；`env.step 中位 11.0 ms`。Galbot 在 Newton 下仍偶发启动崩溃（本站这一轮 13 次启动崩了 6 次），崩了就重跑。

## 8.10：策略在 PhysX 与 Newton 之间互通

| 脚本 | 说明 |
|---|---|
| `scripts/print_ordering.py` | 打印当前后端下的关节 / 刚体顺序与策略观测布局（一行 `ORDER {...}` JSON） |
| `scripts/step_response_30.py` | 右臂单关节阶跃响应，指标同 6.3.2；`--csv` 写出曲线 |
| `scripts/plot_step_30.py` | 把几条阶跃曲线画在一张图上 |
| `scripts/convert_ckpt_23_to_30.py` | 把 2.3（rsl_rl 3.1.2）的检查点改写成 rsl_rl 5.x 的格式，只改键名 |
| `scripts/eval_reach.py` | 新增 `--load_models_only`（不加载优化器状态）、`--cmd_quat_wxyz`（观测里目标四元数改回 2.3 顺序）；非有限样本单独计数、记为失败 |

在 1.5 路线 A 环境里（两个后端都能跑）：

```bash
export OMNI_KIT_ACCEPT_EULA=YES PYTHONPATH=<本目录> GALBOT_GENERATED_DIR=<生成资产的目录>
python scripts/print_ordering.py physics=isaacsim_physx
python scripts/print_ordering.py physics=newton_mjwarp
python scripts/eval_reach.py --checkpoint <8.5 的 physx_s42>/model_999.pt physics=newton_mjwarp
python scripts/convert_ckpt_23_to_30.py <2.3 运行>/model_999.pt model23_as30.pt
python scripts/eval_reach.py --checkpoint model23_as30.pt --load_models_only --cmd_quat_wxyz physics=isaacsim_physx
python scripts/step_response_30.py --joint right_arm_joint2 --step 0.05 --csv step_physx.csv physics=isaacsim_physx
```

预期（本站实测，v3.0.0，RTX 5090，2026-10-23）：`right_arm_joint2` 在 PhysX 下序号 10、Newton 下 21；3.0 PhysX 检查点在 Newton 上 `中位数 7.70–7.96 cm … < 5 cm 26.6%–28.3%`（3 次的范围）；2.3 检查点改回四元数顺序后在 3.0 PhysX 上 `中位数 2.75 cm … < 5 cm 81.5%`；阶跃两后端上升时间都是 0.092 s。
