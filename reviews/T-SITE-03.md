# T-SITE-03 校验报告

- 校验日期：2026-09-30
- 校验对象：`site-sphinx/`（Sphinx 8.1.3 / myst-parser 4.0.1 / pydata-sphinx-theme 0.16.1 / sphinxcontrib-mermaid 2.1.1）
- 结论：**通过**（1 条一般、3 条建议；"像不像官方站"由用户判断，本报告不评）

## 设计 session 指定的 5 个重点

### ① 许可：未使用 nvidia-sphinx-theme 及 NVIDIA logo/字体/图标 — 通过
- `site-sphinx/.venv` 中没有 `nvidia-sphinx-theme`（`pip freeze` 核对）。该包在 PyPI 上 license 为 "NVIDIA LICENSE AGREEMENT"、分类 `Other/Proprietary License`，与卡片所述一致。
- 构建产物中的字体文件只有 pydata 自带的 FontAwesome（`_static/vendor/fontawesome/webfonts/`），没有 NVIDIA Sans / RobotoMono，也没有任何 logo 图片。
- 构建产物中出现 "NVIDIA" 的地方只有：页脚第三方声明、正文内容，以及 `academy.css` 里记录色值来源的注释。
- 站名为纯文字 "Isaac Academy"。

### ② 无境外请求 — 通过
- 校验方自行全量重建（`-E -a -W --keep-going`，输出到 scratch），用 headless Chrome、除 127.0.0.1 外所有域名都解析失败的条件下打开 0.2 页；`--log-net-log` 中，除 Chrome 自身后台服务外，页面请求的主机只有 `127.0.0.1`。
- 在实现方的 8767 预览上，Performance API 统计的外部主机数为 0。

### ③ 中文搜索 — 可用，但有一个显著限制（见问题 1）
| 查询 | 结果数 | |
|---|---|---|
| 版本绑定 | 1 | ✓ |
| 脚注 | 2 | ✓ |
| 导入 | 2 | ✓ |
| 路径 | 1 | ✓ |
| 分层 | 2 | ✓ |
| Kit | 1 | ✓ |
| 量子纠缠 | 0 | 对照组 ✓ |
| **导入路径** | **0** | ✗：两个词单独都能搜到 |
| **弃用警告** | **0** | ✗ |
| **旧导入路径** | **0** | ✗ |

原因（已查源码）：索引端 `sphinx/search/zh.py` 用 `jieba.cut_for_search` 分词；但查询端 `searchtools.js` 的默认 `splitQuery` 只按非字母字符切分，连续的中文短语被当成一个词，而索引里没有这个词。单个词能搜到，连写的多词短语搜不到。任务卡的字面要求（"能搜到中文词"）已满足。

### ④ Mermaid 深浅色（截图目检）— 通过
- 屏蔽外网截图：`reviews/img/T-SITE-03-0.2-dark.png`、`reviews/img/T-SITE-03-0.2-light.png`。图 1 方向正确（GPU 在底）；深色与浅色下节点、文字、橙色落点框都清晰。
- 实时切换：在 8767 页面上把 `data-theme` 按 light → dark → light 切换，两张图随之重渲染，节点填充在 `rgb(238,238,238)` 与 `rgb(31,32,32)` 之间切换；尺寸始终为 371×549、492×558，不变。
- 小瑕疵：深色下"适配层"边标签带灰底块（Mermaid dark 主题的 edgeLabel 背景），不影响阅读。

### ⑤ MIGRATION-NOTES.md 能否指导机械迁移 — 通过（实测）
校验方挑了一页**未迁移过**的页面 0.6（含 Mermaid 时序图与 `%%{init}%%`、4 个 warning、abstract/info、脚注、表格、11 个站内链接），完全按 MIGRATION-NOTES 操作：
1. `tools/md2myst.py docs/0-map/0.6-one-step.md …`（脚本步骤）
2. 为 5 个缺失的链接目标复制占位页并加 `orphan: true`，在 `index.md` 的 toctree 中加一行（文档所列的"手工"步骤）
3. `sphinx-build -E -a -W --keep-going`：**零警告**

结论：对照表覆盖了现有页面用到的全部语法，脚本输出可以直接构建；手工步骤（toctree、orphan、占位页）写得清楚，工作量可预期。

### 其他
- `sphinx-build -E -a -W --keep-going`：零警告（校验方复现）。
- 没有改动 `docs/` 与 `mkdocs.yml`（任务卡"不做"项）。

## 问题清单
| # | 位置 | 问题 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|---|
| 1 | 中文搜索 | 连写的中文多词查询（如"导入路径""弃用警告"）返回 0 条结果，而读者输入中文时一般不会加空格 | 上表；`searchtools.js` L172–176 的 `splitQuery` 只按非字母字符切分 | 如果决定切换到 Sphinx，需要单独开任务：在 `_static` 中覆盖全局 `splitQuery`，对 CJK 片段按搜索索引的词表做最长匹配切分（索引里的 `terms` 已在前端可用），再验证上表各查询。**本轮没有对比 MkDocs 版在同样查询下的表现**；如需作为切换决策依据，可以补测 | 一般（不阻塞原型，但会影响"是否切换"的决策） |
| 2 | 配色 | 主色直接采用官方站的品牌绿 `#76b900`，整体版式又刻意贴近官方站，读者可能误以为本站是 NVIDIA 官方或附属站点。页脚有"与 NVIDIA 无隶属关系"的声明，可以缓解 | 任务卡允许"取官方站的绿色系"；这里只指出风险，不做法律判断 | 请用户在决定切换时一并考虑：保留相同色值，还是改用相近但不同的绿色（例如只调一点色相），并把首页或页头的非官方声明放得更显眼 | 建议 |
| 3 | `site-sphinx/` 占位页 | 9 个占位页是从 `docs/` 复制过来的，两边以后会各自漂移 | — | 原型阶段可接受；如果决定切换，一次性迁移，不要长期双轨 | 建议 |
| 4 | 深色 Mermaid | 边标签带灰色底块 | 截图 | 可在 CSS 里把 `.edgeLabel` 背景设为透明；非必须 | 建议 |

## 其他意见
- 实现附记列出的"与官方站仍有明显差异的地方"共 7 条，属于视觉判断，本报告不复核，交由用户判断。
- "重建必须 `-E -a`"已在 MIGRATION-NOTES 里写明，校验方复现构建时也按此执行。
