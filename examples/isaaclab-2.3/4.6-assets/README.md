# 4.6 Assets：Articulation.data 演示

对应页面：`docs/4-isaaclab/4.6-assets.md`。

加载 Cartpole（默认 4 个环境），打印 `data` 字段的形状与坐标系，给小车施加 50 N 推力并步进；演示不调用 `update()` 时读到旧数据。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.6-assets/articulation_data_demo.py --headless --num_envs 4
```

## 预期输出（节选）

```text
joint_names = ['slider_to_cart', 'cart_to_pole']
body_names  = ['slider', 'cart', 'pole']
find_joints('slider_.*') -> [0], ['slider_to_cart']
root_state_w         (4, 13)
body_pos_w           (4, 3, 3)
joint_pos_limits     (4, 2, 2)
env_origins[1]            = [2.0, 2.0, 0.0]
default_root_state[1, :3] = [0.0, 0.0, 2.0]
root_pos_w[1]             = [2.0, 2.0, 2.0]
joint_stiffness[0] = [0.0, 0.0], joint_damping[0] = [10.0, 0.0]
推进 0.5 s 后未 update：cart 位置 0.0000（推进前 0.0000）
调用 update() 之后：     cart 位置 1.4895
再推进 0.5 s：cart 位置 [3.992…, …]
```

小车关节限位为 ±4 m，第二段推进后接近限位。

## 资源与耗时

显存占用很小。本站实测（2026-09-30，RTX 5070，headless）约 6 秒，返回码 0；经管道运行时输出完整。脚本按退出三步释放 SimulationContext → flush → close。

---

## 探针：第一次 `reset()` 后关节速度为 0（`first_reset_velocity.py`）

对应页面 4.6 常见坑四（T-4.6b）。在官方 Cartpole（2 个环境，种子 42）上依次打印 `data.soft_joint_vel_limits` 与 env 0 的观测（位置、速度）：构造完成后、第一次 `reset()`、第 1 步之后、`step()` 内因超时重置、第二次 `reset()`。

```bash
python examples/isaaclab-2.3/4.6-assets/first_reset_velocity.py --headless
python examples/isaaclab-2.3/4.6-assets/first_reset_velocity.py --headless --device cpu
```

预期输出（本站实测，每种设备两次运行逐字一致）：

```text
device cuda:0；速度上限即 data.soft_joint_vel_limits（小车、摆杆），位置与速度取自 env 0 的观测
  构造完成后            | 速度上限 [0.0, 0.0]
  第一次 reset()      | 速度上限 [100.0, 8.0] | 位置 [0.226, 0.512] | 速度 [0.0, 0.0]
  第 1 步之后          | 速度上限 [100.0, 8.0] | 位置 [0.226, 0.514] | 速度 [0.032, 0.167]
  step 内重置（超时 2 个） | 速度上限 [100.0, 8.0] | 位置 [-0.347, -0.431] | 速度 [-0.185, -0.222]
  第二次 reset()      | 速度上限 [100.0, 8.0] | 位置 [0.096, 0.039] | 速度 [-0.234, -0.271]
```

`--device cpu` 时数值不同，但规律相同：第一次 `reset()` 的速度为 0（显示为 `-0.0`），其余三行的速度都不为 0。"第一次 reset()"一行显示的速度上限已是 100 / 8，因为 `reset()` 在事件之后调用了 `write_data_to_sim()`；事件运行时上限仍是 0（见"构造完成后"一行）。

资源与耗时：GPU 约 8–9 秒，按进程显存峰值 2315 MiB；CPU 约 6–7 秒，按进程显存峰值 253 MiB；返回码均为 0（2026-09-30，RTX 5070，headless）。显存测量方法：每 0.5 秒执行一次 `nvidia-smi --query-compute-apps=pid,used_memory --format=csv`，只累加本脚本进程树的用量。
