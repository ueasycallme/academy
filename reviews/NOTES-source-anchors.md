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

## 含图页面的校验要点（累积）
- 每张图都要做 headless 截图目检（深浅色各一张），不只看 DOM 尺寸（源自 T-0.2 的漏检）。
- 方向按 D-017：分层/依赖图竖排、底层在下；流程与时间线从左到右；时序图从上到下。校验时先判断图属于哪一类，再看方向是否用对。
- `flowchart BT` 配合"依赖方 --> 被依赖方"的边写法，会把被依赖方画在上方；底层在下的正确写法是 `TB`。
- 子图若作为边的端点，其 `direction` 会被 Mermaid 忽略。

## T-ENV-01 预备（D-019）
- 原文（Isaac Sim 5.1.0 文档每页顶部横幅，2026-09-30）："Unsupported release: Isaac Sim 5.1.0 is no longer supported. Bug fixes and new features are delivered only in newer releases."
- 核对范围：0.1、1.1、1.2 与 Sphinx 公告条；措辞四处要一致；来源用 5.1.0 文档页（任一页均有横幅）；理由写明"2.3.x 最高支持 5.1（README 版本表）；3.0 仍为 EA（v3.0.0-EA release）"。
- Sphinx 站与 MkDocs 站都要检查；Sphinx 公告条位于 `conf.py` 的 `announcement`。

## T-SITE-06 基线（D-020，切换前快照）
- 快照提交：见 `reviews/baseline-pre-site06/HEAD.txt`（4211840）。
- `baseline-pre-site06/site-sphinx-md.sha256`：切换前 `site-sphinx/` 下全部 .md 的 sha256（路径相对 site-sphinx/），切换后与新 `docs/` 逐个比对，应全部一致（除非任务卡要求改动）。
- `formal-pages.txt`：20 个非占位页；切换前 11 个正式页的 docs/ 与 site-sphinx/ 版本已确认一致（md2myst diff = 0），因此以 site-sphinx 为准不会丢内容。
- `pre-0.2-2560.png`：切换前 0.2 页在 2560×1440 下的截图（全新 profile）。
- 还要检查：`tools/check_head_build.sh`、WORKFLOW / CONVENTIONS / README 中 mkdocs 的相关说明已更新；`examples/*/README.md` 中引用的 `docs/…` 路径仍然有效；旧 docs/ 的 `assets/js/mermaid.min.js` 等自托管资源在新站中有对应文件。
