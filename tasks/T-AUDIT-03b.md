# T-AUDIT-03b 用户实测回填：4.20 / 6.7.1 / 6.1.x 的"推断 / 未验证"改为实测结论

状态: 已合并
优先级: P2（微卡，只改文字，约 30 min；不跑 GPU，可穿插在 T-1.6b 的构建等待里做）
类型: 文字回填
依赖: T-AUDIT-03（已合并；本卡是其报告里 3 个"本站没跑过"项目的收尾）
产出: `docs/4-isaaclab/4.20-teleop-devices.md`、`docs/6-galbot/7-deploy/6.7.1-policy-export.md`、`examples/isaaclab-2.3/6-galbot-project/scripts/{check_contacts,gravity_torques,probe_stuck_joint}.py` 首行标注

## 背景

三处断言本站 session 没有条件自己跑（桌面 / ROS 2 / 资产默认路径），用户 2026-10-20 09:17–09:20 在本机按设计方给的脚本跑了一遍。原始日志在 `~/wuql_ws/academy_ws/scratch/user/02_item1_teleop.log`、`02_item2_ros_node.log`、`02_item3_scripts.log`，实现方与校验方都直接读这三份原件，不要重跑。环境：实现方的 5.1 环境 `env_isaaclab23_51`、`policy_venv`（onnxruntime 1.20.1）、`proj6`，RTX 5090、驱动 580.178.04。

## 实测结果（设计方从日志摘出）

1. **4.20 坑一（L131）**：`teleop_se3_agent.py --task Isaac-Lift-Cube-Franka-IK-Rel-v0 --teleop_device keyboard --headless` 完成环境创建后打印
   `WARNING: No teleop device 'keyboard' found in environment config. Creating default.`
   `ERROR: Failed to create teleop device: module 'omni' has no attribute 'appwindow'`
   然后进程结束，**退出码 0**（不是非零）。与页面推断一致，另外多了"退出码为 0"这一事实。
2. **6.7.1 L118**：ROS 2 Humble 下 `reach_policy_node.py --ros-args -p onnx:=… -p spec:=…` 启动，日志
   `[reach_policy]: spec ok: ['joint_pos', 'joint_vel', 'pose_command', 'actions']`
   `[reach_policy]: loaded …/deploy/policy.onnx: input obs ['batch', 28], onnxruntime 1.20.1`
   节点随后正常常驻（20 s 后被 timeout 结束）。
3. **6.1.x 三个脚本**：`check_contacts.py` / `gravity_torques.py` / `probe_stuck_joint.py` 不带 `--usd`、在 `/tmp` 目录下、`GALBOT_GENERATED_DIR` 指向 generated 目录运行，三个都 rc=0，默认路径解析正确，输出与各页记录同量级（如 check_contacts 零位最大偏离 0.0355 rad right_arm_joint2；probe_stuck_joint 8 s 后 right_arm_joint3 误差 1.4491 rad，重力补偿 -4.28 N·m）。日志里的 `Unresolved reference … </visuals/head_link1>` 是 6.1.2 已记录的预期警告。

## 要改什么

- 4.20 L131：把"（L227–L231；本站没有单独跑这一步，推断）"改成实测表述，并补"进程以退出码 0 结束"（这对写自动化脚本的读者有用：不能靠退出码发现设备没建成）。日期 2026-10-20、用户在本机实测；不新增数字。
- 6.7.1 L118："未验证（本站 session 未在 ROS 2 下实跑）"改为实测通过，写明 ROS 2 Humble、onnxruntime 1.20.1、日期；可引上面两行日志（≤ 一句）。
- 三个脚本第 5 行括号"（--usd 默认值为 T-0.8n 所改：未单独验证）"改为"（--usd 默认值 2026-10-20 验证）"之类；GPU 行不改（原数字仍是 RTX 5070 测的，D-032）。
- 如果 6.1.4 / 6.1.5 页或 8.6 有引用这个"未单独验证"的句子，一并改；没有就不动。
- 不改 `verified:` front matter 的版本串（版本没变）。

## 校验（examine）

对照三份原始日志核文字；-W 构建；确认脚本首行标注格式符合 CONVENTIONS。不跑脚本。

## 验收标准

三处不再出现"推断 / 未验证"的限定；每处写明 2026-10-20 实测与环境；校验通过。

## 附记

（实现/校验 session 写）

**实现（accomplish，2026-10-20）**：只读了三份原件，未重跑。
- 4.20 L131：去掉"本站没有单独跑这一步，推断"，改为 2026-10-20 本机（RTX 5090）实测，补"退出码是 0"及"要看日志里那行 ERROR"一句（日志 02_item1 L138–L140：WARNING、ERROR、rc=0）。
- 6.7.1 L118：改为"2026-10-20 在本机实测通过（ROS 2 Humble、onnxruntime 1.20.1，RTX 5090 主机）"，并概述两行日志（spec ok；obs ['batch', 28]）。rc=124 是 timeout 20 s 的结果，正文写"之后正常常驻"。
- 三个脚本第 5 行：括号改为"（--usd 默认值 2026-10-20 验证：不带 --usd 在 /tmp 下运行，rc=0）"，GPU 行未改。用户实际跑的是 proj6 副本：与仓库版逐个 diff，除第 5 行注释外完全一致（proj6 副本原注释是"验证日期 2026-10-12"），改后已 cp 同步到 proj6。
- grep docs/ 无其他"未单独验证 / 本站没有单独跑这一步 / ROS 2 下实跑"引用，6.1.4 / 6.1.5 / 8.6 不动。两页 `updated:` 改为 2026-10-20，`verified:` 未动。
- gen_placeholders 只改了 index.md 的生成日期；check_head_build --worktree：-W 构建通过。8.6 表 2 页数不变。

**校验（examine，2026-10-20，第 1 轮）**：退回，2 条低级问题，同轮可修，见 `reviews/T-AUDIT-03b.md`。
- 三处改动与 `02_item1/2/3` 原件逐条一致：4.20 日志 L138–L140；6.7.1 两行 INFO 加 rc=124（timeout）；三个脚本 rc=0，且不带 `--usd` 加载的就是默认路径。用户跑的 teleop 脚本与 v2.3.2 逐字相同。-W 通过（快照 4531d39）。
- 问题 1：`examples/isaaclab-2.3/6-galbot-project/README.md` L545 仍写"未验证（本站 session 未在 ROS 2 下实跑）"。
- 问题 2：6.7.1 L118 的"RTX 5090 主机"建议去掉，或改为"CPU 推理"。节点用的是 `CPUExecutionProvider`。


**实现第 2 轮（accomplish，2026-10-20）**：① README L545 改为"2026-10-20 在本机实测通过（ROS 2 Humble、onnxruntime 1.20.1，CPU 推理）"；② 6.7.1 L118 "RTX 5090 主机"改为"CPU 推理"（设计裁断）。grep docs/ 与 examples/ 已无"ROS 2 下实跑 / 未单独验证 / 本站没有单独跑这一步"。

**校验（examine，2026-10-20，第 2 轮）**：通过。README L545 与 6.7.1 L118 都已改为"实测通过（ROS 2 Humble、onnxruntime 1.20.1，CPU 推理）"；docs/、examples/ 不再有残留；快照 e7cd10b，-W 通过。
