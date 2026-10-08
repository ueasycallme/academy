# T-SITE-11 浏览器标签页图标（favicon）

状态: 待实现
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
