# T-AUDIT-03b 校验报告：4.20 / 6.7.1 / 6.1.x 的"推断 / 未验证"改为用户实测结论

校验 session：isaac-academy-examine，2026-10-20
结论：**通过**（第 2 轮；第 1 轮退回的 2 条低级问题已修，见文末）

- 三处改动与用户的三份原始日志逐条一致。
- 有 1 处同样的"未验证"句子没有改到：示例 README 里的那句（问题 1）。
- 6.7.1 的硬件标签容易让人误以为节点用了 GPU（问题 2）。
- 按卡要求只读日志，不重跑脚本。

## 与原件核对（`~/wuql_ws/academy_ws/scratch/user/`）

| 页面 / 文件 | 写法 | 原件 | 结果 |
|---|---|---|---|
| 4.20 L131 | `Isaac-Lift-Cube-Franka-IK-Rel-v0` + `--teleop_device keyboard --headless`；环境建好后打出 ERROR，进程随即结束，退出码 0 | `02_optional_checks.sh` 的项 1 命令；`02_item1_teleop.log` L138 WARNING "No teleop device 'keyboard' found…"，L139 ERROR "Failed to create teleop device: module 'omni' has no attribute 'appwindow'"，L140 `rc=0`，两行之间没有别的输出 | 一致 |
| 4.20 L131 的源码行号 L227–L231 | 保留 | 用户运行的 `~/wuql_ws/isaac_sim/IsaacLab` 是 `v2.3.2`，其中的 `teleop_se3_agent.py` 与 tag v2.3.2 的同名文件逐字相同（我拿镜像 diff 过） | 一致 |
| 6.7.1 L118 | ROS 2 Humble、onnxruntime 1.20.1；先 `spec ok`，再报 ONNX 输入 `obs ['batch', 28]`，之后常驻 | 脚本 `source /opt/ros/humble/setup.bash`，命令带 `-p onnx:=… -p spec:=…`；`02_item2_ros_node.log` 两行 INFO 与页面一致；`rc=124` 是 `timeout 20` 杀掉的结果 | 一致；标签见问题 2 |
| 三个脚本第 5 行 | "--usd 默认值 2026-10-20 验证：不带 --usd 在 /tmp 下运行，rc=0" | 命令是 `cd /tmp && … $s.py --headless`，不带 `--usd`；`02_item3_scripts.log` 的 L47、L237、L294 都是 `rc=0`；L37 显示加载的是 `…/accomplish/generated/galbot_fixed_base/configuration/galbot_*.usd`，即默认路径 `generated_asset_dir()/galbot_fixed_base/galbot.usd` 下的层（`check_contacts.py` L61） | 一致 |
| 卡上摘出的数字 | 0.0355 rad（right_arm_joint2）；1.4491 rad（right_arm_joint3）、-4.28 N·m | 日志 L42、L293 | 一致（页面没有新增数字） |
| `Unresolved reference … head_link1/visuals` | 卡上说是预期警告 | 只出现在 Warning 级；没有 Traceback 或 Error 级 | 一致 |

**proj6 副本**：用户跑的是 `scratch/accomplish/proj6/scripts/` 下的副本。三个副本现在与仓库工作区逐字相同（mtime 09:22，晚于用户 09:17–09:20 的运行，是实现方改完后同步的）。运行时的副本"只有第 5 行注释不同"是实现方的说法，我没有办法看到同步前的文件，所以只能确认现在一致。

**其他检查**：
- 第 5 行仍是 CONVENTIONS L156 要求的"验证版本 / 验证日期 / GPU"三行格式。GPU 行保留 RTX 5070，因为原数字是那台卡上测的，符合 D-032 和卡上要求。
- `verified:` 两页都没动；`updated:` 改为 2026-10-20。`index.md` 只改了生成日期。
- 篇幅（汉字数，不含 front matter）：4.20 为 2411，6.7.1 为 1831。
- 构建：快照提交 `4531d39`（`scratch/examine/snap02a`），`-W` 通过（`strict_build_03b.log`）。渲染出的 4.20 有"退出码是 0"一句。

## 问题

| # | 位置 | 问题 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|---|
| 1 | `examples/isaaclab-2.3/6-galbot-project/README.md` L545 | 仍写"带它在 ROS 2 下启动节点：未验证（本站 session 未在 ROS 2 下实跑）"。实现方只 grep 了 `docs/`，没有搜 `examples/` | `grep -rn '未在 ROS 2 下实跑' docs examples` | 改为与 6.7.1 L118 相同的说法："2026-10-20 在本机实测通过（ROS 2 Humble、onnxruntime 1.20.1）" | 低 |
| 2 | 6.7.1 L118"RTX 5090 主机" | 节点用 `CPUExecutionProvider`（`reach_policy_node.py` L40），装的是 CPU 版 `onnxruntime`。这一句没有测量数字，D-032 的硬件标注要求在这里用不上。写"RTX 5090 主机"容易让读者以为节点要用 GPU，而本页表 2 刚说明小网络在 CPU 上最快 | `policy_venv` 只装了 `onnxruntime`，没有 `onnxruntime-gpu`；本页 L86–L91 | 去掉"RTX 5090 主机"，或改为"onnxruntime 1.20.1，CPU 推理" | 低 |

两条都只是改文字，改完我复核文字，再复跑 `-W`。

## 第 2 轮复核

- **问题 1**：README L545 改为"2026-10-20 在本机实测通过（ROS 2 Humble、onnxruntime 1.20.1，CPU 推理）"，与 6.7.1 一致。
- **问题 2**：6.7.1 L118 去掉"RTX 5090 主机"，改为"CPU 推理"（设计已裁断）。
- 在 `docs/` 与 `examples/` 里 grep"未单独验证 / 本站没有单独跑这一步 / 未在 ROS 2 下实跑 / RTX 5090 主机"：0 处。
- 快照 `e7cd10b`，`-W` 通过（`strict_build_03b_r2.log`）。

结论：**通过**。
