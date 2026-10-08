# 5.6 观测设计：去掉关节速度与历史帧的对照

对应页面：`docs/5-rl/5.6-observation-design.md`。

在官方 `Isaac-Cartpole-v0` 上用 Hydra 命令行覆盖做 4 组对照，不改任何文件；`plot_obs_ablation.py` 读 TensorBoard 记录，打印数值并画图。

## 运行（在 Isaac Lab 仓库根目录，已激活环境）

```bash
T="scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless --seed 42"
python $T --run_name obs56_base
python $T --run_name obs56_novel    env.observations.policy.joint_vel_rel=null
python $T --run_name obs56_novel_h3 env.observations.policy.joint_vel_rel=null env.observations.policy.joint_pos_rel.history_length=3
python $T --run_name obs56_base_h3  env.observations.policy.joint_pos_rel.history_length=3 env.observations.policy.joint_vel_rel.history_length=3

python <本仓库>/examples/isaaclab-2.3/5.6-observation-design/plot_obs_ablation.py logs/rsl_rl/cartpole --out obs_ablation.png
```

注意：历史帧要设在**观测项**上（`...joint_pos_rel.history_length=3`）。在观测**组**上设 `env.observations.policy.history_length=3` 会被 Hydra 拒绝：组的这个字段默认是 `None`，报 `Incorrect type ... Expected: <class 'NoneType'>, Received: <class 'int'>`（本站实测）。在 Python 配置里直接赋值不受此限制。

## 预期输出

```text
基线：位置 + 速度     | mean_episode_length: 第 50 次 300.0，第 100 次 300.0，最后 10 次平均 299.4
去掉速度             | mean_episode_length: 第 50 次 209.6，第 100 次 256.8，最后 10 次平均 261.3
去掉速度 + 3 帧历史   | mean_episode_length: 第 50 次 242.6，第 100 次 288.7，最后 10 次平均 298.1
基线 + 3 帧历史       | mean_episode_length: 第 50 次 300.0，第 100 次 300.0，最后 10 次平均 300.0
```

每组训练约 18–29 s，进程显存峰值约 2.9 GB（RTX 5070 12 GB）。单种子结果，复跑时曲线趋势应一致，逐位数值可能因 GPU 非确定性略有差别。

验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2（rsl_rl 3.1.2）；验证日期 2026-10-08。
