# 1.6 容器化环境：示例文件

**未验证（本机无 Docker）**。这些文件照 Isaac Sim 5.1.0 的容器文档和 Isaac Lab v2.3.2 的 `docker/` 目录写成。本站只做了静态检查：

- `compose.yaml` 能被 Python 的 yaml 解析；
- `run.sh` 通过 `bash -n` 语法检查；
- `Dockerfile` 逐行对照过 Isaac Lab 的 `Dockerfile.base`。

讲解见 [1.6 容器化环境](../../../docs/1-env/1.6-container.md)。

| 文件 | 作用 |
|---|---|
| `Dockerfile` | 在 `nvcr.io/nvidia/isaac-sim:5.1.0` 上装 Isaac Lab 2.3.2（带 rsl_rl）、本站 `galbot_academy`，并克隆 Galbot 描述仓库 |
| `compose.yaml` | GPU 透传、宿主网络、缓存与产物的命名卷 |
| `run.sh` | 依次执行：构建 → 转换 USD → 10 次迭代冒烟训练 → 把日志拷到 `artifacts/` |

前提：宿主装好 NVIDIA 驱动（Isaac Sim 5.1.0 测试版本为 Linux 580.65.06）、Docker 与 NVIDIA Container Toolkit。

```bash
cd examples/isaaclab-2.3/1.6-container
./run.sh
```
