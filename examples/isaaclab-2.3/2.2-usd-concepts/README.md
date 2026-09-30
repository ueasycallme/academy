# 2.2 USD 核心概念：查看一个 USD 文件

对应页面：`docs/2-usd-kit/2.2-usd-concepts.md`。

## 准备

默认打开 Galbot One Golf 的 USD 入口文件。先把描述仓库克隆到本仓库的 `third_party/`（已在 .gitignore 中）：

```bash
git clone https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description.git third_party/galbot_one_golf_description
git -C third_party/galbot_one_golf_description checkout 2d496b053f0d4e9e2688f59fac66022f447226be   # 页面对照的版本
```

该仓库为 Apache-2.0 许可。

## 运行

两种方式任选（在本仓库根目录执行）：

```bash
# 方式一：只装 usd-core 的独立环境，不启动 Isaac Sim
uv venv --python 3.11 usd-env && uv pip install --python usd-env/bin/python usd-core
usd-env/bin/python examples/isaaclab-2.3/2.2-usd-concepts/inspect_usd.py

# 方式二：在主线 Isaac Sim 环境（已激活 env_isaaclab）中运行，脚本会 headless 启动 SimulationApp
python examples/isaaclab-2.3/2.2-usd-concepts/inspect_usd.py
```

也可以传入其他 USD 文件：`inspect_usd.py path/to/robot.usd --depth 2 --joint <关节路径> --mesh <网格路径>`。

## 预期输出（节选）

```text
== Stage 元数据 ==
defaultPrim   : /galbot_one_golf
upAxis        : Z
metersPerUnit : 1.0
...
== 类型统计 ==
默认遍历（不进入实例内部）: 共 619 个 Prim，...
含实例内部               : 共 1517 个 Prim，...
...
== 空 Stage 的默认值 ==
upAxis        : Y
metersPerUnit : 0.01
```

## 验证记录

2026-09-30：usd-core 26.8（Python 3.11，约 0.1 秒）与 Isaac Sim 5.1.0 pip 环境（内置 USD 0.24.5，约 10 秒）均运行通过，返回码 0，Prim 树与属性值一致。区别：usd-core 不认识 PhysX / Isaac 的扩展 Schema，关节的 applied schemas 只列出 `PhysicsDriveAPI:angular`。
