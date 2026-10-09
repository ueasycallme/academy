# 1.8 开发工具链：VS Code 配置示例

对应页面：`docs/1-env/1.8-dev-tools.md`。

验证版本：Isaac Sim 5.1.0（pip）+ Isaac Lab 2.3.2，debugpy 1.8.22，pyright 1.1.414；本机 VS Code 1.138.0；2026-10-09。

## 文件

- `.vscode/settings.json`：解释器与 `python.analysis.extraPaths`。把 `<ISAACLAB>`、`<VENV>` 换成本机路径；`extscache` 下两个目录的版本号按本机实际目录改。
- `.vscode/launch.json`：两项调试配置——直接启动主线项目的 `zero_agent.py`（headless、2 个环境），以及 attach 到 `debug_step.py --debugpy`（7.3）。

用法：把 `.vscode/` 复制到主线项目根目录 `examples/isaaclab-2.3/6-galbot-project/`，在 VS Code 里打开这个目录。需要 VS Code 的 Python 扩展（含 Pylance 与 Python Debugger）；`attach` 还要在环境里 `pip install debugpy`。

## 验证方式（重要）

- 两项调试配置：用 debugpy 自带的调试适配器（`python -m debugpy.adapter`，VS Code 的 Python Debugger 扩展用的也是它）按文件里的字段发 launch / attach 请求，在 Isaac Lab 源码 `manager_based_rl_env.py` 的 `_reset_idx` 打断点，确认能停住并取到调用栈。**没有在 VS Code 界面里操作过。**
- `extraPaths`：用 pyright CLI 检查导入能否解析（Pylance 的类型检查基于 pyright，界面内未验证）。

实测输出见页面。
