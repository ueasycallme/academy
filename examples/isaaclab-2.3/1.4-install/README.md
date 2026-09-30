# 1.4 安装验证

对应页面：`docs/1-env/1.4-install-51-232.md`。

## 运行

在按 1.4 页装好的环境中（已激活 `env_isaaclab`）：

```bash
python verify_install.py
```

脚本逐项检查：Python 版本（3.11）、`isaacsim` 包版本（5.1.0.x）、`isaaclab` / `isaaclab_tasks` / `isaaclab_rl` 已安装、`isaaclab` 的导入路径指向真实的源码目录（排查 editable 路径失效）、PyTorch 能用 CUDA；最后 headless 启动 Kit，建一个地面并步进 100 次。

导入路径检查在启动 Kit 之前进行：失效时打印 `[FAIL] isaaclab import path` 与 `SUMMARY` 后以返回码 1 退出。全部通过时返回码为 0，有失败项时为 1。

## 预期输出

每项一行 `[PASS] …`，最后一行：

```text
SUMMARY: 8/8 passed
```

有 `[FAIL]` 时，对照页面"常见坑"一节排查。editable 路径失效时的输出示例：

```text
[FAIL] isaaclab import path: isaaclab 不是一个有效的包（常见原因：editable 安装后移动了 Isaac Lab 仓库；在新位置重新运行 ./isaaclab.sh --install）
SUMMARY: 5/6 passed; failed: isaaclab import path
```

## 需求与时长

- 显存：约 2–3 GB（headless，空场景）。
- 时长：缓存就绪后约 5 秒（本站实测）；全新机器第一次运行需要拉取扩展、编译着色器，可能超过 10 分钟。
- 脚本在结束前会调用 `sim.clear_all_callbacks()` 与 `sim.clear_instance()`；不这样做时 `simulation_app.close()` 不会返回。
