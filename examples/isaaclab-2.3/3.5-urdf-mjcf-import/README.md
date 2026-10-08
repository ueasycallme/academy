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

## 仿真检查

上面的统计只看 USD。转完后还要放进仿真保持几秒，确认没有 NaN，可以用主线项目的 `hold_pose.py`（`examples/isaaclab-2.3/6-galbot-project/scripts/`，需先按项目 README 安装 `galbot_academy`，在项目根目录运行）：

```bash
python scripts/hold_pose.py --headless --usd <本仓库>/galbot_usd/galbot.usd --z 0.05
```

本示例是浮动基座（`fix_base=False`），本站实测 z=0 与 z=0.05 都没有 NaN，放在 z=0 时被地面顶高约 4.5 cm。由于本示例的驱动增益是演示值、mimic 约束未调硬，关节偏离与 mimic 跟随误差都很大（约 0.9 rad），属预期（见页面坑四与 6.1.2）。**如果改成固定根（`fix_base=True`），务必离地放置**：根固定、轮子嵌在地面里时会出现 NaN（页面坑九）。

## 资源与耗时

本站实测（2026-09-30，RTX 5070，headless）约 5–6 秒，返回码 0；输出经管道时 "Generated USD file" 行完整。
