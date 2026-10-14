# T-SITE-15 校验报告：示例代码的获取方式

校验 session：isaac-academy-examine，2026-10-15
结论：**通过**。

## 核对

**构建**：
- 工作区的 docs、examples、`.gitignore` 拷进草稿克隆，提交后在克隆里 `sphinx-build -E -a -W --keep-going` 构建（`scratch/examine/site15_html/`），rc 0。
- 构建后克隆的 `git status` 是干净的：zip 已被 `.gitignore` 挡住。
- 另用 `git archive` 把同一提交导出到一个没有 `.git` 的目录再构建（对应 `check_head_build.sh` / `merge_task.sh` 的做法），rc 0，同样打出 298 个文件，`VERSION.txt` 的提交号为"未知"，符合卡上要求。
- 线上用的 `pages.yml` 是普通的 `actions/checkout`，有 `.git`，所以线上的包会写真实的提交号。

**zip 内容**（`_build/html/_static/academy-examples.zip`）：
- 298 个文件，等于 git 跟踪的 `examples/` 下 297 个文件加 `examples/VERSION.txt`；
- 逐个比对：没有 git 之外的文件，也没有漏掉的；
- 没有 `__pycache__`、`.pyc`、`generated/`、`logs/`、`outputs/`、`datasets/`、`third_party/`、`.venv/`、`.log`；
- 顶层是 `examples/`，下分 `isaaclab-2.3/`（259 个）与 `isaaclab-3.0/`（38 个）；
- 压缩后 0.55 MB，解压后 1.03 MB。卡上"约 1.7 MB"只是估计，内容齐全，不算问题；
- `VERSION.txt` 写了构建日期与提交号。
- 1.4 提示框里的链接被 MyST 当成下载角色，多复制了一份到 `_downloads/…/academy-examples.zip`，与 `_static` 那份逐字节相同，不影响使用。

**解压后实跑**：
- zip 解压到空目录 `scratch/examine/site15_unzip/`，在该目录用本 session 的 5.1 环境（env51，`env -i`）运行 `python examples/isaaclab-2.3/1.4-install/verify_install.py`；
- rc 0，`SUMMARY: 8/8 passed`（RTX 5090，按进程显存 2667 MiB，7 s）。

**页面路径与 zip**：
- 按种子 20261015 随机抽 3 页（3.5、3.2、4.4），提到的 `examples/` 路径都在 zip 里；
- 又把全站 45 页的 57 个 `examples/…` 路径全部核了一遍，0 缺失。

**页脚**：
- 链接的 href 随目录深度正确：首页为 `_static/…`，1.4 为 `../_static/…`，6.1.1 为 `../../_static/…`；
- 在本地服务器上对链接发 HEAD 请求，返回 200；
- headless Chrome 量得页脚两行在 1440（1.4 页）与 2560（6.1.1 页）下都是 14.4 px，≥ 12 px。

**文本**：
- 1.4"第五步"前的"获取本站示例代码"提示框说清了下载、解压、`cd` 到 `examples/` 的上一级，并说明 Isaac Lab 自带的 `scripts/…` 仍在源码目录运行、第 6 部分项目另见 README（链 6.1.1）；
- 0.1 加了一条指向 1.4 #第五步验证，锚点能解析；
- 没有写 GitHub 地址（D-034）。

**审计脚本**（克隆上）：
- anchors 7306 个，0 问题；version 118 / 116 / 2；nav、figures、examples、placeholders、glossary 都没有新增问题；
- 390 px 下 1.4、0.1 正常。
- `audit-crossref` 曾报"`examples/VERSION.txt` 在 examples 里不存在"。这个文件是构建时生成的，所以本 session 在脚本里加了 `GENERATED` 白名单，之后 0 问题。

## 另记（不作问题）

- `check_head_build.sh --worktree` 直接在工作区的 `docs/` 上构建，所以每次都会在工作区写出 `docs/_static/academy-examples.zip`。它被 `.gitignore` 挡住，不会提交，但意味着这个模式现在会往工作区写文件。本 session 今后只在草稿克隆里构建（校验方不写 `docs/`）。
- 卡上 `_EXAMPLES_EXCLUDE_DIRS` 之外，代码还排除了 `venv`、`.pytest_cache`，比卡上多两项，合理。
