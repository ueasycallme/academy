---
title: 常见错误信息索引
updated: 2026-10-09
sources_checked: 2026-10-09
---

# 常见错误信息索引

**怎么用这一页**：先在自己的日志里找到第一个报错，取一段不含路径、数字的关键片段，再在本页用 Ctrl+F 搜。日志在哪、怎么让警告不淹没报错，见 [7.3 的"日志在哪"](../7-infra/7.3-debugging.md#日志在哪)。一个报错后面常常跟着一串连带的报错，**先看第一个**。

## 有错误信息的

这一节回答：报了这句，是什么原因，去哪一页看？

| 错误片段 | 阶段 | 一句话原因 | 详见 |
|---|---|---|---|
| `Accessed invalid expired` | 资产 | Stage 被释放后还在用它的 Prim | [2.5](../2-usd-kit/2.5-usd-python.md#常见坑) |
| `Can't execute command: "MJCFCreateImportConfig"` | 资产导入 | MJCF 导入扩展没有启用 | [3.5](../3-isaacsim/3.5-urdf-mjcf-import.md#mjcf) |
| `Can't find extension` | 启动 | 扩展不在搜索路径里，或这个名字刚启用失败过 | [2.7](../2-usd-kit/2.7-extensions.md#常见坑) |
| `dependency: ... can't be satisfied` | 启动 | extension.toml 的依赖写成了不是扩展的模块名 | [2.7](../2-usd-kit/2.7-extensions.md#常见坑) |
| `DISPLAY environment variable is not set / GLFW initialization failed` | 启动 | 没有显示器；会自动转无窗口，但仍加载带界面的体验文件 | [1.9、7.1](../1-env/1.9-install-troubleshooting.md#display-environment-variable-is-not-set-running-in-headless-mode--glfw-initialization-failed) |
| `Do you accept the EULA? / EOFError: EOF when reading a line` | 启动 | 首次启动要确认 EULA；非交互环境设 OMNI_KIT_ACCEPT_EULA | [1.9](../1-env/1.9-install-troubleshooting.md#do-you-accept-the-eula-yesno-卡住或-eoferror-eof-when-reading-a-line) |
| `ERROR: No matching distribution found for isaacsim==5.1.0` | 安装 | Python 版本或平台不满足 pip 包要求 | [1.9](../1-env/1.9-install-troubleshooting.md#error-no-matching-distribution-found-for-isaacsim510) |
| `Exception ignored in: ... __del__` | 退出 | 前面已经出错，退出时析构函数又报一次；先看第一个报错 | [1.9、6.1.6](../1-env/1.9-install-troubleshooting.md#exception-ignored-in--__del__--typeerror-nonetype-object-is-not-callable) |
| `Failed to find an articulation / Failed to find a single articulation` | 资产 | 没有或有多个 ArticulationRootAPI | [2.4、3.4](../2-usd-kit/2.4-physics-schema.md#常见坑) |
| `FileNotFoundError: USD file not found at path` | 资产 | 还没转换资产，或 GALBOT_GENERATED_DIR 指错 | [6.1.6](../6-galbot/1-asset/6.1.6-articulation-cfg.md#常见坑) |
| `GetCompositionErrors` | 资产 | Isaac Sim 5.1 自带的 USD 24.05 没有这个方法 | [2.5](../2-usd-kit/2.5-usd-python.md#常见坑) |
| `GLIBC` | 安装 | 系统 glibc 低于 2.35（如 Ubuntu 20.04） | [1.9](../1-env/1.9-install-troubleshooting.md#glibc-版本低于-235ubuntu-2004-等) |
| `gymnasium.error.NameNotFound` | 启动 | 任务的注册代码没执行（没 import 任务包） | [4.15](../4-isaaclab/4.15-task-registration.md#常见坑) |
| `No module named 'isaaclab'` | 安装 | Isaac Lab 没有装进当前环境 | [1.9](../1-env/1.9-install-troubleshooting.md#modulenotfounderror-no-module-named-isaaclab) |
| `No module named 'isaacsim.core'` | 启动 | 在启动 SimulationApp 之前导入了 isaacsim.* 子模块 | [3.2](../3-isaacsim/3.2-simulation-app.md#standalone-脚本的骨架) |
| `No module named 'omni'` | 启动 | 在启动 SimulationApp 之前导入了 omni / 旧名模块 | [1.9](../1-env/1.9-install-troubleshooting.md#modulenotfounderror-no-module-named-omni) |
| `No module named 'pkg_resources'` | 安装 | 构建 flatdict 时 setuptools 版本不合适 | [1.9](../1-env/1.9-install-troubleshooting.md#modulenotfounderror-no-module-named-pkg_resources构建-flatdict-时) |
| `No module named 'pxr'` | 启动 | pip 版 Isaac Sim 里 pxr 要在 SimulationApp 启动后才能导入 | [2.5](../2-usd-kit/2.5-usd-python.md#两种运行环境) |
| `No runs present … match` | 回放 | --load_run 从目录名开头匹配，而目录名以日期开头 | [6.6.1](../6-galbot/6-eval/6.6.1-play-replay.md#常见坑) |
| `Patch buffer overflow` | 训练 | 环境数过多（16384），接着显存不足 | [6.5.2](../6-galbot/5-train/6.5.2-hyperparameters.md#12-gb-显卡选多少个环境) |
| `PhysX error: the application need to increase the PxgDynamicsMemoryConfig::` | 训练 | GPU 物理缓冲区不够，调大 PhysxCfg 的 gpu_* 参数 | [1.9、4.4](../1-env/1.9-install-troubleshooting.md#physx-error-the-application-need-to-increase-the-pxgdynamicsmemoryconfigfoundlostpairscapacity) |
| `RuntimeError: Failed to create articulation at` | 资产 | 固定根的资产用 fix_root_link=False 关掉了根关节 | [6.1.6](../6-galbot/1-asset/6.1.6-articulation-cfg.md#变体replace-派生) |
| `RuntimeError（randomize_rigid_body_scale / 纹理随机化）` | 场景 | 运行中调用了只能在仿真开始前用的随机化，或没关 replicate_physics | [4.5、4.12](../4-isaaclab/4.5-interactive-scene.md#常见坑) |
| `torch.OutOfMemoryError: CUDA out of memory` | 训练 | 显存不够：减少环境数或关掉渲染 | [1.9、6.5.2](../1-env/1.9-install-troubleshooting.md#torchoutofmemoryerror-cuda-out-of-memory) |
| `TypeError: Missing values detected` | 配置 | configclass 里有 MISSING 字段没有填 | [4.3](../4-isaaclab/4.3-configclass.md#missing必须由使用者填写的字段) |
| `Unable to find any Python executable at path` | 安装 | isaaclab.sh 找不到解释器：没激活环境，也没有 _isaac_sim 链接 | [1.9](../1-env/1.9-install-troubleshooting.md#error-unable-to-find-any-python-executable-at-path-_isaac_simpythonsh) |
| `Unable to find the Isaac Sim directory` | 安装 | isaaclab.sh 找不到 Isaac Sim：pip 包没装或环境没激活 | [1.9](../1-env/1.9-install-troubleshooting.md#error-unable-to-find-the-isaac-sim-directory) |
| `Unresolved reference prim path` | 资产 | 被引用的文件没有 defaultPrim；或 URDF 里某个连杆没有视觉网格（后者无害） | [2.2、6.1.2](../2-usd-kit/2.2-usd-concepts.md#常见坑) |
| `ValueError: [Config]: Incorrect type under namespace` | 训练 | 用 Hydra 覆盖观测组的 history_length（默认 None），类型不符 | [5.6](../5-rl/5.6-observation-design.md#历史帧) |
| `ValueError: Multiple matches` | 配置 | 同一执行器组（或同一字典）里两个正则匹配到同一关节 | [4.7、6.1.6](../4-isaaclab/4.7-actuators.md#常见坑) |
| `ValueError: The following joints have default positions out of the limits` | 资产 | init_state 的关节默认值超出限位 | [3.4、4.6](../3-isaacsim/3.4-articulation.md#常见坑) |
| `ValueError: The joint name ... was not found in the URDF file` | 资产导入 | 转换器增益字典里的键没有匹配到任何关节；进程返回码仍为 0 | [6.1.2](../6-galbot/1-asset/6.1.2-import-urdf.md#常见坑) |

*表 1：按错误片段的字母顺序排列。"详见"一栏指向本站第一次讲这个错误的页面与小节；1.9 的条目同时是该页的小节标题。*

## 没有错误信息的症状

这一节回答：没报错，但就是不对劲，从哪里查起？

| 症状 | 先看 |
|---|---|
| 第一次启动很久没有输出，像卡死 | [1.9](../1-env/1.9-install-troubleshooting.md#第一次启动很久没有输出像是卡死)：首次启动在编译着色器 |
| 脚本跑完后退不出，`close()` 不返回 | [1.9](../1-env/1.9-install-troubleshooting.md#自己写的脚本退出时卡住simulation_appclose-不返回)、[3.2 的"正常退出"](../3-isaacsim/3.2-simulation-app.md#正常退出) |
| `timeout` 或 `kill` 结束不了进程 | [1.9](../1-env/1.9-install-troubleshooting.md#timeout-或-kill-结束不了-isaac-sim-进程) |
| 黑屏、启动即崩溃 | [1.9](../1-env/1.9-install-troubleshooting.md#驱动过旧启动失败黑屏或崩溃)：驱动过旧 |
| 装了 ROS 2 的机器上导入出错 | [1.9](../1-env/1.9-install-troubleshooting.md#装了-ros-2-的机器上导入时版本冲突或报奇怪的错误) |
| 离线环境首次启动下载扩展失败 | [1.9](../1-env/1.9-install-troubleshooting.md#首次启动时下载扩展失败离线环境没装-extscache) |
| 训练中出现 NaN | [5.8 的"NaN 专项"](../5-rl/5.8-training-debug.md#nan-专项)；轮子压进地面导致的 NaN 见 [3.5](../3-isaacsim/3.5-urdf-mjcf-import.md#常见坑) |
| 机器人塌下去、姿态不对 | [7.3 的"一套顺序"](../7-infra/7.3-debugging.md#一套顺序)：先零动作看能否站住；驱动参数见 [6.1.5](../6-galbot/1-asset/6.1.5-joint-drive-tuning.md) |
| 显存不够、环境数上不去 | [6.5.2 的"12 GB 显卡选多少个环境"](../6-galbot/5-train/6.5.2-hyperparameters.md#12-gb-显卡选多少个环境) |
| 进程返回码是 0，结果却不对 | Isaac Sim 进程的退出码总是 0（[2.5](../2-usd-kit/2.5-usd-python.md#常见坑)）；URDF 转换失败时返回码也是 0（[6.1.2](../6-galbot/1-asset/6.1.2-import-urdf.md#常见坑)） |
| 迁移到 3.0 后姿态悄悄错了 | 四元数顺序 WXYZ → XYZW（[8.4](../8-frontier/8.4-migration-23-30.md#四元数-wxyz--xyzw)） |
| 训练好了，回放却不对 | [6.6.1 的排查表](../6-galbot/6-eval/6.6.1-play-replay.md#回放与训练表现不一致时) |

*表 2：没有错误信息的症状。*

## 维护规则

正文页新写的"常见坑"如果含有错误信息，写页的会话同时在表 1 加一行：错误片段（不含路径与数字，放进行内代码）、阶段、一句话原因、链接到讲它的页面与小节。表 1 按片段的字母顺序插入。只在附录里出现、正文没讲过的错误不收；先在正文写好，再来加索引。

## 延伸阅读

- 安装与启动的完整排障：[1.9 安装排障手册](../1-env/1.9-install-troubleshooting.md)
- 训练不收敛的排查：[5.8](../5-rl/5.8-training-debug.md)；调试手段：[7.3](../7-infra/7.3-debugging.md)

## 版本说明

本页收录的错误信息来自 Isaac Sim 5.1.0 + Isaac Lab 2.3.2。3.0 的报错可能不同，见 [8.6 版本追踪](../8-frontier/8.6-version-tracking.md)。
