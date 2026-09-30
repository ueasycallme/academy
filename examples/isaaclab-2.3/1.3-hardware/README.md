# 1.3 显存与吞吐实测

对应页面：`docs/1-env/1.3-hardware.md`。

## 运行

在装好 Isaac Sim 5.1.0 + Isaac Lab 2.3.2 的环境中：

```bash
# headless
python measure_vram.py --task Isaac-Reach-Franka-v0 --num_envs 256  --headless
python measure_vram.py --task Isaac-Reach-Franka-v0 --num_envs 1024 --headless
python measure_vram.py --task Isaac-Reach-Franka-v0 --num_envs 4096 --headless
# 带 GUI（会打开 Isaac Sim 窗口）
python measure_vram.py --task Isaac-Reach-Franka-v0 --num_envs 256
```

每次运行在最后打印一行 `RESULT {...}`。汇总这些行即可得到页面中的表格。

## 预期输出

`RESULT` 行包含：`rl_steps_per_s`（每秒 RL step 数）、`env_steps_per_s`（每秒环境步数 = RL step × num_envs）、`baseline_mib`（启动前整卡显存）、`peak_mib`（运行期间整卡显存峰值）、`peak_minus_baseline_mib`、`torch_max_allocated_mib`（仅 PyTorch 分配器部分）。

## 需求与时长

- 显存：num_envs = 4096 时约需数 GB，数值见页面实测表。
- 首次运行需编译着色器、加载扩展缓存，可能需要数分钟；之后每次约 1–2 分钟。
- 测量前请关闭其他占用 GPU 的程序，否则整卡显存读数偏大。

## 本站实测结果

原始 `RESULT` 行保存在 `results-2026-09-30.jsonl`（每次运行一行；`h`、`h2` 为 headless 的两次，`g` 为 GUI）。单次运行约 1 分钟（不含首次缓存编译）。

## 本站实测环境

RTX 5070 12 GB，驱动 580.178.04，Ubuntu 22.04（内核 6.8），Isaac Sim 5.1.0（pip，Python 3.11），Isaac Lab 2.3.2。本站的校验环境中，Isaac Lab 的 editable 安装路径失效，需临时设置 `PYTHONPATH` 指向各 `source/` 包，详见 `reviews/ENV.md`；这是本机环境问题，不是脚本要求。

## 补测：按进程口径的显存（2026-09-30，T-1.3b）

`measure_vram.py` 记录的是整卡读数（`memory.used`），包含桌面与其他进程的占用。按 CONVENTIONS 第 5 节，另用"按进程"口径补测了同样的配置：运行期间每 0.5 秒执行一次 `nvidia-smi --query-compute-apps=pid,used_memory --format=csv`，只累加本脚本进程树的用量，取峰值。

| 模式 | num_envs | 显存峰值（按进程） |
|---|---|---|
| headless | 256 / 1024 / 4096 | 2381 / 2517 / 3177 MiB（各 2 次，读数相同） |
| GUI | 256 / 1024 / 4096 | 5076 / 5150 / 5976 MiB（各 1 次） |

同一次运行的整卡峰值比按进程多约 530–560 MiB，大致就是启动前桌面等占用的量。
