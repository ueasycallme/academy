# 校验用源码锚点（Isaac Lab v2.3.2，本地 commit 37ddf6268）

供后续校验对照，非校验报告。

## `ManagerBasedRLEnv.step()`（`source/isaaclab/isaaclab/envs/manager_based_rl_env.py` L153 起）
1. `action_manager.process_action(action)`：每个 env step 只处理一次
2. `recorder_manager.record_pre_step()`
3. decimation 循环（`cfg.decimation` 次），每次依次执行：
   `action_manager.apply_action()` → `scene.write_data_to_sim()` → `sim.step(render=False)` → `record_post_physics_decimation_step()` → 满足 `render_interval` 且有 GUI 或 RTX 传感器时 `sim.render()` → `scene.update(dt=physics_dt)`
4. `episode_length_buf += 1`，`common_step_counter += 1`
5. `termination_manager.compute()`：得到 `reset_buf`、`terminated`、`time_outs`
6. `reward_manager.compute(dt=step_dt)`：**先算终止，再算奖励**
7. 若 recorder 有激活项：先算一次 obs，再 `record_post_step()`
8. 对需要 reset 的环境调用 `_reset_idx(ids)`；有 RTX 传感器时按 `num_rerenders_on_reset` 补渲染；然后 `record_post_reset`
9. `command_manager.compute(dt=step_dt)`
10. `event_manager.apply(mode="interval")`
11. `observation_manager.compute(update_history=True)`：**obs 在 reset 之后计算**，所以 reset 过的环境返回的是新回合的第一帧观测
12. 返回 `(obs, reward, terminated, time_outs, extras)`

## `_reset_idx(env_ids)`（L349 起）
`curriculum_manager.compute` → `scene.reset` → `event_manager.apply(mode="reset")` → 依次调用各 manager 的 `.reset()` 并把返回的 info 写进 `extras["log"]`（顺序：observation、action、reward、curriculum、command、event、termination、recorder）→ `episode_length_buf[ids] = 0`

## T-SITE-03 预备（2026-09-30）
- PyPI：`nvidia-sphinx-theme` 0.0.9.post1，license 字段为 "NVIDIA LICENSE AGREEMENT"，分类为 `Other/Proprietary License`，与卡片所述一致；`pydata-sphinx-theme` 0.22.0 为 BSD（OSI）。
- 校验要点：
  - 确认构建产物中没有 `nvidia_sphinx_theme` / NVIDIA logo / NVIDIA 字体（grep `nvidia`、`NVIDIA-Sans`、`.woff` 来源）。
  - 屏蔽外网截图用 `--host-resolver-rules="MAP * ~NOTFOUND, EXCLUDE 127.0.0.1"`，另加 `--log-net-log`。
  - 中文搜索：检查 `searchindex.js` 是否按 jieba 分词，并在浏览器里实际搜一个中文词。
  - Mermaid：深浅色各截图一张，**目视确认方向与可读性**。
  - MIGRATION-NOTES：拿 0.2 页原文逐个语法元素对照转换，看有没有遗漏（admonition 各类型、可折叠 `???`、tabs、脚注、attr_list、Mermaid fence、frontmatter、站内相对链接 `.md`）。
