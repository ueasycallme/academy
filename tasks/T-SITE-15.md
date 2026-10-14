# T-SITE-15 示例代码的获取方式（学员反馈：1.4 卡在"本站脚本"处）

状态: 待实现
优先级: P1（学员已卡住；不占 GPU）
类型: 站点 + 微修订
产出: `docs/conf.py`（构建时打包）、`docs/_templates/academy-footer.html`、`docs/1-env/1.4-install-51-232.md`、`docs/0-map/0.1-overview.md`

## 问题

全站 45 页引用 `examples/...` 路径（1.4"第五步：验证"是第一次出现），但没有任何一页说明怎样拿到这些文件。D-034 之后页面上也没有 GitHub 入口。学员在 1.4 的 `python examples/isaaclab-2.3/1.4-install/verify_install.py` 处卡住。

## 必须完成

1. **构建时打包**：`docs/conf.py` 加 `setup(app)`，在 `builder-inited` 事件里把仓库 `examples/` 打成 `docs/_static/academy-examples.zip`（zip 内顶层目录名 `examples/`，保留 `isaaclab-2.3/`、`isaaclab-3.0/` 结构）。排除：`__pycache__/`、`*.pyc`、`generated/`、`logs/`、`outputs/`、`datasets/`、`third_party/`、`.venv/`、`*.log`。用目录遍历，不要用 `git ls-files`（`check_head_build.sh` 与 `merge_task.sh` 在导出的无 .git 目录里构建）。`.gitignore` 加 `docs/_static/academy-examples.zip`。打包结果应约 1.7 MB；在 zip 里附一个 `examples/VERSION.txt`，写构建日期与（若能取到）`git rev-parse --short HEAD`，取不到写"未知"。
2. **页脚入口（全站可见）**：`academy-footer.html` 在免责声明后加一行：`示例代码：<a href="{{ pathto('_static/academy-examples.zip', 1) }}">academy-examples.zip</a>（随站点同步更新）`。样式沿用 `.academy-footer`。
3. **1.4 "第五步：验证"**：在"再跑本站的验证脚本"之前加一个 `:::{admonition} 获取本站示例代码` 框：下载 zip、解压到任意目录、`cd` 到解压后的 `examples/` 的上一级；全站命令里的 `examples/...` 路径都相对这个目录；第 6 部分项目有自己的 README 与安装步骤（链 6.1.1）。四五句话。
4. **0.1 "本站怎么读"**：加一句"示例代码在每页页脚的 zip 里，使用方法见 1.4 第五步"，链到 1.4 的该节锚点。
5. **不写 GitHub 仓库地址**（D-034）。若设计后续裁断允许 `git clone`，再加。
6. `sphinx-build -W` 通过；本地构建后 `_build/html/_static/academy-examples.zip` 存在、能解压、里面没有 `__pycache__`；页脚链接在首页与 1.4 都能点到。

## 验收标准

校验方：解压 zip 后在 5.1 环境里跑 `python examples/isaaclab-2.3/1.4-install/verify_install.py` 走通；抽 3 页核 `examples/` 路径在 zip 里存在；页脚两档宽度字号 ≥ 12 px；audit-all 无新问题。

## 附记

（实现 / 校验 session 写）
