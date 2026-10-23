# T-GA-04 3.0 正式版的命令行、Kit-less 与 Warp：8.7 / 8.8 / 8.9 重测

状态: 已合并
优先级: P1（T-GA 系列第 4 张）
类型: 实测改写（含计时：实现约 3–4 h，校验约 1.5 h）
依赖: T-GA-01；T-GA-03（8.9 用到升级后的 galbot_academy 包）；D-035、`tasks/T-8-common.md`
产出: `docs/8-frontier/8.7-isaaclab-cli.md`、`8.8-kitless.md`、`8.9-warp-data-path.md`；`examples/isaaclab-3.0/8.7-cli/`、`8.8-kitless/`；`examples/isaaclab-3.0/8.5-galbot-reach/` 下 8.9 专用的 `rewards_warp.py`、`bench_reward_warp.py`、`warp_pitfalls.py`

## 要做什么

1. **8.7**：命令与表格按 GA 逐条重跑。重点是发布页列出的改动：`--cpu` 删除改 `--device cpu`、`--viz newton` 弃用改 `newton_gl`、`args_cli.visualizer` 区分 `None` 与 `[]`、入口点让命令行发现下游任务包（本站 `academy_cli_demo` 示例正好覆盖）、`--headless` 的新语义（F2）。EA 时"外部回调返回 [] 会丢掉 `physics=`"、"`visualizer[rerun,viser]` 被静默跳过"两条在 GA 上复核：已修的改成"EA 时有，GA 已修"一句，没修的保留并更新行号。
2. **8.8**：Kit-less 能 / 不能的清单按 GA 核对；路线 C 环境用 T-GA-01 的；Kit 与 Kit-less 的显存、内存、启动时间对照与"装了 Isaac Sim 但不启动 Kit 也慢 7–10 ms / 迭代"一条，在 GA 上**计时**重测并替换；OVRTX 一节重测。8.8 原有"原因未查"的那条，GA 上若仍存在保持原表述，消失了就照实写。
3. **8.9**：ProxyArray 拷贝语义按 GA 核对（发布页称资产与传感器数据统一用 `ProxyArray`，有 `.torch` 与 `.warp`）；奖励项 torch 与 Warp 两版的逐步比对、耗时对照在 GA 上**计时**重测并替换；Warp 1.17.0 的 `launch_array_access_mode` 默认值按 F8 写。
4. 页顶提示框、`verified:`、permalink 同 T-GA-02 的规则。

## GPU 与计时

8.8 与 8.9 的耗时数字属计时测量：开测前在群里报"开始计时"，得到校验方确认后再跑，期间双方都不做构建、不开 Chrome（D-032）。

## 校验（examine）

计时数字至少复现 8.8 的 Kit / Kit-less 一组与 8.9 的奖励项耗时一组（同样独占），差别超过 15% 时双方各再跑一次；8.7 的命令抽查三条；-W 构建；篇幅。

## 验收标准

三页的命令与数字全部来自 GA + RTX 5090；EA 时期的两个已知问题在 GA 上有明确结论；校验方复现两组计时。

## 附记

（实现/校验 session 写）

**实现（accomplish，2026-10-23）**：原件都在 `scratch/accomplish/tga04/`（`cli/`、`t88/`、`t88b/`、`t89/`、`help_*.txt`、`ep_*.log`）。环境用 T-GA-01 的路线 A / C；路线 C 另装了 `ov[ovrtx]`、`visualizer[rerun],visualizer[viser]`，并 `uv pip install -e` 了 8.7-cli（12 GB）。
- **8.7**（命令都在 GA 上跑过，非计时；`cli87.sh`）
  - `isaaclab --help` 多了 `list_envs`、`demo`、`example`；`--rl_library` 新增 torchrl。
  - Cartpole 4 条命令都通过：默认 `newton_mjwarp`；`--frontend warp` 用 `InteractiveSceneWarp`；不写 `--rl_library` 也能跑（help 的用法行写成必填，与实际行为不符）。
  - 外部回调返回 None / [] 两条按 EA 时的结论复核：返回 [] 仍会吞掉 `physics=`，没修。
  - 入口点组由"未验证"改为实测：`uv pip install -e` 进路线 C 后，`list_envs --keyword Academy` 能列出，`train` 能跑。
  - `--viz newton` 仍可用，被换成 `newton_gl`；`DeprecationWarning` 默认不显示（sim_launcher L196–L203）。
  - `--headless`、`--cpu` 返回 rc=2（引 T-GA-01 F2 / F3）。
  - `visualizer[rerun,viser]` 仍被静默跳过（F1），写进坑五。
  - 脚注全部改指 v3.0.0。
- **8.8 表 2 / 表 3**（独占计时；开跑前和每 30 s 记录 GPU 进程，全程只有被测进程；`time88.sh`，2026-10-23 20:40–20:48）
  - 表 2：A + PhysX 111.5 / 109.2 ms；A + Newton 77.7 / 76.7 ms；C + Newton 68.4 / 68.6 ms。"只装不用慢 7–10 ms / 迭代"在 GA 上仍在（约 9 ms），原因仍未查，保持原表述。
  - 表 3：OVRTX 5.01 / 4.96 ms，Newton 渲染器 1.08 ms。装好 OVRTX 后第一次运行约 5 min，RSS 峰值 13.9 GB。
- **8.8 其余**
  - Cartpole 200 次迭代回报 4.95；viser / rerun 回放打印的地址与 EA 相同。
  - Galbot Kit-less 200 次迭代：81 s（训练 71.9 s），位置误差 4.20 cm，第一次启动就成功。这一组与 8.9 一起计时，无外部进程。
  - 表 1 按 GA 核对：PhysX 一行改为实测；Newton GL 一行改为实测；Isaac RTX 在 GA 文档里标为 legacy。
  - 图 1–3 仍是 EA 时的截图，页首已注明。
- **8.9**
  - ProxyArray 的源码与 how-to 文档在 GA 里没有改动，行号不变。
  - F8：warp 1.17.0 默认仍是 RELAXED；context.py L10345–L10348，已核对 GitHub v1.17.0。
  - STRICT 模式在 Warp 1.17 上本站重测（`strict_test.py`），报错文字变了，页面已更新，同时去掉了"校验方实测"字样。
  - `bench_reward_warp.py` 在 GA 上报 "body_names 与 body_ids 不一致"：奖励管理器已 resolve 并 finalize 了 asset_cfg，脚本再 resolve 一次就出错。已删掉那一行，加了注释。
  - 表 3：
    - 1024 一行（20:51，无外部进程）：torch 0.128 / 0.134 ms，Warp 0.049 / 0.049 ms，env.step 10.0 ms。
    - 4096 一行第一次测量（20:58）中途 awesun_desktop 出现，按规则作废；21:02 重测时 awesun 全程常驻：torch 0.126 / 0.136 ms，Warp 0.048 / 0.049 ms，env.step 23.0 ms。表注按行写明两行条件不同。
  - 坑四：空缓存（新建目录，未动 `~/.cache/warp`）第一次调用 36.8 ms（作废那次为 35.6 ms），缓存目录 52 MB。按校验方提醒写明计时口径：模块在这次调用里编译（目录时间戳为证）；`warp_pitfalls.py` 单独运行时 Warp 报告编译 313 ms。两者的差别推断是编译器的一次性初始化。
- **其他**
  - `docs/conf.py`：`_pack_examples` 跳过 `*.egg-info` 目录（设计方要求，一行）。
  - `examples/isaaclab-3.0/8.7-cli/academy_cli_demo.egg-info/` 已删除；路线 C 里的 editable 安装保留（元数据在 site-packages）。重新 `pip install -e` 会再生成这个目录。
  - 示例头注改为 v3.0.0；8.7 / 8.8 / 8.5 的 README 同步更新。
- **篇幅**（含表）：8.7 3162、8.8 2294、8.9 2342。-W 通过。
- **给 T-GA-05**：8.5 L104、L122 仍有"校验方"字样（T-GA-03 已合并，本卡不改）。


**校验（examine，2026-10-24，第 1 轮）**：退回，1 条低级问题，同轮可修，见 `reviews/T-GA-04.md`。
- 独占计时复现（全程有 awesun 常驻，没有出现或消失）：8.8 三组 111.7 / 78.4 / 71.2 ms；8.9 的 1024 env 一组 torch 0.1277、Warp 0.0485、env.step 10.26 ms。都与页面相差 < 15%。
- 8.7 抽查三条命令都是 rc=0；STRICT / CHECKED / RELAXED 复现；链接、原件、`bench_reward_warp.py` 改动都核过。快照 c57f15b，-W 通过；篇幅 2792 / 2244 / 2168。
- 问题 1（低）：8.9 坑四写"奖励模块就在这次调用里编译"，但缓存时间戳只能说明是在这次运行中编译的。另外有不少 MJWarp 内核编译得比它晚，所以"此前 Newton 已编译过自己的内核"只对一部分成立。改为推断的写法即可。

**实现第 2 轮（accomplish，10-24）**：8.9 坑四 L139 按校验意见改写："在这次运行中"编译有时间戳为证（21:03:22，进程 21:03:10 起跑），"就在这次调用里"标推断；"此前 Newton 已编译过"改为"已编译过部分 Newton 内核（还有一些 MJWarp 内核在它之后才编译）"。-W 通过。

**校验（examine，2026-10-24，第 2 轮）**：通过。8.9 L139 已改为推断的写法，与缓存时间戳一致；快照 bf86968，-W 通过。
