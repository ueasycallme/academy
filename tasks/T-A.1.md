# T-A.1 Isaac Lab 常用 API 速查表

状态: 待实现
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

（实现/校验 session 写）
