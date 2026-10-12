# 3.6 传感器：三种不走渲染的传感器的每步代价

对应页面：`docs/3-isaacsim/3.6-sensors.md`（"代价"一节）。

每个环境放一个从 2 m 落下的方块，方块上装 RayCaster（向下 11 × 11 = 121 条射线，只对地面求交）、Imu、ContactSensor，量每个物理步读一次传感器的代价。

## 运行

在主线环境中（Isaac Sim 5.1.0 + Isaac Lab 2.3.2），在本目录执行：

```bash
python cheap_sensors.py --headless                  # 1024 个环境
python cheap_sensors.py --headless --no_sensors     # 对照：不建传感器
python cheap_sensors.py --headless --imu_history 1  # Imu 每个物理步都更新（页面误解三）
```

## 预期输出

第一条命令先打印三种传感器的数据形状（本站实测，2026-10-11，1024 个环境，物理步 1/120 s，不渲染）：

```text
[3.6] RayCaster：update_period 0.0；pos_w (1024, 3)，quat_w (1024, 4)，ray_hits_w (1024, 121, 3)
[3.6] Imu：update_period 0.0；… lin_vel_b (1024, 3)，ang_vel_b (1024, 3)，lin_acc_b (1024, 3)，ang_acc_b (1024, 3)
[3.6] ContactSensor：update_period 0.0；net_forces_w (1024, 1, 3)，net_forces_w_history (1024, 1, 1, 3)
```

随后打印自由落体时 IMU 的读数、每个物理步的耗时与静止后的检查，例如：

```text
[3.6] num_envs 1024，不读：每个物理步 0.874 ms（3 轮 0.866–1.082），比不读多 +0.000 ms
[3.6] num_envs 1024，读 height_scan：每个物理步 1.700 ms（3 轮 1.613–2.110），比不读多 +0.826 ms
[3.6] num_envs 1024，读 imu：每个物理步 1.373 ms（3 轮 1.349–1.412），比不读多 +0.499 ms
[3.6] num_envs 1024，读 contact：每个物理步 1.062 ms（3 轮 1.029–1.062），比不读多 +0.188 ms
[3.6] 静止后 env_0 接触合力 Fz 1.962 N（0.2 kg × 9.81 = 1.962）；射线命中点高度 0.0000 m；IMU lin_acc_b z +9.81 m/s²
```

耗时随机器不同，看相对大小即可（页面表 2）。

## 资源

本站实测（RTX 5070 12 GB，2026-10-11）：

| 命令 | 进程显存峰值 | 主机内存峰值 | 墙上时间（含启动） |
|---|---|---|---|
| 默认 | 2.4 GB | 3.1 GB | 约 12 s |
| `--no_sensors` | 2.3 GB | 2.8 GB | 约 8 s |
| `--imu_history 1` | 2.4 GB | 3.1 GB | 约 9 s |

墙上时间是首次启动之后的数（Kit 缓存已热）；首次启动会更久。
