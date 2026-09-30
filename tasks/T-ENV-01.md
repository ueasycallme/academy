# T-ENV-01 披露 Isaac Sim 5.1.0 的 Unsupported 状态

状态: 已合并
优先级: P1（T-1.4 交校验后立即做）
类型: 微任务（跨页，D-019）
产出: 修改 `docs/0-map/0.1-overview.md`、`docs/1-env/1.1-compat-matrix.md`、`docs/1-env/1.2-version-decision.md`、Sphinx 公告条文案（site-sphinx 同步）

## 必须完成

1. 三页各加一个 `warning` 提示框（措辞统一，放在首次提到主线版本处）：Isaac Sim 5.1.0 官方文档已标注 "Unsupported release"（引用原文一句并脚注 5.1.0 文档页）；本站仍以 5.1.0 + Isaac Lab 2.3.2 为主线的理由（2.3.x 最高支持 5.1；3.0 仍为 EA，GA 目标 2026-10 底，来源 v3.0.0-EA release notes）；主线将在 3.0 GA 后切换，进展见 8.6。
2. 1.1 表中 Isaac Sim 5.1 行加"官方支持状态：已停止支持（2026-09 核对）"列或备注；6.0/6.1 行写"支持中"。
3. 站点公告条改为："主线：Isaac Sim 5.1.0（官方已停止支持）+ Isaac Lab 2.3.2；3.0 前沿专栏基于 EA。为何仍选 5.1.0 → 链接 1.2"。
4. 8.6 版本追踪占位页顶部加一行"待写：跟踪 3.0 GA 与主线切换"。

5. 首页"从哪里开始"指向改为 0.1（入口页），不是 0.2（reviews/T-SITE-06.md 一般意见）。

## 验收标准

三页 warning 措辞一致；来源脚注成立；两站构建零警告；校验只复核这些改动。

## 附记

（实现/校验 session 写）

### 实现附记（isaac-academy-accomplish，2026-09-30）

**当前在做**：本任务已完成。接下来做 T-SITE-07。页面已是 MyST 源（T-SITE-06 之后的 `docs/`）。

1. **统一 warning**：三页使用完全相同的 MyST 提示框（标题"Isaac Sim 5.1.0 已不再获官方支持"，`:class: warning`），正文只有 8.6 的相对链接路径随页面位置不同。位置如下：
    - `docs/0-map/0.1-overview.md`："本站怎么读"一节"版本"一条之后
    - `docs/1-env/1.1-compat-matrix.md`："Isaac Lab 主表"之前
    - `docs/1-env/1.2-version-decision.md`："决策树"之前
   三页各加 3 个脚注，键名统一加 `env01-` 前缀以免与页内已有脚注冲突：`[^env01-unsupported]`（5.1.0 文档横幅原文一句，已用 curl 复核全文为 "Unsupported release: Isaac Sim 5.1.0 is no longer supported. Bug fixes and new features are delivered only in newer releases."）、`[^env01-readme]`（v2.3.2 README 支持集合）、`[^env01-lab30]`（v3.0.0-EA Release Notes：EA、GA 目标 2026-10 底）。
2. **1.1 表 2 新增列"官方支持状态（2026-09 核对）"**：
    - 5.1 为"已停止支持"（`[^env01-unsupported]`）；
    - 6.0 与 6.1 为"支持中"（新脚注 `[^support6]`：curl 复核 6.0.0 与 6.1.0 文档首页，都没有 Unsupported 横幅）；
    - 4.5 与 5.0 为"官方文档已下线"（沿用 `[^sim45]`）。
   顺手修正：新增列时，替换表头分隔行误改到了主表，现已按各表表头的列数重写所有分隔行（主表 8 列、表 2 8 列、RL 表 4 列、更新记录 2 列），渲染后逐表核对了列数。
3. **公告条**：`conf.py` 中 `announcement` 改为"主线：Isaac Sim 5.1.0（官方已停止支持）+ Isaac Lab 2.3.2；3.0 前沿专栏基于 EA。为何仍选 5.1.0 →"，末尾链接指向 `/1-env/1.2-version-decision.html`。由于文案变了，关闭按钮的 localStorage 键也随之变化，之前关闭过的读者会重新看到公告，这符合设计。
   - 注意：链接用的是站点根相对路径，托管在自定义域名根目录 academy.kiloong.com 时正确；如果 T-SITE-07 改为部署在 `github.io/academy/` 这样的子路径下，这个链接需要改。已在 T-SITE-07 中留意。
4. **8.6 占位页**：标题下加一行"待写：跟踪 3.0 GA 与主线切换。"

**验证**：`tools/check_head_build.sh --worktree` 构建通过；headless Chrome 在三页上确认 warning 标题存在，公告条 HTML 含链接与关闭按钮，1.1 各表列数正确。

**备注**：1.4 页开头在 T-1.4 中已有一个同主题的 warning，措辞略有不同（当时按 D-019 写，比本卡早）。1.4 仍在校验中，是否也统一成本卡的措辞，请设计 session 决定，改动很小。

### 校验附记（isaac-academy-examine，2026-09-30）
结论：通过。三页 warning 逐字一致，来源成立（5.1.0 横幅、README 版本表、3.0 EA release notes 均已核对）；1.1 支持状态列与公告条、8.6 占位页均按任务卡完成；构建通过。2 条建议（"支持中"应标为推断；1.4 页的同类 warning 措辞可统一）。
