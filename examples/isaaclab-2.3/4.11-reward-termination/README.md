# 4.11 Reward / Termination / Curriculum：给 Cartpole 加奖励、终止与课程

对应页面：`docs/4-isaaclab/4.11-reward-termination-curriculum.md`。

继承官方 Cartpole 配置，加三处：

- 奖励 `action_rate`：`mdp.action_rate_l2`，权重 −0.01；
- 终止 `pole_fallen`：`mdp.joint_pos_out_of_manual_limit`，摆杆超出 ±90° 即失败；
- 课程 `action_rate`：`mdp.modify_reward_weight`，环境步计数超过 100 后把上面的权重改为 −0.1。官方 Cartpole 没有课程配置，脚本新建了一个。

脚本运行 320 步（回合上限为 300 步），打印：

- 第 1 步的分项奖励，并核对 Σ(func × weight) × dt 与环境返回的奖励相等；
- 失败 / 超时次数；
- 最近一次重置时的 `Episode_Reward/*`、`Episode_Termination/*`、`Curriculum/*`。

## 运行

在主线环境中（已激活 `env_isaaclab`）：

```bash
python examples/isaaclab-2.3/4.11-reward-termination/reward_termination_demo.py --headless
python examples/isaaclab-2.3/4.11-reward-termination/reward_termination_demo.py --headless --zero_action --no_pole_fallen
```

## 预期输出（本站实测，种子 42，重复运行输出一致）

第一条（随机动作，含 `pole_fallen`）：

```text
step_dt 0.01667 s，episode_length_s 5，回合上限 300 步
Σ × dt = 0.012269，env 返回的奖励 = 0.012269
320 步内：terminated（失败）148 次，truncated（超时）0 次
当前 action_rate 权重 -0.1（课程已生效）
  Curriculum/action_rate                   -0.1000
  Episode_Reward/alive                      0.1633
  Episode_Termination/pole_fallen           1.0000
  Episode_Termination/time_out              0.0000
```

第二条（零动作，不加 `pole_fallen`）：

```text
320 步内：terminated（失败）0 次，truncated（超时）16 次
  Episode_Reward/alive                      1.0000
  Episode_Reward/pole_pos                  -5.5409
  Episode_Termination/time_out              1.0000
```

页面"读训练日志"一节的片段来自：

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless env.scene.num_envs=64 agent.max_iterations=2
```

在 Isaac Lab 仓库根目录运行，约 12 秒，返回码 0。

## 资源与耗时

显存占用很小。示例每次约 8–9 秒，返回码 0（2026-09-30，RTX 5070，headless）。环境的 `close()` 会释放 SimulationContext，之后 flush，再关闭 app。
