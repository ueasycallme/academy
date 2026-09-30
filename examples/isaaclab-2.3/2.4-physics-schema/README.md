# 2.4 Schema：列出资产上的物理 Schema

对应页面：`docs/2-usd-kit/2.4-physics-schema.md`。

## 准备

与 2.2 相同：把 Galbot One Golf 描述仓库克隆到 `third_party/` 并切到 commit `2d496b0`（见 `../2.2-usd-concepts/README.md`）。

## 运行

在本仓库根目录执行，usd-core 环境或主线 Isaac Sim 环境均可：

```bash
python examples/isaaclab-2.3/2.4-physics-schema/list_physics_schemas.py            # 默认 Galbot
python examples/isaaclab-2.3/2.4-physics-schema/list_physics_schemas.py my_robot.usd --prims 20
```

脚本读取每个 Prim 的 `apiSchemas` 元数据（而不是 `GetAppliedSchemas()`），因此在只装 usd-core、没有注册 PhysxSchema 的环境里，也能看到 `Physx…API`。

## 预期输出（Galbot，节选）

```text
== 统计 ==
刚体 78，关节 77（带驱动 27），碰撞体 184
网格碰撞近似方式：{'convexHull': 144}
Articulation 根：['/galbot_one_golf/base_link']
PhysicsScene：无（场景由使用方创建，Isaac Lab 默认建在 /physicsScene）

== 检查 ==
[OK] Articulation 根数量为 1（Isaac Lab 要求恰好一个）
[OK] 嵌套刚体 0 个
[OK] 关闭碰撞的碰撞体 0 个
```

## 验证记录

2026-09-30：usd-core 26.8 与 Isaac Sim 5.1.0 pip 环境均运行通过，返回码 0，两者输出一致（Isaac Sim 环境仅多出 Kit 的日志行）。
