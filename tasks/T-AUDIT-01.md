# T-AUDIT-01 全站质量巡检（校验 session 主导）

状态: 待校验（报告已交，问题由设计 session 拆微任务）
优先级: P2（校验方空闲时做；不占 GPU）
类型: 巡检（产出是报告，不改页面；问题由设计 session 拆成微任务）
产出: `reviews/AUDIT-01.md` + 自动化脚本放 `reviews/scripts/audit-*.{py,sh}`（可重复运行，以后每月跑一次）

## 范围（全部已上线页面，以 HEAD 为准）

1. **外链**：全站 `http(s)://` 链接逐个 HEAD/GET，列出非 200（403 的按 CONVENTIONS 第 4 节区分"抓取被拒"与真失效）；重定向到新地址的列出新旧对照。
2. **站内锚点**：`sphinx-build -W` 不查 `#锚点` 是否存在于目标页——用脚本解析所有 `page.md#anchor` 与 `{ref}`，核对目标标题/label 存在。
3. **术语一致性（D-018）**：对术语表里每个词条，grep 全站首次出现是否按"中文（English）"写法、之后是否只用中文；列出不一致页（抽样即可，但覆盖率写明）。
4. **图字号（D-025）**：对所有含 Mermaid / SVG / PNG 图的页面，在 1440 与 2560 下量最小字号，列出 < 12px 的（用 `reviews/scripts/diagram-fontprobe.js`）。
5. **版本说明一致性**：每页"版本说明"末尾是否有 T-8.6b 的固定句；8.6 表 2 的归类是否与各页 `sources_checked` 一致。
6. **占位页**："现在可以读什么"列表是否都指向已上线页（gen_placeholders 的逻辑之外再核一遍）。
7. **代码示例头注**：`examples/**` 每个 .py 文件头是否有验证版本/日期/GPU（CONVENTIONS 第 5 节）；缺的列出。

## 产出格式

报告按"阻塞 / 一般 / 建议"分级，每条：页面、位置、问题、建议；末尾给一张汇总表（每类检查了多少、问题多少）。脚本可重复运行并打印同样的汇总。

## 附记

（校验 session 写；实现 session 不参与本卡）

### 实现附记（isaac-academy-examine，2026-10-09）

产出：`reviews/AUDIT-01.md`，以及 `reviews/scripts/audit-{links,anchors,terms,fonts,version,placeholders,examples}.py` 和总入口 `audit-all.sh`。基准为 HEAD 386aa36。全量跑一次约 4 分钟，在克隆里构建，不碰工作区。

**结果**：
- 阻塞：0 条。
- 一般：3 条。
  - G-1：D-018 在首次详细讲解页缺对照 49 处，涉及 29 页，报告附表按页列出；
  - G-2：1.5 缺固定句（我在 T-1.5 校验时漏查了）；
  - G-3：6 个 examples 文件的头注缺项。
- 建议：8 条（S-1 至 S-8）。
- 外链与站内锚点：没有失效。
- 图字号：全部 ≥ 12 px。
- 8.6 表 2：日期与各页逐一一致。

脚本局限写在报告第 4 节。
