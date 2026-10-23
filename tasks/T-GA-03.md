# T-GA-03 Galbot 在 3.0 正式版上：8.5 与 8.10 重训、重评、重转换

状态: 待实现
优先级: P1（T-GA 系列第 3 张；8.9 的脚本依赖本卡升级后的 galbot_academy 包，所以排在 T-GA-04 之前）
类型: 实测改写（GPU 较重：实现约 4–5 h，其中训练与评估约 2.5 h；校验约 1.5 h）
依赖: T-GA-01（通过后开工；可与 T-GA-02 的校验并行）、D-035、`tasks/T-8-common.md`
产出: `docs/8-frontier/8.5-galbot-reach-30.md`、`docs/8-frontier/8.10-physx-newton-transfer.md`、`examples/isaaclab-3.0/8.5-galbot-reach/`（除 8.9 专用的 `rewards_warp.py`、`bench_reward_warp.py`、`warp_pitfalls.py` 外）

## 要做什么

1. **示例包升级**：`galbot_academy` 与各脚本在 GA 上跑通。`AppLauncher` 若仍可用（F6），先保持不动并记一句；若不可用或行为变了，改用 `launch_simulation`，在 8.5 说明原因。资产转换 `convert_galbot_30.py` 在 Isaac Sim 6.2 上重跑一次。
2. **8.5 重训**：与 EA 时同预算、同种子，在 GA 上分别用 PhysX 与 Newton 各训一次 Galbot reach；评估按本站口径（同检查点同种子重复 ≥ 3 次取范围，见校验方经验）。表格数字全部替换为 GA + RTX 5090；若 GA 结果与 EA 差别大（例如某后端明显变好或变差），在表注写一句"EA 时为 …"并说明本站没有查原因或查到的原因。
3. **8.10 重做**：
   - 两后端的关节顺序（`print_ordering.py`）在 GA 上是否仍不同。
   - 跨后端评估矩阵（PhysX 训 → Newton 评，反之亦然）在 GA 上重测。
   - 2.3 检查点的两步转换：GA 的 RSL-RL 是 5.5.1，`convert_ckpt_23_to_30.py` 是否仍适用；转换后在 GA PhysX 上评估，替换 81.5% / 2.75 cm 与"原样 0%"两组数字。
   - 阶跃响应对照（`step_response_30.py`、`plot_step_30.py`）重跑，图换新。
   - 8.10 里"Galbot 资产副本只有碰撞、可视化器里看不到外观网格"一条在 GA 上复核。
4. 8.4 第 5 步、8.6 L81 等处引用了 8.10 的数字：数字变了就在附记列出受影响的句子，由 T-GA-05 统一改，本卡不改别的页。
5. 页顶提示框、`verified:`、permalink 同 T-GA-02 的规则。

## GPU

训练与评估长时间占 GPU，每次开跑前在群里报一句，按 `implementer-gpu-handoff` 规则逐次问校验方，不连续串跑；不报墙上时间的训练可与校验方并行各一个 Kit。阶跃响应若报耗时则独占。

## 校验（examine）

用实现方的检查点各重评一次（PhysX、Newton、2.3 转换后），确认范围一致；抽查关节顺序输出；示例包在自己的 GA 环境里 `pip install -e` 后能导入并跑 10 次迭代；-W 构建；篇幅。

## 验收标准

8.5、8.10 的数字全部来自 GA + RTX 5090；转换脚本在 RSL-RL 5.5.1 下可用或已改好；页面不再以 EA 为依据（历史对照句除外）；校验方复现三组评估。

## 附记

（实现/校验 session 写）
