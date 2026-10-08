# 2.3 Layer 与合成：强度顺序与 Galbot 资产结构

对应页面：`docs/2-usd-kit/2.3-layers-composition.md`。三个脚本都只需要 usd-core，不启动 Isaac Sim，不占 GPU。

| 脚本 | 做什么 |
|---|---|
| `livrps_demo.py` | 在内存里让同一属性在本地、继承、变体、引用、载荷、特化六处都有值，依次删掉最强的一处，打印合成结果（LIVRPS） |
| `inspect_galbot_layers.py` | 打印 Galbot One Golf 厂商 USD 的合成弧、变体集、载荷加载与否的差别，并在 Session Layer 里切换变体 |
| `layer_cache_demo.py` | 常见坑一：还有 Stage 开着时，改了磁盘上的文件，重新打开仍读到旧值；`Reload()` 后才更新 |

## 准备

```bash
uv venv --python 3.11 usd-env && uv pip install --python usd-env/bin/python usd-core
```

`inspect_galbot_layers.py` 需要 Galbot 描述仓库（克隆方法见 `../2.2-usd-concepts/README.md`，页面对照 commit 2d496b0）。

## 运行（在本仓库根目录）

```bash
usd-env/bin/python examples/isaaclab-2.3/2.3-layers-composition/livrps_demo.py
usd-env/bin/python examples/isaaclab-2.3/2.3-layers-composition/layer_cache_demo.py
usd-env/bin/python examples/isaaclab-2.3/2.3-layers-composition/inspect_galbot_layers.py \
    third_party/galbot_one_golf_description/usd/galbot_one_golf.usda
```

## 预期输出（节选）

```text
合成结果：mass = 1.0（L 本地）
删掉本地值 → mass = 2.0（I 继承）
...
删掉载荷 → mass = 6.0（S 特化）
```

```text
第一次打开：mass = 1.0
改文件后，第一个 Stage 还开着，重新打开：mass = 1.0
对该 Layer 调用 Reload() 后：mass = 9.0
再改成 5.0，并关掉所有 Stage 后重新打开：mass = 5.0
```

```text
载荷：
  全部加载（默认）：Prim 1517 个，刚体 78，关节 77，用到的 Layer 13 个
  不加载载荷（LoadNone）：Prim 7 个，刚体 0，关节 0，用到的 Layer 8 个

在 Session Layer 里把变体 Physics 切到 none：
  Prim 1440 个，刚体 0，关节 0，用到的 Layer 12 个
  根 Layer 里的选择仍是：physx；Session Layer 里是：none
```

`inspect_galbot_layers.py` 只改 Session Layer，结束前清空，不会写磁盘上的 USD 文件。

验证版本：usd-core 26.08；验证日期 2026-10-08。
