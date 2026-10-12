# AUDIT-02b 390 px 宽度下的表格、代码块与 Mermaid

校验 session：isaac-academy-examine，2026-10-12
任务卡：`tasks/T-AUDIT-02b.md`（AUDIT-02 B10 补做）
基准：HEAD `869fe0d` 的克隆构建（`scratch/examine/audit02b/html`，与 AUDIT-02 复跑同一份 HTML；96e1b99 没有改 docs/）。不改页面。
脚本：`reviews/scripts/audit-mobile.py`（新），已作为可选项接进 `audit-all.sh`：`MOBILE=1` 时才跑，默认跳过。

## 1. 汇总

| 检查 | 范围 | 结果 | 阻塞 | 一般 | 建议 |
|---|---|---|---|---|---|
| 页面是否撑破 | 386aa36 之后新增的 39 页（含 P3 十页） | **30 页撑破**：页面本身没有水平滚动条，但正文容器 `.bd-article-container` 整体横滚，最多 506 px（6.4.7）。原因全部相同，见 G-1 | 0 | 1 | 0 |
| 表格 | 39 页共 122 张 | 50 张比屏宽，都在主题的 `.pst-scrollable-table-container` 里横向滚动；超出视口 0 | 0 | 0 | 0 |
| 代码块 | 80 个 | 都在自己的框里横向滚动，超出视口 0 | 0 | 0 | 0 |
| Mermaid 图 | 14 张 | 全部缩放到容器内，超出 0 | 0 | 0 | 0 |
| 全站（范围外，供参考） | 123 页 | 撑破 88 页；套用 G-1 的改法后剩 2 页，见 S-1 | 0 | 0 | 1 |

## 2. 一般

**G-1　正文与脚注里的行内代码不换行，30 页的正文在手机上整体横滚（站点样式问题，只报一条）**

- **现象**：390 px 下，长路径、长类名写成行内代码（`code.docutils.literal`）时不会折行，右边缘越出视口。主题的 `.bd-article-container` 是 `overflow-x: auto`，所以页面本身不出滚动条，而是整篇正文跟着左右滑。读者横滑一下，所有段落都跟着移出屏幕。
- **位置**：越界的 118 处中，脚注 83 处（全是源码路径，如 `isaaclab_tasks/manager_based/manipulation/stack/config/franka/…`），正文 35 处：段落与列表项里的行内代码 24 处（路径、`carb.settings.get_settings().set_string(…)` 之类）；因行内代码而溢出的列表项 10 处；表注 `<em>` 里的长路径 1 处。逐页明细见第 4 节表。
- **原因**：
  - Sphinx 给行内代码的 `span.pre` 设了 `white-space: nowrap`。
  - 本站的 `docs/_static/css/academy.css` L144–L145（T-SITE-09）只在**表格里**把它改回可折行，`docs/_static/js/table-code-wbr.js` L22 也只给 `.bd-article table code` 插 `<wbr>` 断行点。
  - 表格外的行内代码都没覆盖到。
- **对照（证实）**：在 HTML 的副本里（`scratch/examine/audit02b_fix`，不碰 docs/）只改两处：
  1. `academy.css` 末尾加 `.bd-article code, .bd-article code .pre { overflow-wrap: break-word; white-space: normal; }`；
  2. `table-code-wbr.js` 的选择器由 `.bd-article table code` 改为 `.bd-article code`。

  重量结果：
  - 39 页的撑破由 **30 → 0**；
  - 全站由 **88 → 2**；
  - 表格、代码块、Mermaid 的计数不变：代码块是 `pre`，不受影响；表格仍在各自的容器里滚动。
- **建议**：按上面两处改 `docs/_static`，并更新 L141–L143 的注释与 `table-code-wbr.js` 头注里"表格内"的说法。改完 1440 / 2560 下段落里的短代码不受影响（只在放不下时才折行），但仍建议目检一页。

## 3. 建议

**S-1　全站范围外的 2 页（套用 G-1 改法后仍横滚）**

| 页 | 正文横滚 | 原因 | 建议 |
|---|---|---|---|
| 1.1 | 96 px | 脚注 `[^sim45]` 是纯文本 `docs.isaacsim.omniverse.nvidia.com/4.5.0/、/5.0.0/`，没有空格，也不是代码或链接 | 写成行内代码（G-1 改后可折行），或改成两个链接 |
| 0.6 | 15 px | 一条脚注被引用 20 次，Sphinx 生成的回链 `(1,2,3,…,20)` 没有空格 | 可在 academy.css 给 `.footnote .backrefs` 加 `overflow-wrap: anywhere`；或不改，影响很小 |

## 4. 逐页结果（39 页，修改前）

| 页面 | 结果 | 正文横滚 | 超出元素：脚注 / 正文 | 最宽的一处（右边缘 px，视口 375） |
|---|---|---|---|---|
| 1-env/1.6-container | 撑破 | 37 px | 2 / 1 | `examples/isaaclab-2.3/1.6-container/Dockerfile`（412） |
| 1-env/1.8-dev-tools | 撑破 | 53 px | 1 / 2 | `examples/isaaclab-2.3/1.8-dev-tools/.vscode/`（428） |
| 2-usd-kit/2.8-nucleus | 撑破 | 206 px | 3 / 2 | `site-packages/isaacsim/kit/data/Kit/Isaac-Sim/5.`（581） |
| 3-isaacsim/3.10-ros2-bridge | 撑破 | 532 px | 3 / 1 | `isaaclab_tasks/manager_based/manipulation/deploy`（907） |
| 3-isaacsim/3.6-sensors | 撑破 | 137 px | 2 / 3 | `isaaclab/sensors/contact_sensor/contact_sensor_d`（512） |
| 3-isaacsim/3.7-cloner | 撑破 | 1 px | 0 / 1 | `SimulationCfg.create_stage_in_memory`（376） |
| 3-isaacsim/3.8-rendering | 撑破 | 165 px | 2 / 2 | `carb.settings.get_settings().set_string("/rtx/re`（540） |
| 3-isaacsim/3.9-replicator | 撑破 | 65 px | 4 / 3 | `exts."omni.replicator.core".Orchestrator.enabled`（440） |
| 4-isaaclab/4.17-multi-agent | 撑破 | 145 px | 4 / 1 | `direct/cart_double_pendulum/cart_double_pendulum`（520） |
| 4-isaaclab/4.19-mimic | 撑破 | 179 px | 7 / 2 | `scripts/imitation_learning/isaaclab_mimic/annota`（554） |
| 4-isaaclab/4.20-teleop-devices | 撑破 | 397 px | 6 / 2 | `isaaclab_tasks/manager_based/manipulation/stack/`（772） |
| 4-isaaclab/4.8-sensors | 撑破 | 145 px | 10 / 1 | `isaaclab/sensors/frame_transformer/frame_transfo`（520） |
| 6-galbot/1-asset/6.1.7-asset-versioning | 撑破 | 2 px | 1 / 0 | `sim/converters/asset_converter_base.py`（377） |
| 6-galbot/2-scene/6.2.2-wrist-camera | 撑破 | 222 px | 2 / 3 | `right_arm_link7/right_arm_wrist_camera_stand/rig`（597） |
| 6-galbot/4-task/6.4.3-lift | 撑破 | 204 px | 3 / 0 | `isaaclab_tasks/manager_based/manipulation/lift/l`（579） |
| 6-galbot/4-task/6.4.5-base-navigation | 撑破 | 212 px | 2 / 1 | `manager_based/locomotion/velocity/config/digit/r`（587） |
| 6-galbot/4-task/6.4.6-teleop-demos | 撑破 | 165 px | 3 / 2 | `FRANKA_PANDA_HIGH_PD_CFG.spawn.rigid_props.disab`（540） |
| 6-galbot/4-task/6.4.7-mimic | 撑破 | 506 px | 9 / 0 | `isaaclab_tasks/manager_based/manipulation/stack/`（881） |
| 6-galbot/5-train/6.5.4-multi-gpu | 撑破 | 69 px | 2 / 0 | `scripts/reinforcement_learning/rsl_rl/train.py`（444） |
| 6-galbot/7-deploy/6.7.1-policy-export | 撑破 | 61 px | 1 / 0 | `scripts/reinforcement_learning/rsl_rl/play.py`（436） |
| 6-galbot/7-deploy/6.7.2-ros2-closed-loop | 撑破 | 414 px | 1 / 0 | `source/galbot_academy/galbot_academy/tasks/manag`（789） |
| 7-infra/7.4-testing-ci | 撑破 | 187 px | 3 / 2 | `source/isaaclab/test/envs/test_action_state_reco`（562） |
| 7-infra/7.5-data-management | 撑破 | 254 px | 3 / 0 | `source/isaaclab/isaaclab/utils/datasets/hdf5_dat`（629） |
| 7-infra/7.6-team-conventions | 撑破 | 61 px | 1 / 0 | `source/isaaclab/isaaclab/utils/configclass.py`（436） |
| 8-frontier/8.2-multi-backend | 撑破 | 11 px | 2 / 0 | `isaaclab/physics/physics_manager_cfg.py`（386） |
| 8-frontier/8.3-newton | 撑破 | 44 px | 1 / 0 | `newton/_src/solvers/mujoco/solver_mujoco.py`（419） |
| 8-frontier/8.5-galbot-reach-30 | 撑破 | 86 px | 2 / 2 | `isaaclab_rl/entrypoints/backends/train_rsl_rl.py`（461） |
| 9-source/9.1-rl-env-step | 撑破 | 105 px | 0 / 1 | `ManagerBasedRLEnv.step()`（480） |
| 9-source/9.3-articulation-data | 撑破 | 19 px | 1 / 0 | `assets/articulation/articulation_data.py`（394） |
| 9-source/9.4-train-script | 撑破 | 102 px | 2 / 3 | `scripts/reinforcement_learning/rsl_rl/train.py`（477） |

正常 9 页：6.2.3、6.3.1、6.3.2、6.4.4、6.6.2、6.7.3、7.2、9.2、A.4

"超出元素"只计最外层越界的元素：一段里的行内代码越界时，算代码，不再算它所在的段落。正文一列含 10 个被标为"文字溢出"的列表项，原因同样是其中的行内代码。

## 5. 方法与局限

| 项 | 做法 | 局限 |
|---|---|---|
| 视口 | headless Chrome 打开同源测试页，用 390 px 宽的 iframe 逐页加载。iframe 宽度就是页面视口，主题的移动端媒体查询按它生效：侧栏收起，正文宽 375 px，另 15 px 是滚动条。不用 `--window-size=390`，因为 headless Chrome 的窗口最小只到约 485 px，本 session 实测 body 宽 485 | 没有模拟触屏与设备像素比，只看 CSS 像素宽度 |
| 撑破判断 | 满足任一条即算撑破：页面 `scrollWidth − clientWidth > 1`；正文容器 `.bd-article-container` 的 `scrollWidth − clientWidth > 1`；有元素右边缘越出容器且没有被它和容器之间的祖先裁掉 | 表格、代码块各自的滚动容器算正常。"能滚"不等于"好读"，很宽的表在手机上要滑很远，这类只计数不列问题 |
| 文字溢出 | 段落、列表项等块元素自身 `scrollWidth > clientWidth` 时也报。无空格的纯文本长串没有子元素盒子，只能这样查。1.1 就是这种情况：初版脚本只看元素盒子，漏报了，逐层隐藏元素二分后才定位到 | — |
| 负对照 | 在一页里注入 300 个连续字母与一个 700 px 宽的 div | 初版判定为"正常"：没算到 `.bd-article-container` 自带的 overflow-x:auto，越界元素被它"接住"后不算撑破。改为以它为页面级边界后能报出 |
| 内存 | 每次起 Chrome 前看 `free -g`；有一次 available 降到 3 GB，等到回到 4 GB 才跑最后一轮 | 巡检期间实现方在跑 T-6.4.5b 的训练 |
| 范围 | 39 页（386aa36 时是占位页、869fe0d 时是正式页），含 P3 十页 | 只查水平方向。位图没有单独统计，但越界检查覆盖所有元素，没有报出 `img` |
