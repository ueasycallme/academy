# 8.8 Kit-less 工作流实测：脚本

对应页面：`docs/8-frontier/8.8-kitless.md`。

| 文件 | 说明 |
|---|---|
| `time_train.py` | 给一条 `isaaclab train` 计时：启动到第一次迭代、每次迭代的墙上时间（本脚本在读到每行 `Learning iteration k/N` 时打时间戳，被计时的进程要设 `PYTHONUNBUFFERED=1`） |
| `ovrtx_frame.py` | 用 `Isaac-Cartpole-Camera-Direct` 的 tiled camera 出一帧：每步耗时、输出形状，存首个环境的 RGB 与 4×4 拼图 |

## 环境

- Kit-less：1.5 路线 C，另装 `ov[ovrtx]`、`visualizer[rerun]`、`visualizer[viser]`（分开写，页面坑一）。不装 Isaac Sim。
- 对照：1.5 路线 A（装了 `isaacsim` 6.2.0.0）。
- 版本：Isaac Lab v3.0.0（commit e3f7d9ff1），ovrtx 0.5.1；RTX 5090 32 GB，驱动 580.178.04（2026-10-23）。

## 运行

```bash
export PYTHONUNBUFFERED=1
python time_train.py -- isaaclab train --rl_library rsl_rl --task Isaac-Cartpole-Direct --num_envs 4096 --max_iterations 100 physics=newton_mjwarp
python ovrtx_frame.py --num_envs 64 --steps 50 --out ovrtx_cartpole.png physics=newton_mjwarp renderer=ovrtx
python ovrtx_frame.py --num_envs 64 --steps 50 --out newton_cartpole.png physics=newton_mjwarp renderer=newton_renderer
```

`time_train.py` 只计时；显存与 RSS 本站用外部脚本每秒采样（`nvidia-smi --query-compute-apps` 按进程树累加、`/proc/<pid>/status` 的 VmRSS）。测量时 GPU 上不要有别的计算进程，也不要同时构建或开浏览器。

## 预期输出（本站实测，v3.0.0，RTX 5090 32 GB，2026-10-23）

```text
[8.8] rc 0；启动到第一次迭代 6.9 s；每次迭代 均值 68.4 ms、中位 68.4 ms（65.8–71.1，89 次，跳过前 10 次）；rsl_rl 自报中位 0.07 s；总用时 15.2 s
[8.8] 相机 96×96，64 台；数据类型 ['rgb']
[8.8] 输出 (64, 96, 96, 3)，dtype <class 'warp._src.types.uint8'>，像素均值 2.8（全 0 即黑帧）
[8.8] 每步（含物理 2 步与一次渲染）中位 5.01 ms、最小 4.80、最大 6.47 ms（50 步，前 10 步不计）；torch 显存峰值 31 MiB
```

第一行是路线 C + Newton；OVRTX 的像素均值低，是因为这个场景背景为黑色（页面图 3），不是黑帧。三种组合与两种渲染器的完整数字见页面表 2、表 3。

## 需求与时长

- 显存（按进程）：训练 756 MiB（Newton）/ 3286 MiB（Isaac Sim PhysX）；OVRTX 出帧约 3.6 GB，Newton 渲染器 690 MiB。
- 每次约 10–25 s（含启动）。`ovrtx` 包本身 2.6 GB，首次安装下载较慢；装好后第一次运行 OVRTX 约 5 分钟、主机内存峰值 13.9 GB，之后约 10 s。
