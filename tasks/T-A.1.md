# T-A.1 Isaac Lab 常用 API 速查表

状态: 已合并
优先级: P1
类型: 参考页
依赖: 第 4 部分全部 P1、第 6 部分 P1
产出: `docs/appendix/A.1-api-cheatsheet.md`（替换占位页）
公共要求: 见 `tasks/T-A-common.md`

## 必须覆盖

1. **范围**：只收本站正文用过或讲过的 `isaaclab.*` API（第 4、6 部分 + 3.11 提到的 Isaac Lab 侧），不做全量 API 索引（那是官方 API 文档的事，链接之）。
2. **分组表**：启动（AppLauncher）、仿真（SimulationContext / SimulationCfg）、场景（InteractiveScene / SceneEntityCfg）、资产（Articulation / RigidObject 及其 `data.*` 常用字段、`write_*` / `set_*` 方法）、执行器（ImplicitActuatorCfg 等）、Manager 配置类（Obs/Action/Reward/Termination/Event/Command/Curriculum 的 *TermCfg 与 *Cfg）、常用 mdp 函数（本站用过的）、工具（`math` 里的四元数函数、`VisualizationMarkers`、`configclass`、转换器 UrdfConverterCfg）、RL 适配层（RslRlOnPolicyRunnerCfg 与 wrapper）。每行：名字（行内代码）→ 一句话用途 → 常用参数/字段（≤ 3 个）→ v2.3.2 permalink → 本站讲它的页面锚点。
3. **数据流一张小图可免**；用"常见组合"一小节给 3–5 个两行代码片段（如取末端位姿、写关节目标、重置若干环境），每个片段注明出自哪页的示例。
4. **3.0 对照列**：在表中加一列"3.0 变化"，只填 8.4 清单里涉及到的（改名 / 类型变化 / 不变），其余留空并注明"未核对"。
5. 维护规则一段。

## 验收标准

每行 permalink 行号指向定义处；站内锚点可达；条目来自站内实际使用（校验方抽 15 行 grep 站内验证）；8.4 一列与 8.4 页一致。

## 附记

### 实现（isaac-academy-accomplish，2026-10-09）

**修改**：只写 `docs/appendix/A.1-api-cheatsheet.md`。重跑了 gen_placeholders。

**生成与核验**：表由 scratchpad 里的 gen_a1.py 生成。
- **定义行**：对 v2.3.2 源码（本地 clean14/IsaacLab，tag v2.3.2）逐个匹配 `^class 名字` 或 `^def 名字(`（也接受 class，因为 v2.3.2 里 `modify_reward_weight` 是类），得到行号再拼成 permalink；匹配不到就报错，所以每个行号都指向定义处。数据属性匹配 `    def joint_pos(` 这类属性定义。
- **站内使用**：先 grep 全站的 `from isaaclab… import` 与 `mdp.*` 用法定出候选；再逐行检查 API 名字确实出现在所链接的页面里（0 处缺失）。第一轮有 9 行链接的页面里没出现这个名字，已改到真正讲它的页面。`quat_error_magnitude` 只在项目代码里用过、正文没讲，按"只收正文讲过的"删掉；export 一行改为 `isaaclab_rl.rsl_rl.exporter`（6.6.1 的脚注引了这个文件）。
- 共 **52 行**，分 9 组：启动、仿真、场景、资产、执行器、环境与 Manager 配置、常用 mdp 函数、工具、RL 适配层与任务工具。
- **3.0 一列**只按 8.4 填（`PhysxCfg` 移动、数据属性改为 `ProxyArray`、四元数 XYZW、写入方法拆分、执行器字段改名、Schema 类拆分、统一的 `--checkpoint` 等），其余写"未核对"。

**常见组合**：5 个片段，都取自本站已讲的用法，注明出处页（4.5、4.6、4.13、6.4.1、7.3）；第三个片段原用了 4.6 没讲的 `default_joint_pos`，已改为普通变量。

**篇幅**：含表 1495（D-027），不超限。表格行多，但每格都很短。

**自查**：按附录公共要求，没有学习目标三节；没有新术语；官方 API 文档链接返回 200；`check_head_build.sh --worktree` 通过。

### 校验附记（isaac-academy-examine，2026-10-09）

**退回**，见 `reviews/T-A.1.md`。52 行全部核对：定义行 52/52 正确，站内页面 52/52 出现，抽查的 10 个参数都对得上。问题 1（低）：Articulation、ManagerBasedRLEnv、DirectRLEnv 三格的 3.0 内容出处是 8.1 而不是 8.4，与本页声明的"只按 8.4 填"不符。

### 实现附记（第二轮，2026-10-09）

按校验问题 1 与设计的裁断（"改成 8.4 口径"）：Articulation、ManagerBasedRLEnv、DirectRLEnv 三格的 3.0 列改为"未核对"，因为 8.4 没有写这三个类，原内容取自 8.1。现在 3.0 列的非"未核对"格都能在 8.4 找到出处；"未核对"共 36 格。生成脚本同步修改，页面与脚本输出逐行一致。`check_head_build.sh --worktree` 通过。

### 校验附记（第二轮，isaac-academy-examine，2026-10-09）

**通过**。三格已改为"未核对"；其余 16 格非"未核对"的都有 8.4 出处；-W 通过。
