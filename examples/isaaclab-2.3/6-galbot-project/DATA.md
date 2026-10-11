# 数据目录约定（7.5）

本项目产生的数据都不进 git。仓库只放能把它们重新生成出来的代码、参数与清单。

| 目录 | 放什么 | 怎么来 | 能否重新生成 | git |
|---|---|---|---|---|
| `third_party/galbot_one_golf_description/` | 上游描述仓库（URDF、网格） | `scripts/fetch_galbot.sh`，固定 commit | 能（克隆） | 忽略 |
| `generated/galbot_<变体>/` | 转换出的 USD、`MANIFEST.json`（6.1.7） | `scripts/convert_galbot.py` | 能，逐字节相同 | 忽略 |
| `datasets/` | 示教 HDF5（6.4.6 录制、6.4.7 标注与生成） | `record_pick_place.py`、`mimic_pipeline.sh` | 能，但要几分钟到几十分钟 | 忽略 |
| `logs/rsl_rl/<实验>/<时间>_<run_name>/` | 检查点、TensorBoard、`params/`、`git/` | `scripts/rsl_rl/train.py` | 同机同版本同种子时逐位相同（6.5.1）；否则只能重训 | 忽略 |
| `logs/robomimic/` | BC 训练输出（6.4.7） | `mimic_pipeline.sh` | 同上 | 忽略 |
| 评估 CSV、图 | `eval_reach.py --csv` 等的输出 | 评估脚本 | 能 | 忽略，需要留档的拷到 `logs/` 对应运行下 |

**不覆盖**：Isaac Lab 的 HDF5 写入器以 `"w"` 打开文件，同名文件会被清空。`record_pick_place.py` 在文件已存在时默认退出，要覆盖得加 `--overwrite`；Isaac Lab 自带的 `record_demos.py` 不检查，换文件名再录。

**命名**：训练一律带 `--run_name`（如 `seed42`），日志目录就是 `<时间>_seed42`；评估 CSV 命名为 `<运行目录名>_<检查点>_<评估种子>.csv`，放回该运行目录。

**对得上代码**：训练前先提交代码，`logs/.../git/*.diff` 才只记录未提交的部分（6.5.3）；资产版本看 `generated/<变体>/MANIFEST.json`；示教 HDF5 的 `data` 组属性 `env_args` 里记着环境名与仿真参数。

**容器里**：`generated/`、`datasets/`、`logs/` 用命名卷（1.6），需要时拷到宿主。

**外部存储**（NAS、对象存储）：只存不能便宜重生成的东西（检查点、生成的大 HDF5），同时存一份记录它来源的清单。本站没有这样的环境，这条是建议，未验证。
