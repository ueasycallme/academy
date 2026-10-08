# 2.5 用 Python 操作 USD

对应页面：`docs/2-usd-kit/2.5-usd-python.md`。

| 脚本 | 做什么 |
|---|---|
| `edit_usd.py` | 读 Galbot 厂商 USD、按类型与名字筛选关节；新建 `scene.usda` 引用它，改一个关节的刚度、加一个带物理的方块；比较 `Save` 与 `Export`。厂商文件只读，最后用 MD5 核对 |
| `check_asset.py` | 资产静态检查清单（依赖、合成错误、defaultPrim、单位、Articulation 根、嵌套刚体、关节连接、限位、质量、碰撞体、驱动），输出 通过 / 注意 / 失败 |

## 准备

需要 Galbot 描述仓库（克隆方法见 `../2.2-usd-concepts/README.md`，页面对照 commit 2d496b0）。

## 运行（在本仓库根目录）

两种环境都可以；脚本先试 `from pxr import Usd`，失败时自动 headless 启动 SimulationApp。

```bash
# usd-core（推荐，秒级启动；CI 用这个）
uv venv --python 3.11 usd-env && uv pip install --python usd-env/bin/python usd-core
usd-env/bin/python examples/isaaclab-2.3/2.5-usd-python/edit_usd.py [--out 输出目录]
usd-env/bin/python examples/isaaclab-2.3/2.5-usd-python/check_asset.py [path/to/robot.usda]

# Isaac Sim 环境（已激活 env_isaaclab）
python examples/isaaclab-2.3/2.5-usd-python/check_asset.py
```

`edit_usd.py` 不给 `--out` 时写到临时目录，结束后删除。`check_asset.py` 在 usd-core 环境下有"失败"项时退出码为 1；Isaac Sim 环境下退出码总是 0（页面坑五），请看最后的统计行。

## 预期输出（节选，usd-core）

```text
按类型：转动关节 77 个，移动关节 0 个
按名字 right_arm_joint\d：7 个
mimic 跟随关节 left_gripper_l_inner_knuckle_joint 的 applied schemas：[]
/World/Robot/joints/right_arm_joint1 stiffness：1e+05 → 2e+05
scene.usda            0.7 KB  合成后 Prim 1512 个
flattened.usda    20580.1 KB  合成后 Prim 1512 个
厂商文件未被改动：True
```

```text
[注意] MDL 材质：['OmniPBR.mdl']：按 Kit 的 MDL 搜索路径解析，到 Isaac Sim 里确认
[通过] 合成错误：0 个
...
[注意] 关节驱动：非固定关节中没有 DriveAPI 的 50 个，按名字归类：{'wheel_#_passive_#_joint': 40, 'mimic 跟随': 10}
共 12 项：失败 0，注意 2
```

在 Isaac Sim 环境里，mimic 关节的 applied schemas 列出 4 个（含 `PhysxMimicJointAPI:rotZ`），MDL 材质能解析，这一项不再出现。

验证版本：usd-core 26.08；Isaac Sim 5.1.0（pip，自带 USD 24.05）+ Isaac Lab 2.3.2；验证日期 2026-10-08。
