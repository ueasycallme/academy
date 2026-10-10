# 4.20 遥操作与设备：脚本按键与录制结构

对应页面：`docs/4-isaaclab/4.20-teleop-devices.md`。

本站只有键盘，实现方也不能操作桌面窗口，所以两个脚本都用 `carb.input` 的 InputProvider 注入"按下 / 松开"事件，走 `Se3Keyboard` 自己订阅的回调路径（只绕过键盘硬件与窗口）。

- `keyboard_teleop_probe.py`：在 `Isaac-Lift-Cube-Franka-IK-Rel-v0` 上按 W、Q、A、C、K，打印末端在根坐标系下的位移、转轴与指关节位置。
- `record_probe.py`：照搬 `scripts/tools/record_demos.py` 对环境配置的改动，在 `Isaac-Stack-Cube-Franka-IK-Rel-v0` 上录 66 步，打印 HDF5 结构。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.20-teleop/keyboard_teleop_probe.py --headless                      # 复现坑一：键盘建不起来
python examples/isaaclab-2.3/4.20-teleop/keyboard_teleop_probe.py --headless --enable_appwindow   # 表 2
python examples/isaaclab-2.3/4.20-teleop/record_probe.py --headless                               # 表 3，写 ./datasets/probe.hdf5
python examples/isaaclab-2.3/4.20-teleop/record_probe.py --headless --export succeeded_only       # 坑三：没成功就 0 个回合
```

## 预期输出（本站实测，RTX 5070）

不带 `--enable_appwindow`：

```text
[probe] 无法导入 omni.appwindow：No module named 'omni.appwindow'
[probe] 创建 Se3Keyboard 失败：AttributeError: module 'omni' has no attribute 'appwindow'
```

带 `--enable_appwindow`（节选）：

```text
[probe] 默认窗口的键盘：'offscreen'；注入方式 provider
[probe] W（+x）：按住时命令 [0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]，松开后 [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        末端位移（根坐标系）[+5.9, -0.0, -0.0] cm；……
[probe] C（绕 z 转）：……
        末端位移（根坐标系）[-0.0, +0.3, -0.0] cm；转角 0.059 rad，转轴（根坐标系）[-0.00, -0.00, +1.00]；……
[probe] K（夹爪开/合）：……指关节 … → [0.0001, 0.0001]
```

`record_probe.py`：

```text
[probe] 录了 66 步，任务成功：False；已导出成功回合 0，失败回合 1
[probe] …/datasets/probe.hdf5：data 下 1 个回合，attrs total=66
        demo_0/actions  (66, 7) float32
        demo_0/processed_actions  (66, 8) float32
        ……
```

`--export succeeded_only` 时最后是 `data 下 0 个回合，attrs total=0`。

每个脚本用时约 12 s，进程显存约 1.4 GB，主机内存约 3.1 GB。
