# 3.5 资产导入：把 Galbot URDF 转成 USD

对应页面：`docs/3-isaacsim/3.5-urdf-mjcf-import.md`。

## 准备

把 Galbot One Golf 描述仓库克隆到本仓库的 `third_party/`，并切到 commit `2d496b0`（见 `../2.2-usd-concepts/README.md`）。

## 运行

在主线环境中（已激活 `env_isaaclab`），在本仓库根目录执行：

```bash
python examples/isaaclab-2.3/3.5-urdf-mjcf-import/convert_galbot.py --headless --output galbot_usd/galbot.usd
```

与 Isaac Lab 自带的 `scripts/tools/convert_urdf.py` 相比，脚本多设了两项：

- `convert_mimic_joints_to_normal_joints=True`：在 v2.3.2 中，只有设为 True 才会保留 mimic 关系，效果与字段名相反，见页面"常见坑"。
- 驱动目标类型按关节名分组：`{".*": "position", "wheel_.*_passive_.*": "none"}`，被动滚子的增益为 0。字典按顺序应用，通配项必须放在最前面。

驱动增益（stiffness 100、damping 1）只是演示值。

## 预期输出

```text
Generated USD file: <绝对路径>/galbot_usd/galbot.usd
```

输出目录约 12 MB，包含 `galbot.usd`、`config.yaml` 与 `configuration/`。过程中大量 `Unresolved reference … </visuals/…>` 警告来自 URDF 中没有 `<visual>` 的连杆，可以忽略。

检查结果：

```bash
python examples/isaaclab-2.3/2.4-physics-schema/list_physics_schemas.py galbot_usd/galbot.usd
```

应得到：刚体 78，关节 77，Articulation 根 1 个（`/galbot_one_golf/base_link`），`PhysxMimicJointAPI` 10 个。27 个关节有非零驱动增益，40 个被动滚子增益为 0。

## 资源与耗时

本站实测（2026-09-30，RTX 5070，headless）约 5–6 秒，返回码 0；输出经管道时 "Generated USD file" 行完整。
