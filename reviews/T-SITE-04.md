# T-SITE-04 校验报告

- 校验日期：2026-09-30
- 校验对象：`site-sphinx/`（8767 预览，另在 scratch 中全量重建）
- 结论：**通过**（2 条建议，交用户决定；"像不像"由用户判断，本报告不评）

## 验收标准逐项
| 验收项 | 核查方法 | 结果 |
|---|---|---|
| 实测对照表覆盖 1–5 项关键属性，差异 ≤ 5% | 校验方**独立抽测**：Chrome 同一窗口（视口 2490px）分别打开官方站 5.1.0 `installation/requirements.html` 与原型 0.2 页，在两边执行同一段 `getComputedStyle` 脚本（官方站只读取，不做任何交互） | 下表各项**完全相同**（差异 0%） |
| 默认浅色，刷新后仍为浅色 | headless Chrome 全新 profile（localStorage 为空），并加 `--force-dark-mode` 模拟系统偏好深色 | `<html data-theme="light" data-mode="light">`；截图 `reviews/img/T-SITE-04-0.2-light-fresh-darkOS.png` |
| 0.2 页深浅色截图与并排对比 | 附记已给出路径（实现方 scratch） | 已提供；视觉判断交给用户 |
| `sphinx-build -W` 零警告 | `-E -a -W --keep-going` 全量重建到 scratch | 退出码 0 |
| 不用 NVIDIA 字体、logo、主题文件 | `conf.py` 只从 Google Fonts 加载 Inter / Noto Sans SC / Roboto Mono，三者均为开源字体（OFL / Apache-2.0）；没有 nvidia-sphinx-theme | ✓ |
| 境外请求 | 按 D-015 不再作为验收项；Google Fonts 链接带 `display=swap`，字体加载失败时回退系统字体、文字不会隐藏 | — |

### 抽测对照（官方站 vs 原型，浅色）
| 元素 | 属性 | 官方站 | 原型 |
|---|---|---|---|
| `.bd-header` | height / background | 48px / #fff | 48px / #fff |
| `.bd-sidebar-primary` | 宽 / flex-basis / min-width / padding-top / 右边框色 | 282 / 20% / 272px / 32px / rgb(209,213,218) | 同左 |
| `.bd-article-container` | 宽 / max-width | 845 / 960px | 同左 |
| `.bd-sidebar-secondary` | 宽 / flex-basis | 282 / 25% | 同左 |
| body | font-size / line-height / color | 16px / 26.4px / #1a1a1a | 同左（font-family 为有意替代：Inter, "Noto Sans SC", Arial…） |
| p | font-size / line-height | 16px / 26.4px | 同左 |
| h1 | size / weight / margin 上·下 | 36px / 700 / 0 · 16.8px | 同左 |
| h2 | size / weight / margin 上·下 | 28px / 700 / 44px · 16.8px | 同左 |
| code | font-size | 14px | 14px（Roboto Mono） |
| th | 下边框色 / 字号 | rgb(0,72,49) / 16px | 同左 |
| footer | font-size | 14.4px | 14.4px |
| 左栏 / 右栏标题 | 文字 | "Table of Contents" / "On this page" | 同左 |

结论：实现附记中"布局、断点、字号、配色原本就一致，差异来自默认深色、字体、栏标题和搜索框"的判断，与校验方的抽测结果一致。

## 问题清单
无阻塞 / 一般问题。

## 建议（交用户决定）
| # | 位置 | 意见 | 建议 | 严重度 |
|---|---|---|---|---|
| 1 | 左右栏标题 | 按任务卡"官方站叫什么就叫什么"，改成了英文 "Table of Contents" / "On this page"，但本站是中文站，正文与导航项都是中文，两个英文标题比较突兀 | 请用户选：保持英文（与官方站完全一致），或改回中文（如"目录" / "本页内容"）。实现方已说明，只需改两个模板各一行 | 建议 |
| 2 | 字体加载 | D-015 的前提是"访问者必然能访问 GitHub"，但 Google Fonts（fonts.googleapis.com / fonts.gstatic.com）在中国大陆的可达性与 GitHub 不同。由于有 `display=swap` 和回退栈，不可达时页面照常显示，只是字体变成系统字体，与 T-SITE-03 之前的观感相近 | 如果中国大陆读者占比高，可考虑自托管 Inter 与 Roboto Mono（体积小），中文继续用系统字体；否则维持现状。仅作提醒，不影响 D-015 | 建议 |

## 其他意见
- 附记里的标题层级检查（0.2 页 h1/h2 使用正确；"逐层说明："一段可以升为 h3）合理，是否修改由设计 session 决定。
