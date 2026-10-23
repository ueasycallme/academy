# T-GA-03 Galbot 在 3.0 正式版上：8.5 与 8.10 重训、重评、重转换

状态: 已合并
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

**实现（accomplish，2026-10-23）**：原件都在 `scratch/accomplish/tga03/`（`runs.sh`、各 `*.log` / `*.summary`、`gpu_before_*.txt`、`gpu_watch_*.log`、`NOTE_timing.txt`）。环境：1.5 路线 A（v3.0.0 检出的 `.venv`），`GALBOT_GENERATED_DIR=tga03/gen`；其中 `galbot_fixed_base` 链到 5.1 资产，`galbot_fixed_base_30` 在 Isaac Sim 6.2 上重新转换。
- **示例包**
  - `galbot_academy` 在 GA 上可以导入，注册 `Galbot-Reach` 与 `Galbot-Reach-Play`，导入时不加载 pxr。
  - 正式版删除了 `hydra_task_config`：4 个脚本（check_hold、eval_reach、print_ordering、step_response_30）报 ImportError，改为 `main(*resolve_task_config(args.task, args.agent))`。
  - `convert_galbot_30.py` 仍用 AppLauncher，能跑，带弃用警告（F6），未改。
  - 21 个文件的头注改为 v3.0.0 / 6.2.0 / RTX 5090 / 2026-10-23；README 的环境表与预期值同步更新。
- **转换脚本**：rsl_rl 5.5.1 与 5.4.1 的 `PPO.save` 键名相同（actor_state_dict / critic_state_dict / iter / infos / optimizer_state_dict）。转换后的 2.3 检查点与 3.0 检查点的键名、形状完全相同，评估能加载。
- **资产**
  - 重新转换：mimic 0 个、过滤对 7 对、组合错误 0 个，与 EA 一致。
  - pxr 统计：184 个几何体全带 CollisionAPI，purpose 都是 guide，没有显示用的网格（8.8 坑三照旧成立）。
  - 每侧 5 个 mimic 关节都写了 `newton:mimicJoint`，2 个另写了 `newton:mimicCoef1`，与 EA 资产逐项相同。原 8.5"每侧只保留 2 个跟随关节"的说法不准确，已改正。
  - 原样的 5.1 资产在 GA 的 Newton 上仍报组合错误（`hold_newton_51asset.log`）。
- **训练**（1024 env，1000 次迭代，按 D-032 计时，30 s 一次记录进程名）
  - PhysX s42：rc=0，训练 1391.9 s。开跑时 GPU 上有 awesun_desktop，19:33 前消失，计时按规则作废，检查点只用于评估。
  - PhysX s43：墙上时间 1403 s，训练 1385 s，每次迭代 1.38 s（采集 1.307 s、更新 0.073 s），3332 MiB，RSS 7.0 GB；全程无外部进程。
  - Newton s42：第 1 次启动即成功；墙上时间 372 s，训练 361 s，每次迭代 0.36 s（0.296 / 0.059），5566 MiB，RSS 2.8 GB；全程无外部进程。
- **评估**（每个 3 次；PhysX 上 3 次逐位一致）
  - PhysX s42 → PhysX：5.36 cm / 46.6%
  - PhysX s43 → PhysX：4.78 cm / 51.6%
  - PhysX s42 → Newton：7.70–7.96 cm / 26.6–28.3%
  - Newton s42 → Newton：3.49–3.56 cm / 74.2–74.6%（EA 时 5.67 / 41.4，明显变好，原因未查）
  - Newton s42 → PhysX：5.70 cm / 40.5%
  - 2.3 转换后：原样 51.58 cm / 0%；WXYZ 后在 PhysX 上 2.75 / 81.5%（与 EA 逐位相同）；WXYZ 后在 Newton 上 24.0–25.8 cm / 4.3–5.9%（nan 分别为 1、2、0 个）
- **关节顺序与阶跃响应**：关节顺序 PhysX 10 / Newton 21，与 EA 相同；阶跃上升 0.092 s，超调 0.3 / 0.4%，调节 0.175 / 0.167 s，与 EA 相同；图 1 换成新曲线（1200×630，字号沿用 plot_step_30.py 的 13）。
- **Newton 建场景崩溃**：GA 上 13 次启动（冒烟、顺序、训练、9 次评估、阶跃）0 次崩溃；EA 时 14 次中 7 次。原因未查，8.5 表 3 加了正式版一行。
- **篇幅**（含表）：8.5 3478（≤ 3500，偏紧）、8.10 2628。-W 通过。
- **受影响的其他页（本卡不改，交 T-GA-04 / 05）**
  - 8.3 L76、L119"约一半启动会崩溃（8.5 表 3）"：正式版上 0 / 13，宜改成"EA 时约一半，正式版 13 次 0 次"。
  - 8.8 L82 的 Galbot Kit-less 数字由 T-GA-04 重测。
  - 8.4 表 3 的 81.5% / 2.75 cm 与正式版相同，不用改；8.4 第 5 步已在 T-GA-02 写成"正式版上的数字见 8.10"。
  - 8.6 里没有找到 8.5 / 8.10 的具体数字。


**校验（examine，2026-10-23）**：通过，1 条建议不阻塞，见 `reviews/T-GA-03.md`。
- 在校验方的 GA 环境（envGA）里重评 3 个检查点：PhysX s42 → PhysX 5.36 / 46.6%，Newton s42 → Newton 3.49 / 74.3%，c23w → PhysX 2.75 / 81.5%，都与页面一致。实现方 c23w 那几次评估的日志路径是 `IsaacLab-3.0-GA/.venv`，加上我在独立的 GA 环境里结果相同，可以排除用错环境。
- 关节顺序 10 / 21；Newton 10 次迭代冒烟 rc=0。24 份评估日志、Wilson 区间、两场计时（含 gpu_watch）、13 次 Newton 启动 0 次崩溃，逐项核过。链接全部指向 v3.0.0；快照 83a8317，-W 通过；8.5 3128、8.10 2511。
- 建议：8.5 表 3 注里"每次的日志单独保存"重复了一次。
- 附带：`examples/isaaclab-3.0/8.7-cli/academy_cli_demo.egg-info/` 未跟踪，20:35 新出现，合并时不要 add 进去。
