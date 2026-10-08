# T-SITE-11 校验报告：站点图标

- 校验日期：2026-10-08
- 校验 session：isaac-academy-examine
- 范围：`docs/_static/img/favicon/`（SVG 与 3 个 PNG）、`docs/_tools/make_favicons.py`、`docs/_templates/layout.html`、`docs/conf.py` 的 `html_favicon`、仓库根 `README.md` 第 28 行

## 结论：通过

只有一项未完成：真实浏览器标签栏的截图。校验方也拿不到（见"未完成项"），留给用户上线后看一眼，不阻塞。

## 核对

- **构建**：`tools/check_head_build.sh --worktree`（-W）通过。
- **`<head>` 链接**：首页与深层页面（`6-galbot/1-asset/6.1.6-articulation-cfg.html`）都有 4 个图标链接，SVG（`_static/favicon.svg`）、PNG 32、PNG 16 和 apple-touch-icon，深层页面用 `../../_static/…` 相对路径。本地服务器上 4 个地址都返回 200，类型为 `image/svg+xml` 与 `image/png`。
- **`favicons` 主题选项**：实现方说 pydata 0.16.1 不支持 `html_theme_options["favicons"]`，校验方独立复现了：在 scratch 副本的 conf.py 中加上这个选项，`sphinx-build -W` 报 `WARNING: unsupported theme option 'favicons' given` 并失败（rc 1）。`theme.conf` 中没有声明 `favicons`，`__init__.py` L213–224 仍会处理 `theme_favicons`，但这个变量在 0.16.1 中传不进去。所以改用 `layout.html` 的 `extrahead` 是合理的备选方案。
- **图形与许可**：`favicon.svg` 只有 4 个圆角矩形，是 `academy-logo.svg` 去掉留白、台阶加厚后的版本，没有文字。图标文件中没有 NVIDIA 相关内容。配色沿用 T-SITE-03 已通过的站点 logo。
- **PNG 与 SVG 一致**：`make_favicons.py` 的 SHAPES 坐标与 SVG 相同。校验方用 headless Chrome 把 SVG 栅格化到 16 / 32 px，与 PNG 并排比较，形状一致。apple-touch-icon 为 180 × 180、不透明（左上角像素是 #76B900）。
- **浅色 / 深色可辨**：把 16、32 px 的 PNG 与 SVG 栅格放在 Chrome 标签栏的 4 种底色上，放大 8 倍检查：浅色活动标签 #ffffff、浅色标签栏 #dee1e6、深色活动标签 #35363a、深色标签栏 #202124。三层台阶在 16 px 下都能分清，圆角绿底在深浅两种底色上边界清楚。拼图见 `reviews/img/T-SITE-11-favicon-tabs.png`。
- **README**：根目录 README L28 写明了图标文件的来源、生成工具（Pillow 脚本，8 倍超采样）以及改了 SVG 要同步改脚本，满足卡片第 4 项。

## 未完成项（不阻塞）

卡片第 3 项要求"在真实浏览器中强制刷新，截取浅色 / 深色标签栏"。headless Chrome 没有标签栏，校验方尝试用 Claude in Chrome 打开本地站点，但扩展未连接，所以没有拿到真实标签栏的截图。上面的底色拼图模拟了标签栏的渲染。建议用户在上线后打开 academy.kiloong.com，强制刷新，看一眼浅色 / 深色系统主题下的标签页图标。
