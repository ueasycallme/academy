# T-SITE-11 浏览器标签页图标（favicon）

状态: 已合并
优先级: P1（用户直接要求；不占 GPU，穿插做）
类型: 基础设施
产出: `docs/_static/img/favicon.svg`、`favicon-32.png`、`favicon-16.png`、`apple-touch-icon.png`（180×180）；`docs/conf.py`

## 背景

用户反馈：浏览器标签页现在显示的是默认的地球图标。站点已有自制标识 `docs/_static/img/academy-logo.svg`（顶栏用）。

## 必须完成

1. 以 `academy-logo.svg` 为基础做 favicon：裁成正方形、去掉文字只留图形（16×16 下文字不可读），保证在浅色与深色标签栏上都看得清（必要时加圆角底色）。不使用任何 NVIDIA 素材（D-020 / T-SITE-03 的许可约束）。
2. 生成 SVG 与 PNG 两套：`html_favicon` 指向 SVG；用 `html_extra_path` 或 `html_static_path` + `templates` 在 `<head>` 里补 `<link rel="icon" type="image/png" sizes="32x32">`、`16x16`、`apple-touch-icon`，保证旧浏览器与 iOS 书签也有图标（pydata 主题支持通过 `html_theme_options["favicons"]` 配置多尺寸图标，优先用它，给文档链接）。
3. 本地构建后用浏览器确认标签页图标生效（强制刷新，favicon 有缓存）；截图浅色与深色主题各一张放附记。
4. 在 README 的目录说明里加一行图标文件的来源与生成方式（用什么工具从 SVG 导出 PNG）。

## 验收标准

`sphinx-build -W` 零警告；线上页面 `<head>` 含 SVG + PNG 图标链接；标签页图标在浅色/深色下可辨；不含 NVIDIA 素材。

## 附记

（实现/校验 session 写）

### 实现附记（isaac-academy-accomplish，2026-10-08）

**新增 / 修改的文件**：
- 新增 `docs/_static/img/favicon/favicon.svg`、`favicon-16.png`、`favicon-32.png`、`apple-touch-icon.png`；
- 新增 `docs/_tools/make_favicons.py`（Pillow，PNG 的生成脚本）、`docs/_templates/layout.html`；
- 修改 `docs/conf.py`（`html_favicon`）、仓库根 `README.md`（目录表加一行）。

**做法与依据**
- 图形：`academy-logo.svg` 本身就是正方形、没有文字。favicon 版去掉四周 4 px 的留白，铺满并加圆角（rx 14/64），三级台阶加厚（高 8 → 12），16 px 下仍能分出三层。颜色沿用 logo 的 #76B900 / #004831 / 白，不含 NVIDIA 图形。
- **没有用 `html_theme_options["favicons"]`**：pydata-sphinx-theme 0.16.1 的代码仍处理 `theme_favicons`（`__init__.py` L213–L224），但 `theme.conf` 没有声明这个选项。实测写进 conf.py 后报 `WARNING: unsupported theme option 'favicons' given`，`-W` 构建失败。所以按卡片的备选方案，用 `_templates/layout.html` 继承 `!layout.html`，在 `extrahead` 块里加 PNG 与 apple-touch-icon 的 `<link>`；SVG 由 `html_favicon` 生成（Sphinx 复制为 `_static/favicon.svg`）。
- PNG 的生成：环境里没有 cairosvg / rsvg / inkscape，所以用 Pillow 按 SVG 的同一组矩形绘制，8 倍超采样后缩小。apple-touch-icon 按 iOS 惯例为不透明方形，不加圆角。

**验证**
- `tools/check_head_build.sh --worktree` 通过。
- 生成的页面 `<head>` 里有 4 个链接，深层页面用相对路径（如 `../../_static/img/favicon/favicon-32.png`）；本地服务器上 4 个文件都返回 200，类型分别为 image/svg+xml 与 image/png。
- 浅色 / 深色可辨：headless Chrome 截不到标签栏，所以把 16 px 与 32 px 图标贴在 Chrome 浅色（#f1f3f4）与深色（#35363a）标签栏的底色上，放大 2 倍检查，两种底色下都清楚可辨。截图在 scratchpad `favicon_tabs.png`，校验方可以用 make_favicons.py 的输出自己拼图。真实浏览器标签页的截图（带强制刷新）需要有界面的浏览器，本 session 做不到，请校验方或用户在本地或线上确认。

### 校验附记（isaac-academy-examine，2026-10-08）

**通过**，见 `reviews/T-SITE-11.md`。-W 通过；首页与深层页面的 4 个链接都返回 200；"`favicons` 选项不受支持"已独立复现；PNG 与 SVG 一致，在 4 种标签栏底色上都可辨（`reviews/img/T-SITE-11-favicon-tabs.png`）。真实浏览器标签栏的截图双方都拿不到（headless 没有标签栏，Chrome 扩展未连接），建议用户上线后看一眼，不阻塞。
