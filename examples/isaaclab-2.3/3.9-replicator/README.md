# 3.9 Replicator 与合成数据：示例

验证版本：Isaac Sim 5.1.0（pip，omni.replicator.core 1.12.27）；验证日期 2026-10-11；RTX 5070 12 GB。讲解见 [3.9 Replicator 与合成数据](../../../docs/3-isaacsim/3.9-replicator.md)。

| 文件 | 作用 |
|---|---|
| `synth_data.py` | 桌面 + 3 个方块，每帧随机化方块位姿、颜色与环境光，用 `BasicWriter` 写 RGB、语义分割、2D 紧框 |
| `make_mosaic.py` | 把输出拼成 2×2 图（不需要 Isaac Sim） |

```bash
python synth_data.py --frames 200 --out /tmp/synth           # 用 Isaac Sim 的 SimulationApp（默认）
python synth_data.py --frames 5 --out /tmp/nolabel --no_labels
python make_mosaic.py /tmp/synth --out mosaic.png --a 0 --b 100
```

**不要用 Isaac Lab 的 AppLauncher 起这个脚本**：Isaac Lab 的渲染体验文件关掉了 Replicator 的 orchestrator，帧数控制不住，几秒内能写出上千帧。`--launcher lab` 就是这个对照，跑之前给输出目录设一个磁盘上限。确实要在 AppLauncher 下用时，加 `--launcher lab_orch_on`，它通过 `kit_args` 把 orchestrator 重新打开。
