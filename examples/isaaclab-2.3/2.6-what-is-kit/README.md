# 2.6 Omniverse Kit 是什么：查看一个 Kit 应用

对应页面：`docs/2-usd-kit/2.6-what-is-kit.md`。

`kit_inspect.py` 只启动 Kit、不建场景，打印：启动前能否导入 `omni.kit.app`、AppLauncher 选中的 `.kit`、Kit 版本、启用的扩展数、几个设置的值，并演示运行时读写设置和 `update()` 推进帧号。

## 运行（在已激活的 Isaac Lab 环境中，本仓库根目录）

```bash
python examples/isaaclab-2.3/2.6-what-is-kit/kit_inspect.py --headless
python examples/isaaclab-2.3/2.6-what-is-kit/kit_inspect.py --headless --enable_cameras
python examples/isaaclab-2.3/2.6-what-is-kit/kit_inspect.py --headless --kit_args="--/physics/updateToUsd=true"
```

## 预期输出（第一条命令，节选）

```text
启动前 import omni.kit.app：ModuleNotFoundError
启动用时 4.0 s
体验文件（.kit）：isaaclab.python.headless.kit
Kit 版本：107.3.3+production.229672.69cbf6ad.gl
已启用的扩展：80 个（已发现 651 个）
  /isaaclab/cameras_enabled      = None
  /app/useFabricSceneDelegate    = False
  /physics/updateToUsd           = False
运行时 set 之后 /physics/updateToUsd = True
update() 3 次：帧号 13 → 16
```

加 `--enable_cameras` 后：体验文件为 `isaaclab.python.headless.rendering.kit`，启用 153 个扩展，`cameras_enabled = True`，`useFabricSceneDelegate = True`，启动约 6.8 s。加 `--kit_args` 后：`/physics/updateToUsd` 启动即为 `True`。启动用时与帧号随机器而变。

体验文件名取自 AppLauncher 的内部属性 `_sim_experience_file`，仅作演示。

验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2，RTX 5070 12 GB；验证日期 2026-10-08。
