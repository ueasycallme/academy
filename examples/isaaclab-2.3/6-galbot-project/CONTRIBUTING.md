# 提交前清单（7.6）

每条后面括号里是出处页。全部打勾再提交；做不到的，在提交说明里写原因。

## 环境

- [ ] `python scripts/check_versions.py` 返回 0。版本不同不是不能提交，但要在说明里写出来（7.6 坑四）。

## 代码

- [ ] 新文件或改过的脚本，文件头写了验证版本、验证日期、GPU 型号；没跑过的写 `# 未验证`。
- [ ] 启动了 `AppLauncher` 的脚本，退出前按顺序做三步：`sim.clear_all_callbacks()` 与 `sim.clear_instance()`（用了 `SimulationContext` 时）→ `sys.stdout.flush()` → `simulation_app.close()`（6.4.5 坑五）。
- [ ] 不写死绝对路径：资产目录用 `assets/paths.py` 的 `generated_asset_dir()`（环境变量 `GALBOT_GENERATED_DIR`），数据放 `DATA.md` 约定的目录（7.5）。
- [ ] 新任务的 `num_envs` 默认值 ≤ 1024，Play 变体 ≤ 16。
- [ ] 新任务 id 照 `Galbot-<任务>[-<变体>]-v<N>` 取名，先 `gym.registry` 查重：重复注册只打一行警告，后注册的覆盖前一个（7.6 坑二）。
- [ ] 改了配置，想清楚要不要重训：dt、decimation、执行器参数、动作的 `scale` / `clip`、观测项都要重训（6.3.1 结论、6.4.5 坑三）。
- [ ] 改机器人配置（执行器分组、关节名）后跑 `python scripts/check_actuator_groups.py`（只需 usd-core，6.1.6）。

## 测试

- [ ] `python3 -m pytest tests -q` 通过（无 GPU 层，7.4）。
- [ ] 改了环境或任务配置：再跑 `$PY -m pytest tests/gpu -m "not slow" -q`（冒烟）。
- [ ] 改了训练相关代码：再跑 `$PY -m pytest tests/gpu -m slow -q`（确定性回归）；指纹变了要说明原因，不要直接重新记录。

## 数字与文档

- [ ] 写进文档的显存是**按进程**测的（`nvidia-smi --query-compute-apps=pid,used_memory`，只算这条命令的进程树），不是整卡读数。
- [ ] README 对应小节写了运行命令与预期输出。
- [ ] 训练前先提交代码，训练带 `--run_name`；记录表里写 commit、Isaac Lab tag、种子（6.5.3）。
