# T-SITE-01 校验报告

- 校验日期：2026-09-30
- 校验版本：n/a（站点基础设施；mkdocs 1.6.1 / mkdocs-material 9.7.7 / pymdown-extensions 12.1）
- 结论：**通过**（附 3 条"建议"级意见）

## 断言核查
| # | 位置 | 断言 | 来源是否成立 | 备注 |
|---|---|---|---|---|
| 1 | 任务卡附记·说明 1 | Material search 插件检测到 jieba 即自动分词 | 成立 | `material/plugins/search/plugin.py`：模块级 `try: import jieba`；`if jieba:` 时对 title/text 调 `_segment_chinese`（`jieba.cut`，以 `​` 连接）。构建产物 `search/search_index.json` 中首页文本已按词插入 `​`，确认生效 |
| 2 | 附记·说明 2 | Material 9.7.x 打印 MkDocs 2.0 横幅，不影响 strict | 成立 | 构建输出有横幅，`--strict` 退出码 0 |
| 3 | 附记·说明 3 | Mermaid 运行时从 unpkg 加载 mermaid@11 | 成立 | 浏览器 resource 记录：`https://unpkg.com/mermaid@11/dist/mermaid.min.js` |
| 4 | 附记·产出 | requirements 全部锁定 | 成立 | 7 个包均为 `==` |

## 覆盖检查（任务卡"必须完成"）
1. `mkdocs.yml`：已覆盖。site_name / site_url / material / `language: zh` / 深浅色切换 / `navigation.tabs` / `toc.follow` / `content.code.copy` / 搜索 `lang: [zh, en]` 均在；扩展 admonition、details、superfences(mermaid)、tabbed、highlight、footnotes、attr_list、md_in_html、`toc(permalink)` 均启用。nav 为首页 + 0-map。
2. `docs/index.md`：已覆盖（定位 + 与 isaac.kiloong.com 关系表）。
3. `requirements-docs.txt`：已覆盖，版本锁定。
4. `.gitignore`：已覆盖（site/、__pycache__/、*.pyc、.venv/、venv/、.cache/）。
5. strict 构建 / serve：已覆盖（见下）。
6. `_template-check.md`：已覆盖，且确认不出现在左侧导航。

## 构建与渲染验证
| 项 | 命令 / 方法 | 结果 |
|---|---|---|
| strict 构建（仓库 .venv） | `env -u PYTHONPATH .venv/bin/mkdocs build --strict -d <scratch>/site` | 退出码 0，0 WARNING，0.41 s |
| 干净环境复现 | `uv venv -p 3.10` + `uv pip install -r requirements-docs.txt` + strict 构建 | 退出码 0 |
| 渲染（Chrome，DOM/计算样式检查） | 静态服务构建产物，打开 `/0-map/_template-check/` | admonition：abstract/info/note/tip/warning/danger + 可折叠 details 共 7 个；tabbed-set 1 组；脚注 1 条；代码复制按钮 2 个；headerlink 8 个 |
| Mermaid 浅色 | 同上 | 渲染为 div（826×515），标签色 `#36464e` on 白底 |
| Mermaid 深色 | 切 `data-md-color-scheme=slate` | 仍为 826×515，标签色 `hsla(225,18%,86%,0.82)` on `rgb(30,33,41)`，可读 |

说明：Chrome 标签页截图超时（与实现 session 遇到的情况相同），渲染结论来自 DOM 与计算样式，未做肉眼截图确认。

## 问题清单
无阻塞 / 一般问题。

## 其他意见（建议级）
| # | 位置 | 意见 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|---|
| 1 | Mermaid 加载 | Mermaid 从 unpkg CDN 运行时加载；目标读者多在中国大陆，unpkg 访问不稳定时所有依赖图将显示为空白 | 浏览器 resource 记录 | 部署前评估：用 `extra_javascript` 自托管 mermaid.min.js，或换国内可达 CDN；至少在 1.9 排障页记一条 | 建议 |
| 2 | `mkdocs.yml` `nav` / `not_in_nav` | 骨架已包含 0.2 页入口及 0.3/0.4/1.1/8.1 占位页，超出本任务"只填首页与 0-map 占位"的范围（占位页路径已由 D-007 认可） | 任务卡"必须完成 1" | 无需修改；设计 session 提交时注意 T-SITE-01 与 T-0.2 的文件归属 | 建议 |
| 3 | 本地环境 | shell 带 ROS 2 Humble 的 PYTHONPATH，在 `.venv` 里 `pip freeze` 会混入 ROS 包，容易误导以为依赖不干净 | `pip freeze` 输出 | 附记"本地环境"一行补充 `env -u PYTHONPATH`（或在 README 里说明） | 建议 |
