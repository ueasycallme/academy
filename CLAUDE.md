# isaac_tutor — academy.kiloong.com

Isaac Sim / Isaac Lab 中文学习网站的内容仓库。定位是官方文档之上的"导读层"：讲清体系框架、核心概念和工程落地。解释原创，细节链接官方文档与源码，不搬运原文。

- 主线版本：**Isaac Sim 5.1.0 + Isaac Lab 2.3.2**。3.0 前沿专栏基于 Isaac Sim 6.1 + Isaac Lab 3.0.0-EA。
- 主线机器人：Galbot One Golf（https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description）。
- 读者：会 Python，未接触 Isaac / USD，无 RL 基础。
- 站点：Sphinx + MyST + pydata-sphinx-theme（`docs/` 为源，页面用 MyST 写，模板见 CONVENTIONS 第 2 节），GitHub Pages 托管，仓库 https://github.com/ueasycallme/academy ，域名 academy.kiloong.com。中文翻译站 isaac.kiloong.com 是官方文档的中文版，可作延伸阅读链接。

## 三个 session 协作

本目录由三个 Claude Code session 同时工作，职责与文件所有权见 `WORKFLOW.md`，**开始任何工作前先读它**：

| Session 名 | 角色 |
|---|---|
| `isaac-tutor-de` | 设计：大纲、规范、任务卡、裁断 |
| `isaac-academy-accomplish` | 实现：写 `docs/` 与 `examples/` |
| `isaac-academy-examine` | 校验：写 `reviews/` |

必读文件：`WORKFLOW.md`（协议）→ `CONVENTIONS.md`（写作与代码规范）→ `OUTLINE.md`（大纲）→ `tasks/`（任务卡）。裁断记录在 `DECISIONS.md`，已裁断的事项不再争论。

## 硬规则

1. 只写自己角色拥有的文件。任务卡中只能改"状态"与"附记"区。
2. 架构、版本、API 相关的断言必须有来源（官方文档链接、源码 permalink、release notes）。无法查证的写"推断"并说明依据。
3. 代码示例必须标注验证版本；未在真实环境跑过的代码标注"未验证"。
4. 不大段复制官方文档原文；引用超过一句话就改为链接。
5. 中文写作，术语首次出现附英文；术语定义以 `docs/0-map/0.8-glossary.md` 为准。
6. 提交 git 由设计 session 负责；其他 session 不执行 `git commit`。
