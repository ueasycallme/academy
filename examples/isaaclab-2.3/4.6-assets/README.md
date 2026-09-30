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
