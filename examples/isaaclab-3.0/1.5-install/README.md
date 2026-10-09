# 1.5 安装 Isaac Sim 6.1 + Isaac Lab 3.0-EA：验证脚本

对应页面：`docs/1-env/1.5-install-61-30.md`。

验证版本：Isaac Lab v3.0.0-EA（commit ae37b028e）+ Isaac Sim 6.1.0.0（pip，可选）；Ubuntu 22.04，RTX 5070 12 GB，驱动 580.178.04，2026-10-09。

`examples/isaaclab-3.0/` 从本页起专放 3.0 EA 的示例，与 `examples/isaaclab-2.3/` 分开。

## verify_install_30.py

只做导入与版本检查，不启动仿真：Python 3.12、PyTorch（CUDA 可用）、warp-lang、newton、Isaac Lab 各包及导入路径、Isaac Sim（可选）。

```bash
# 路线 A：在 Isaac Lab 3.0 仓库根目录
uv run python /path/to/verify_install_30.py --require-isaacsim

# 路线 B / C：先激活对应环境
python verify_install_30.py                     # 路线 C 不装 Isaac Sim，该项记为 SKIP
python verify_install_30.py --require-isaacsim  # 路线 B
```

本站实测输出：路线 A、B 为 `SUMMARY: 10/10 passed`，路线 C 为 `SUMMARY: 9/9 passed, 1 skipped`；在 5.1 的环境里运行为 `6/10`（Python、torch、isaacsim 版本不符），可用来发现用错了环境。退出码：有失败项为 1，否则为 0。

## 仿真验证（官方命令）

```bash
# Newton 后端，不需要 Isaac Sim
uv run isaaclab train --rl_library rsl_rl --task Isaac-Cartpole-Direct physics=newton_mjwarp
# PhysX 后端，经 Isaac Sim 6.1（需要 isaacsim extra 与 EULA）
OMNI_KIT_ACCEPT_EULA=YES uv run --extra isaacsim isaaclab train --rl_library rsl_rl \
    --task Isaac-Cartpole-Direct physics=isaacsim_physx
```

耗时、显存与主机内存的实测值见页面表 3。
