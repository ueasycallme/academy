# 4.8 Sensors 抽象：示例

对应页面：`docs/4-isaaclab/4.8-sensors.md`。

验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2；GPU：NVIDIA GeForce RTX 5070 12 GB，驱动 580.178.04；2026-10-09。

## sensors_demo.py

Cartpole 场景加一个从 1 m 落下的小方块（0.2 kg），装三种传感器：方块上的 ContactSensor、小车到杆上一点的 FrameTransformer、每个环境一台相机。打印各传感器 `data` 的字段形状，以及每个物理步（含渲染）的平均耗时。

```bash
python sensors_demo.py --headless --enable_cameras                                 # 4 个环境，TiledCamera 64×64
python sensors_demo.py --headless --no_camera                                      # 对照：不建相机
python sensors_demo.py --headless --enable_cameras --num_envs 64 --camera_type camera   # 逐台渲染的 Camera
python sensors_demo.py --headless --enable_cameras --num_envs 64 --res 256
```

预期输出（第一条命令，关键行）：

```text
[INFO] num_envs=4 camera=tiled 64x64：每个物理步（含渲染）7.69 ms
[INFO]   方块静止后的法向力 Fz = 1.962 N（重力 0.2 kg × 9.81 = 1.962 N），上次空中时间 0.417 s，当前接触时间 1.592 s
[INFO] TiledCamera: rgba (4, 64, 64, 4) torch.uint8，rgb (4, 64, 64, 3) torch.uint8，distance_to_camera (4, 64, 64, 1) torch.float32，intrinsic_matrices (4, 3, 3)
```

按进程显存：不建相机 2379 MiB，TiledCamera 4 个环境 4497 MiB；Camera 与 TiledCamera 在不同环境数、分辨率下的对比见页面表 3。耗时会因 GPU 上的其他负载而变化。

不带 `--enable_cameras` 运行会在相机初始化时抛 `RuntimeError: A camera was spawned without the --enable_cameras flag.`。
