# AUDIT-01 全站质量巡检报告

校验 session：isaac-academy-examine，2026-10-09
任务卡：`tasks/T-AUDIT-01.md`
基准：HEAD `386aa36`（T-9.5 合并后）。巡检在仓库的干净克隆里进行，HTML 也在克隆里构建，不读工作区；工作区里正在写的 4.8 不在范围内。
重跑：`reviews/scripts/audit-all.sh [输出目录]`，约 4 分钟，打印的汇总与本报告第 1 节相同。

## 1. 汇总

| # | 检查 | 范围 | 结果 | 阻塞 | 一般 | 建议 |
|---|---|---|---|---|---|---|
| 1 | 外链存活 | 唯一 URL 736 个（引用 999 处） | 735 个可达，其中 476 个 GitHub permalink 用本地克隆核对了 tag、路径与行号；1 个 403（抓取被拒）；9 个重定向 | 0 | 0 | 2 |
| 2 | 站内锚点 | 正文里的站内链接 5518 个，带 `#` 的 3901 个 | 目标文件与锚点全部存在 | 0 | 0 | 0 |
| 3 | 术语（D-018） | 术语表 140 条，其中"中文附英文"类 85 条；正式页 82 页；页 × 词条共出现 913 次 | 首次出现就附英文的只有 40 次（4%）；按设计 session 的口径，在"首次详细讲解页"缺对照的有 49 处 | 0 | 1（49 处） | 2 |
| 4 | 图字号（D-025） | Mermaid 图 25 张 × 1440、2560 两档 = 50 次测量；位图 8 张 | 50 次全部 ≥ 12 px，最小为 3.1 在 1440 下的 12.0 px；位图里的文字按出图参数推算为 13.9 px 以上，另 3 张照片类图片里没有需要阅读的文字 | 0 | 0 | 1 |
| 5 | 版本说明 | 含"版本说明"一节的正式页 75 页；8.6 表 2 | 69 页有固定句；1.5 缺固定句；4 个附录页按 T-8.6b 的范围本来就没有加；8.6 表 2 逐页列出的 32 页，日期与各页 `sources_checked` 全部一致；"其余 40 页"的数目与"未核对"字样都对 | 0 | 1 | 1 |
| 6 | 占位页 | 占位页 39 个，"现在可以读什么"里的链接 201 个 | 全部指向正式页；链接文字与目标页标题一致；同目录的正式页都已列出 | 0 | 0 | 1 |
| 7 | examples 头注 | git 中的 `examples/**/*.py` 共 109 个 | 42 个齐全；其余 67 个中，一般 6 个，建议 61 个（模板生成 24 个、GPU 写在 README 里 25 个、包声明与纯工具 12 个） | 0 | 6 | 3 |

没有阻塞项。下面按"一般"和"建议"分级列出；每条写明页面、位置、问题与建议。设计 session 拆微任务时可以直接按条目编号引用，例如 G-1、S-3。

## 2. 一般

**G-1　术语：首次详细讲解页的首次出现没有附英文（D-018），共 49 处，涉及 29 页**

- **口径**：按设计 session 2026-10-09 的倾向统计。只看术语表"首次详细讲解"一列指向的那一页，检查该术语在这一页第一次出现时，是否写成"中文（English）"。
- **数正文时剔除的部分**：frontmatter、标题行、"学习目标"框和"前置知识"框、代码、脚注定义。
- **不计入的情况**：
  - "扩展"：D-018 允许它单独使用；
  - 术语后隔了至多 4 个汉字才接括号的，算已附，如"执行器模型（actuator）"；
  - 括号里写的是术语表给出的缩写，也算已附，如"工具中心点（TCP）"。
- **表格末列的含义**："页内后文有对照"指同页后面某处写过对照，只是第一次出现时没写，改法是把对照挪到第一次出现处。"全页无对照"指整页都没写过。
- **建议**：机械微任务，在所列行号处补上"（English）"。英文的写法与大小写按术语表；一般概念用小写，例如"刚体（rigid body）"。

| 页面 | 行 | 术语（应附的英文） | 现状 |
|---|---|---|---|
| 2-usd-kit/2.2-usd-concepts.md | L53 | 属性（Attribute） | 全页无对照 |
| 2-usd-kit/2.3-layers-composition.md | L40 | 合成弧（Composition Arc） | 全页无对照 |
| 2-usd-kit/2.5-usd-python.md | L119 | 压平（Flatten） | 全页无对照 |
| 2-usd-kit/2.7-extensions.md | L68 | 扩展搜索路径（Extension Folder） | 全页无对照 |
| 3-isaacsim/3.2-simulation-app.md | L29 | standalone 脚本（Standalone Python） | 全页无对照 |
| 3-isaacsim/3.3-rigid-collision.md | L29 | 刚体（Rigid Body） | 全页无对照 |
| 3-isaacsim/3.3-rigid-collision.md | L61 | 碰撞近似（Collision Approximation） | 全页无对照 |
| 3-isaacsim/3.3-rigid-collision.md | L72 | 物理材质（Physics Material） | 全页无对照 |
| 3-isaacsim/3.4-articulation.md | L27 | 关节（Joint） | 页内后文有对照 |
| 3-isaacsim/3.4-articulation.md | L51 | 驱动（Joint Drive） | 全页无对照 |
| 3-isaacsim/3.5-urdf-mjcf-import.md | L48 | mimic 关节（Mimic Joint） | 全页无对照 |
| 4-isaaclab/4.1-why-isaac-lab.md | L31 | 环境（Environment） | 全页无对照 |
| 4-isaaclab/4.10-observation-action.md | L49 | 观测组（Observation Group） | 全页无对照 |
| 4-isaaclab/4.11-reward-termination-curriculum.md | L25 | 奖励（Reward） | 页内后文有对照 |
| 4-isaaclab/4.11-reward-termination-curriculum.md | L25 | 终止（Termination） | 全页无对照 |
| 4-isaaclab/4.11-reward-termination-curriculum.md | L25 | 课程（Curriculum） | 全页无对照 |
| 4-isaaclab/4.13-command-manager.md | L25 | 指令（Command） | 页内后文有对照 |
| 4-isaaclab/4.14-direct-env.md | L25 | Direct 环境（DirectRLEnv） | 全页无对照 |
| 4-isaaclab/4.5-interactive-scene.md | L36 | 环境原点（env origin） | 全页无对照 |
| 4-isaaclab/4.5-interactive-scene.md | L81 | 碰撞过滤（Collision Filtering） | 全页无对照 |
| 4-isaaclab/4.6-assets.md | L25 | 资产（Asset） | 页内后文有对照 |
| 4-isaaclab/4.7-actuators.md | L41 | 执行器（Actuator） | 页内后文有对照 |
| 4-isaaclab/4.9-manager-based-env.md | L184 | Manager-based 环境（ManagerBasedRLEnv） | 全页无对照 |
| 5-rl/5.1-mdp.md | L63 | 状态（State） | 页内后文有对照 |
| 5-rl/5.2-policy-value.md | L27 | 策略（Policy） | 页内后文有对照 |
| 5-rl/5.2-policy-value.md | L44 | 价值（Value） | 页内后文有对照 |
| 5-rl/5.2-policy-value.md | L64 | 观测归一化（Observation Normalization） | 全页无对照 |
| 5-rl/5.3-ppo.md | L85 | KL 散度（KL Divergence） | 全页无对照 |
| 5-rl/5.3-ppo.md | L41 | 小批量（Mini-batch） | 全页无对照 |
| 5-rl/5.3-ppo.md | L29 | 迭代（Iteration） | 全页无对照 |
| 5-rl/5.3-ppo.md | L89 | 熵（Entropy） | 全页无对照 |
| 5-rl/5.4-parallel-envs.md | L54 | 批量（Batch） | 全页无对照 |
| 5-rl/5.4-parallel-envs.md | L46 | 吞吐（Throughput） | 全页无对照 |
| 5-rl/5.4-parallel-envs.md | L54 | 墙上时间（Wall-clock Time） | 全页无对照 |
| 5-rl/5.5-reward-design.md | L62 | 核函数（Kernel） | 全页无对照 |
| 5-rl/5.6-observation-design.md | L119 | 历史帧（Observation History） | 全页无对照 |
| 5-rl/5.7-il-vs-rl.md | L27 | 模仿学习（Imitation Learning） | 页内后文有对照 |
| 6-galbot/1-asset/6.1.1-galbot-repo.md | L53 | 全向轮（Omni Wheel） | 全页无对照 |
| 6-galbot/1-asset/6.1.1-galbot-repo.md | L53 | 被动滚子（Passive Roller） | 页内后文有对照 |
| 6-galbot/1-asset/6.1.2-import-urdf.md | L95 | 固有频率（Natural Frequency） | 全页无对照 |
| 6-galbot/1-asset/6.1.2-import-urdf.md | L95 | 阻尼比（Damping Ratio） | 全页无对照 |
| 6-galbot/1-asset/6.1.4-collision-mass-inertia.md | L32 | 过滤对（Filtered Pair）；首次出现后的括号是“（只依赖 pxr）”，不是英文对照 | 全页无对照 |
| 6-galbot/1-asset/6.1.4-collision-mass-inertia.md | L175 | 初始穿透（Initial Penetration） | 全页无对照 |
| 6-galbot/1-asset/6.1.5-joint-drive-tuning.md | L29 | 阶跃响应（Step Response） | 页内后文有对照 |
| 6-galbot/1-asset/6.1.5-joint-drive-tuning.md | L75 | 上升时间（Rise Time） | 页内后文有对照 |
| 6-galbot/1-asset/6.1.5-joint-drive-tuning.md | L75 | 超调（Overshoot） | 页内后文有对照 |
| 6-galbot/1-asset/6.1.5-joint-drive-tuning.md | L75 | 调节时间（Settling Time） | 页内后文有对照 |
| 6-galbot/1-asset/6.1.5-joint-drive-tuning.md | L75 | 稳态误差（Steady-state Error） | 页内后文有对照 |
| 8-frontier/8.1-what-changed.md | L64 | 物理后端（Backend） | 全页无对照 |

说明：
- **Manager-based 环境、Direct 环境**：术语表的英文列写的是类名（ManagerBasedRLEnv、DirectRLEnv），中文名本身已经带英文。这两处由设计 session 决定补还是豁免，我倾向豁免。
- **全站情况（只作参考，不建议逐处改）**：在所有页面上，第一次出现就附英文的只占 4%（913 次中有 40 次）。逐页执行 D-018 原文要改约 870 处，读者收益小，所以支持设计 session 收窄口径。如果采纳，CONVENTIONS 第 3 节与 0.8"中英使用规则"要同步改写，否则规则与实践不符的情况还在。

**G-2　1.5 的版本说明缺 T-8.6b 固定句**

- **位置**：`1-env/1.5-install-61-30.md` 的"## 版本说明"。
- **问题**：1.5 是 T-8.6b 之后新写的页面，按 CONVENTIONS 第 2 节"新页照写"，应有固定句。
- **自我披露**：我在 T-1.5 的校验中漏查了这一项。T-9.5 第 1 轮查出了同样的问题，那张卡已经改了。今后新页的校验清单里会加上这一项：本报告的 `audit-version.py` 可以直接跑。
- **建议**：在节末加"3.0 的差异以 [8.6 版本追踪](../8-frontier/8.6-version-tracking.md) 为准，本页最后核对的版本见该页核对状态表。"

**G-3　examples：6 个文件的头注缺项，不在下文的豁免类别里**

| 文件 | 缺 |
|---|---|
| `2.2-usd-concepts/inspect_usd.py` | GPU |
| `2.4-physics-schema/list_physics_schemas.py` | GPU |
| `2.5-usd-python/check_asset.py` | GPU |
| `2.5-usd-python/edit_usd.py` | GPU |
| `2.7-extensions/enable_hello.py` | GPU |
| `6-galbot-project/.../tasks/manager_based/reach/__init__.py` | 验证版本、日期、GPU（只有版权行和 docstring） |

前 5 个都会启动 Isaac Sim（或可选启动），所在目录的 README 也没有写 GPU。建议按 CONVENTIONS 第 5 节补一行 `# GPU：…`；如果当初没有记录，就写实际验证时用的 RTX 5070。reach 的 `__init__.py` 补三行头注。

## 3. 建议

**S-1　外链：1 个 403，经判断是抓取被拒**

- **链接**：`https://docs.omniverse.nvidia.com/kit/docs/usdrt/latest/docs/usd_fabric_usdrt.html`，被 0.8 L232、4.4 L165 / L179 引用。
- **判断依据**：curl 和 headless Chrome 拿到的都是 Akamai 的"Access Denied"。连 `usdrt/latest/index.html` 也一样，而同一域名下其他 9 个链接都返回 200。所以判断是这一路径对自动化抓取做了拦截，按 CONVENTIONS 第 4 节不判为失效。该页内容此前已经用 pip 包里随附的副本核对过（见 visual-check-method 的记录）。
- **建议**：请用户用浏览器打开一次，确认页面还在。

**S-2　外链：9 个重定向（都可达）**

| 原链接 | 跳到 | 建议 |
|---|---|---|
| `isaac.kiloong.com/zh/...*.html`（4 处） | 去掉 `.html` 的同名地址 | 可以统一去掉 `.html`；不改也能用 |
| `isaac.kiloong.com`、`isaac.kiloong.com/` | `/zh/` | 不用改 |
| `developer.nvidia.com/cosmos` | `www.nvidia.com/en-us/ai/cosmos/` | 可以换成新地址 |
| `github.com/isaac-sim/IsaacLab.git` | 仓库页 | 这是 `git clone` 用的地址，不用改 |
| `pypi.nvidia.com` | `pypi.nvidia.cn` | 按访问地区跳转（本机在国内），不用改。1.4 如果需要，可以提一句"国内会被跳到 .cn 镜像" |

**S-3　术语：Prim / Term 写成小写 3 处**

- `0-map/0.5-sim-lab-boundary.md` L73："直接读写 prim"；
- 同页 L99："prim 封装"；
- `6-galbot/2-scene/6.2.1-workbench-scene.md` L105："命令项（command term）"。

前两处建议改为 Prim。第三处是括号里的英文对照，可以写成 command Term，也可以不改。

**S-4　术语："之后单独用英文"的 59 组只作参考**

`audit-terms.py` 的 ENALONE 类我抽了 7 处人工看，都不是问题：
- Manager 名，如表格里的"Reward"一行；
- 官方文档页面的标题（链接文字）；
- 英文在前的对照写法，如 2.2"Attribute（属性）"；
- D-018 允许二选一的 wrapper。

结论：这一类噪声太大，不拆任务。脚本保留它，供以后人工抽查。

**S-5　图字号：3.1 图 1 在 1440 下正好 12.0 px**

在线上，但没有余量（缩放比 0.748）。以后改这张图时，如果增加文字或节点会跌破 12 px，到时按 D-025 合并节点即可。

位图的结论：
- **曲线图**：5.6、6.1.5、6.5.1、6.5.2 共 6 张，由 `plot_*.py` 以 13 pt / 150 dpi 输出，图例 12 pt。页面上的最小缩放为 0.557，文字约 15.1 px，图例约 13.9 px，均 ≥ 12 px。
- **照片类**：6.1.1、6.1.4 的渲染图和 6.6.1 的关键帧，图里除机身 logo 外没有需要阅读的文字，D-025 不适用。

**S-6　CONVENTIONS 第 2 节关于占位页的写法过时**

- **现状**：CONVENTIONS 写"占位页：frontmatter 加 `orphan: true` 且不进 toctree"。实际上 39 个占位页都没有 orphan，而且都在 toctree 里，目录用"（待写）"标出。
- **依据**：T-SITE-12 附记"占位页本来都没有 orphan，slug 与 toctree 都没动"。
- **建议**：设计 session 把 CONVENTIONS 那一行改成现行做法。

**S-7　附录 A.1、A.2、A.3、A.5 的版本说明没有固定句**

T-8.6b 按范围排除了附录。但 A.1、A.2、A.3 写了 3.0 内容，并且已列入 8.6 表 2，加上固定句与正文页一致。A.5 是更新日志，可以不加。

**S-8　examples：61 个文件按类别豁免或统一处理**

| 类别 | 数量 | 建议 |
|---|---|---|
| 模板生成的文件，头注是 Isaac Lab 版权行（4.18 `academy_demo/**`、6 部分的 `scripts/rsl_rl/*`、`list_envs.py`、`zero_agent.py`、`random_agent.py` 等） | 24 | CONVENTIONS 第 5 节加一句豁免："由 Isaac Lab 模板生成器生成、保留原版权头的文件，验证信息写在示例目录的 README"。这些目录的 README 已经写明来自模板 |
| 只缺 GPU，所在示例目录的 README 写了 GPU（6 部分项目的大部分源文件，以及 2.3、2.7 的扩展等） | 25 | 同样在 CONVENTIONS 里允许"GPU 可只写在示例目录 README" |
| 包声明 `__init__.py`（≤ 15 行），以及不依赖 Isaac 与 torch 的纯工具（画图、解析日志、比较 USD） | 12 | 豁免 |

## 4. 方法与局限

| 检查 | 脚本 | 做法 | 局限 |
|---|---|---|---|
| 1 外链 | `audit-links.py` | GET 并跟随重定向；`--mirror` 指定的仓库，blob / tree 链接用本地克隆核对 tag、路径与 `#L` 行号（比抓网页更严）；其余 github.com 链接限 2 个并发，429/503 时退避重试 | 不检查外链的 `#锚点`；GitHub 在不给 mirror 时可能报"限流未核" |
| 2 锚点 | `audit-anchors.py` | 在构建好的 HTML 上，逐个检查正文里的站内链接，目标文件与 `#id` 都要存在 | 只查正文 `.bd-article`，导航由主题生成，不查 |
| 3 术语 | `audit-terms.py` | 去掉代码、标题、学习目标框、前置知识框和脚注后，找每个术语第一次出现的位置，看后面是否紧跟英文括号；遇到更长术语的一部分（如"关节"在"mimic 关节"里）不算出现 | 启发式。FIRST 类经人工抽查准确（3.3 全页没有"刚体（"，4.7 也没有"执行器（"）；ENALONE 类噪声大（见 S-4） |
| 4 字号 | `audit-fonts.py` | headless Chrome 打开同源测试页，用宽度为 1440 或 2560 的 iframe 加载各页，等 Mermaid 渲染完，量 computed font-size × 缩放比（与 `diagram-fontprobe.js` 同一口径） | 连续加载多页时，0.2 与 8.1 的第 2 张图会停在未完成的临时 svg 上；单独加载正常，原因未查。脚本对这类页会单独另开一个 Chrome 重量，结果标"单独重量"。位图里的字号量不到，只列缩放比，由人工判断 |
| 5 版本 | `audit-version.py` | 节内找固定句，并按目录层级核对相对链接；解析 8.6 表 2 各行列出的页码与日期，与各页 frontmatter 比对 | 反向对照已做：在克隆里把两页的 `sources_checked` 改成假日期，两处都报出，包括 1.7 的单独日期 |
| 6 占位页 | `audit-placeholders.py` | 只读 git，不调用生成器；检查链接目标是否为正式页、链接文字与目标页标题是否一致、同目录的正式页是否都已列出 | "同部分"按目录判断，与生成器的分组口径（第 6 部分按 6.x 小节，其余按部分）在现有页面上结果相同 |
| 7 头注 | `audit-examples.py` | 读第一行代码之前的注释与 docstring，查验证版本、日期、GPU，或"未验证"；按模板文件、GPU 写在 README、包声明分类 | 只查 git 中已跟踪的文件；未提交的 lift 文件等合并后再查 |

其他：
- 锚点检查的负对照：在 HTML 副本里改坏一个锚点和一个文件链接，都报出了。外链检查的本地核对也做了负对照：行号越界、路径不存在、tag 不存在三种情况都能报出。
- 本次巡检没有修改 `docs/` 与 `examples/`：生成器只用 `--check` 跑，构建都在 scratchpad 的克隆里进行。
- **更正（2026-10-09，校验 T-4.8 / T-1.8 时发现）**：`audit-version.py` 初版判断表 2 在哪里结束，看的是整行里有没有"其余"二字。而 0.1… 那一行的日期格里也有"其余为 2026-09-30"，脚本就在那一行停住了，"其余 40 页"一行实际没有被核对。已改为按第一格判断，并在找不到这一行时报错。修正后在同一个 HEAD（386aa36）上重跑：其余 40 页 = 实际 40 页，第 1 节的结论不变。负对照：把行内的数字改成 39，能报出来。
