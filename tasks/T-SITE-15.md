# T-SITE-15 颜色模式按钮改为两态（浅 ↔ 深）

状态: 已合并
优先级: P2（用户 2026-10-09 反馈：浅→深要点两次、深→浅一次）
类型: 站点
产出: `docs/_static/js/theme-toggle.js`（或并入现有 js），`docs/conf.py` 的 `html_js_files`

## 背景

pydata-sphinx-theme 0.16 的按钮是三态循环：系统为浅色时顺序为 auto → dark → light，从 light 点一次到 auto（系统浅色下看起来仍是浅色），再点一次才到 dark；从 dark 点一次就回 light。这是主题设计，不是 bug，但读者会困惑。本站默认浅色（D-020），不需要 auto。

## 必须完成

1. 页面加载后接管 `.theme-switch-button` 的点击：读取 `document.documentElement.dataset.mode`，`light` ↔ `dark` 直接切换（调用主题暴露的同一套设置逻辑：写 `dataset.mode` / `dataset.theme` 与 `localStorage` 的 `mode` / `theme`，与主题 JS 一致，不另起一套），不再经过 `auto`；首次访问若存的是 `auto`，按 `default_mode`（light）处理。
2. 按钮图标随状态正确显示（主题自己根据 `dataset.mode` 切图标；若接管后图标不更新，补一行触发）。
3. 自检：浅→深一次、深→浅一次，刷新后状态保持；深浅色截图各一张；无 console 报错；`sphinx-build -W` 通过。

## 验收标准

两个方向都是一次点击；刷新保持；无报错。

## 附记

### 实现附记（isaac-academy-accomplish，2026-10-09）

**本页新增/修改的项目文件**：新增 `docs/_static/js/theme-toggle.js`；`docs/conf.py` 的 `html_js_files` 加入 `js/theme-toggle.js`。

**做法**：
- pydata-sphinx-theme 0.16.1 的 `setTheme` 与 `cycleMode` 是模块内部函数，没有暴露给页面（从主题 JS 的 source map 读到源码）。所以本脚本按 `setTheme` 的写法重做了同样的几步：`<html>` 的 `data-mode` / `data-theme`、`.dropdown-menu` 的 `dropdown-menu-dark` 类、`localStorage` 的 `mode` / `theme`。
- 用 document 上的捕获阶段监听器接管 `.theme-switch-button` 的点击，`stopPropagation` 之后，主题注册在按钮上的 `cycleMode` 就不会执行；`light` ↔ `dark` 直接切换。
- 页面加载时，若 `data-mode` 为 auto（以前存过），按 `data-default-mode` 处理，本站为 light。
- `localStorage` 不可用时，只切换当前页面。
- 图标由主题 CSS 根据 `data-mode` 显示，不需要另外触发。

**自检**（headless Chrome，经本地 http 服务）：
- **浅色起步**：连点三次，序列为 light → dark → light → dark，每次都是一击切换；记录的是 mode/theme/localStorage 三者，始终一致。
- **深色起步**：先存 dark 再刷新，加载后为 dark；连点三次为 dark → light → dark → light。说明刷新后状态能保持。
- **存过 auto**：先存 auto 再刷新，加载后为 light/light/light。
- console 报错为 0。
- **截图**：深色模式下导航栏图标显示为月亮（`/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/f3f4833b-8289-4aef-a2b3-96df640b88d0/scratchpad/tt-darkclick.png`），浅色见 `/tmp/claude-1000/-home-wuql-wuql-ws-academy-ws-isaac-tutor/f3f4833b-8289-4aef-a2b3-96df640b88d0/scratchpad/tt-light.png`。

**验证**：`check_head_build.sh --worktree`（-W）通过。

### 校验附记（isaac-academy-examine，2026-10-09）

**通过**，有 1 条建议，不阻塞。报告见 `reviews/T-SITE-15.md`。

- **源码对照**：与主题 0.16.1 的 `setTheme` 一致（对照 source map）。
- **实测**：headless Chrome 下测了三种配置：1440 宽；1440 宽、系统深色；500 宽。两个方向都是一次点击，刷新后、跨页后都保持，存的 auto 按 light 处理，图标随之切换，报错 0 条。-W 构建通过。
- **建议**：把 auto → light 的转换移到脚本顶层立即执行，避开主题先执行 `setTheme("auto")` 留下的 onchange 和可能的闪烁。这一点是读源码得出的推断，没有复现。
