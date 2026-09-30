# 3.2 SimulationApp 与 Python 启动方式：两个最小示例

对应页面：`docs/3-isaacsim/3.2-simulation-app.md`。

两个脚本做同一件事：一个 10 cm 的方块从 1 m 高处落到地面，2 秒仿真后打印高度。

| 脚本 | 启动方式 | 运行 |
|---|---|---|
| `isaacsim_minimal.py` | `SimulationApp` + `World`（只用 Isaac Sim） | `python isaacsim_minimal.py`（加 `--gui` 打开窗口） |
| `isaaclab_minimal.py` | `AppLauncher` + Isaac Lab `SimulationContext` / `RigidObject` | `python isaaclab_minimal.py --headless`（可加 `--device cpu`） |

在主线环境中运行（已激活 `env_isaaclab`）。

## 预期输出

最后一行（Kit 日志之外，脚本自己的输出）：

```text
sim time 2.02 s, cube z = 0.050 m
```

方块停在 0.05 m，即边长的一半，表示落到了地面上。仿真时间比 2.00 s 多出约 0.02 s，推断是 `reset()` 过程中推进的步数（未深究）。

## 资源与耗时

显存占用很小（单个刚体）。本站实测（2026-09-30，RTX 5070，headless，缓存已预热，均返回码 0）：

- `isaacsim_minimal.py` 约 11 秒
- `isaaclab_minimal.py --headless` 约 5 秒
- `isaaclab_minimal.py --headless --device cpu` 约 5 秒

耗时大部分是 Kit 启动。首次运行需要编译着色器，会慢很多。

## 验证说明

- 两个脚本在 headless 与 GUI 下都用 `step(render=False)` 推进物理，GUI 时每两步另调一次 `render()`，因此两种模式的仿真时长都是 2 秒。`step(render=True)` 一次推进一个 `rendering_dt`（1/60 s），循环 240 次会变成 4 秒，见页面 3.1 "时间参数"。
- headless：实现方验证。GUI 代码路径：实现方在取消 `DISPLAY` 的情况下运行 `--gui` 与不带 `--headless`（SimulationApp 自动改为无窗口），输出同样为 2.02 s。真正打开窗口的运行由校验方在桌面环境验证（reviews/T-3.2.md）。
- 两个脚本都在 `close()` 前调用 `sys.stdout.flush()`，输出重定向到文件或管道时不会丢失。
- 两个脚本都在退出前释放仿真上下文。去掉 `isaaclab_minimal.py` 中的 `clear_all_callbacks()` 与 `clear_instance()` 后，进程会卡在 `close()`（本站实测，90 秒后被强制结束）。
