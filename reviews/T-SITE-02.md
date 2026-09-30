# T-SITE-02 校验报告

- 校验日期：2026-09-30
- 校验版本：n/a（站点基础设施；mkdocs 1.6.1 / mkdocs-material 9.7.7 / mermaid 11.17.2）
- 结论：**通过**（附 2 条建议）

## 断言核查
| # | 位置 | 断言 | 是否成立 | 备注 |
|---|---|---|---|---|
| 1 | 附记·产出 | `mermaid.min.js` 即 npm 上 `mermaid-11.17.2.tgz` 里的 `dist/mermaid.min.js`，sha256 `581ed7d7…0eb8` | 成立 | 从 registry 重新下载 tarball 比对，sha256 一致；`mermaid.LICENSE.txt` 与 tarball 内的 `LICENSE` 逐字节相同 |
| 2 | 附记·Mermaid 方案 | Material 9.7.7 仅在 `typeof mermaid=="undefined"` 时才从 unpkg 拉取 | 成立 | bundle 原文：`typeof mermaid=="undefined"\|\|mermaid instanceof Element?_t("https://unpkg.com/mermaid@11/dist/mermaid.min.js"):$(void 0)`。unpkg 地址仍作为休眠的回退留在 bundle 里（构建产物 grep 只在 bundle 中命中），不会触发 |
| 3 | 附记·图标 | 图标为内联 SVG，无外部请求 | 成立 | 屏蔽外网的测试中，页面没有产生任何外部请求（见下） |
| 4 | 附记·验证 | 构建产物中的 HTML 不含境外资源域名 | 成立 | `_template-check` 页只有 `academy.kiloong.com`（canonical）、`squidfunk.github.io`（正文链接）、`w3.org`（SVG 命名空间），都不是资源加载 |

## 覆盖检查（任务卡"必须完成"）
1. Mermaid 自托管：已完成。方案与理由已记录，理由成立。
2. 字体：已完成。`font: false`；`extra.css` 设置了 `--md-text-font` 和 `--md-code-font` 系统字体栈，截图中正文确为系统中文字体。
3. 图标：已完成。
4. 验证与域名清单：已完成。
5. README：已完成，含 `env -u PYTHONPATH` 说明。

## 验证（真实屏蔽外网）
实现方没有做断网测试，校验方补做了：

| 项 | 方法 | 结果 |
|---|---|---|
| strict 构建 | `env -u PYTHONPATH .venv/bin/mkdocs build --strict` | 退出码 0，零 WARNING |
| 屏蔽外网渲染 | `google-chrome --headless=new --host-resolver-rules="MAP * ~NOTFOUND, EXCLUDE 127.0.0.1"`，即除 127.0.0.1 外**所有域名都解析失败**，然后对 `_template-check` 截图，浅色与 `--force-dark-mode` 深色各一张 | 两张截图里 Mermaid 图都完整渲染，admonition 图标正常；深色下节点文字清晰可读 |
| 网络记录 | `--log-net-log` | 页面请求只指向 `127.0.0.1`。记录中其余的 google/gstatic/googleapis 主机都是 Chrome 浏览器自身的后台服务（更新、翻译、账号等），与页面无关，且同样被屏蔽；**没有** `unpkg.com`、`fonts.googleapis.com`、`fonts.gstatic.com`、`cdn.jsdelivr.net` |
| 0.2 页 | 同样屏蔽外网，全页截图 | 两张图都能渲染（但发现一个与本任务无关的内容问题，见"其他意见"） |

## 问题清单
无阻塞 / 一般问题。

## 其他意见（建议）
| # | 位置 | 意见 | 建议 | 严重度 |
|---|---|---|---|---|
| 1 | `mkdocs.yml` 的 extra_javascript 注释 / README | 本方案依赖 Material bundle 内部的 `typeof mermaid` 判断，而不是公开配置项。另外 npm 上 mermaid 最新版已是 12.0.0，以后升级 Material 可能随之切换 Mermaid 大版本 | 在 README 里加一条升级检查项："升级 mkdocs-material 后，grep bundle 里的 `unpkg.com/mermaid@` 确认大版本，并复跑屏蔽外网的截图测试"（命令见上） | 建议 |
| 2 | 验收方法 | 屏蔽外网的 headless 截图命令只需一行，适合作为今后改动站点配置时的回归检查 | 由设计 session 决定是否写进 CONVENTIONS 或 README | 建议 |
| — | 0.2 页（**不属于本任务**） | 屏蔽外网截图时发现：0.2 页图 1、图 2 实际渲染为 **GPU 在最上、用户代码在最下**，与正文"下图自底向上画出"相反。原因是 `flowchart BT` 配合"依赖方 --> 被依赖方"的边写法，会把被依赖方放在上面。图 1 的子图 `direction LR` 也没有生效，三大基础被竖着排。这是 T-0.2 两轮校验都漏掉的问题（前两轮只做了 DOM 尺寸检查，没有看截图），已单独报告设计 session | 见 `reviews/T-0.2.md` 第 3 轮补充 | — |
