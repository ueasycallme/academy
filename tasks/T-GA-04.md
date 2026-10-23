# T-GA-04 3.0 正式版的命令行、Kit-less 与 Warp：8.7 / 8.8 / 8.9 重测

状态: 待实现
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
