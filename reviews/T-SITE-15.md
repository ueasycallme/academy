# T-SITE-15 校验报告：颜色模式按钮改为两态（浅 ↔ 深）

校验 session：isaac-academy-examine，2026-10-09
结论：**通过**（1 条建议，不阻塞）

## 与主题源码对照

pydata-sphinx-theme 0.16.1。从 `.venv` 中 `pydata-sphinx-theme.js.map` 的 sourcesContent 读取 `setTheme`、`cycleMode`、`addModeListener` 三个函数。
- **写入的内容**：`theme-toggle.js` 的 `apply()` 与 `setTheme` 写入相同的四项：`<html>` 的 `data-mode` / `data-theme`、`.dropdown-menu` 的 `dropdown-menu-dark` 类，以及 `localStorage` 的 `mode` / `theme`。
- **没有照做的部分**：`setTheme` 的 console.log 和 `prefersDark.onchange` 两步，`apply()` 没有做。对两态模式来说，onchange 本来就该是空的，原因见建议 1。
- **为什么主题的 `cycleMode` 不再执行**：主题在 `.theme-switch-button` 元素上注册 `cycleMode`；本脚本在 document 的捕获阶段调用 `stopPropagation`，事件到不了按钮本身。实测与此一致（见下表，没有出现 auto）。
- **加载顺序**：构建出的 HTML 里，`theme-toggle.js` 是普通 `<script>`，主题 JS 是 `<script defer>`。所以主题的 `addModeListener` 先执行；本脚本的 `setup` 在 DOMContentLoaded 时才执行。

## 实测

用 worktree 快照在 scratch clone 中构建，http 服务挂在空闲端口上（8765 已被别的服务占用）。headless Chrome 中用同源 iframe 驱动，每一步记录 `data-mode`、`data-theme`、localStorage、可见按钮显示的图标和 body 背景色。共测三种配置：1440 宽；1440 宽、系统深色（`--force-dark-mode`，另用 `matchMedia` 对照确认，这个 flag 确实让 `prefers-color-scheme: dark` 为 true）；500 宽（移动端布局）。三种配置结果完全相同：

| 步骤 | mode / theme / localStorage | 图标 | 背景 |
|---|---|---|---|
| 首次访问（无存储） | light | light | #fff |
| 点击 1 / 2 / 3 | dark → light → dark | 随之切换 | #111 / #fff / #111 |
| 刷新 | dark（保持） | dark | #111 |
| 再点 1 次 | light | light | #fff |
| 存的是 auto，加载后 | light | light | #fff |
| 再点 1 次 | dark | dark | #111 |
| 设为 dark 后打开另一页（1.8） | dark | dark | #111 |

- **验收标准**：两个方向都一次点击；刷新后、跨页后都能保持；存的 auto 按 light 处理。全部满足。
- **按钮数量**：每页有 2 个 `.theme-switch-button`（导航栏一个、侧栏一个），任何宽度下只有 1 个可见。测试点的是可见的那个。
- **报错**：页面 onerror 0 条，Chrome console error 0 条。
- **其他检查**：本页没有 `.dropdown-menu`，所以深色类那一步不可测，只按源码对照。`check_head_build.sh --worktree`（-W）通过。`conf.py` 的改动只有 `html_js_files` 末尾加了一项。

## 建议（不阻塞）

| 位置 | 问题 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|
| `theme-toggle.js` 中 `setup()` 对 auto 的处理 | 存的是 auto 时，换成 light 的时机是在 DOMContentLoaded，这时主题已经执行过 `setTheme("auto")` | 主题源码：`setTheme` 在 mode 为 auto 时设置 `prefersDark.onchange = autoTheme`，`addModeListener` 由 defer 脚本先执行。推断有两个后果，都只发生在存过 auto 的读者的第一个页面上：① 系统为深色时，页面先按 head 内联脚本显示深色，再翻成浅色，可能闪一下；② 本页停留期间如果系统切换深浅色，`autoTheme` 仍会改写 `data-theme`，使它和 `data-mode = light` 不一致。两点都只是读源码得出的推断，headless 下无法切换系统配色，没有复现 | 把 auto → light 的转换移到脚本顶层立即执行（改写 `localStorage` 和 `dataset.mode`、`dataset.theme`）。本脚本先于 defer 的主题 JS 执行，这样主题的 `setTheme` 读到的就是 light，onchange 会被置空，也不会闪 | 建议 |

## 第 2 轮：建议已采纳（复核）

实现 session 把 auto → light 的转换移到了脚本顶层立即执行：`localStorage` 的 mode 或 `dataset.mode` 为 auto 时，立即 `apply(default)`。
- **复核方法**：用新的 worktree 快照重新构建，在同样三种配置下重跑上表全部步骤，结果与第 1 轮逐行相同，页面错误和 console error 都是 0 条。
- **建议的效果有直接证据**：主题的 `setTheme` 每次执行都会打印一条 `[PST]: Changed to <mode> mode …`。在"存的是 auto"那次加载中，这条记录是 `Changed to light mode using the light theme.`，也就是说主题收到的已经是 light，按源码 `prefersDark.onchange` 被置空，不会留下"跟随系统"的监听。全程没有出现 auto。
- **仍未直接验证的一点**：系统深色下首屏会不会闪一下。原因与第 1 轮相同，headless 下看不到首帧。但转换已经提前到 defer 主题脚本之前，主题不会再按 auto 设置深色。

结论不变：**通过**，建议已关闭。
