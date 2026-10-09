# T-A.3 校验报告：官方资源导航

- 校验日期：2026-10-09
- 校验 session：isaac-academy-examine
- 范围：`docs/appendix/A.3-official-resources.md`

## 结论：通过

- **外部链接**：校验方从页面中提取出 **31** 个不同的 URL（实现方附记写 30，差别在计数口径，不影响结论），逐个 `curl -L` 检查：
  - 30 个第一次就返回 200；
  - NVIDIA 开发者论坛 Isaac Sim 板块（`forums.developer.nvidia.com/c/omniverse/simulation/69`）在本机多次超时（30 s 上限），放宽到 60 s 后返回 200（一次用了 19.0 s，一次 2.0 s），说明是网络慢，链接本身有效。
  - Kit 手册（docs.omniverse.nvidia.com）返回 200，用时 6.2 s。
- **bug 模板要点**：与 v2.3.2 `.github/ISSUE_TEMPLATE/bug.md` 一致。模板要求 Steps to reproduce、System Info（Commit、Isaac Sim Version、OS、GPU、CUDA、GPU Driver），Checklist 中两项是"no similar issue … (**required**)"与"not in running Isaac Sim itself"。页面的概括与此一致。
- **PhysX 版本**："链接为 5.6.1 版；Isaac Sim 5.1 内置的 SDK 具体版本本站未核对"，标注诚实。校验方在 pip 包的 `omni.physx-107.3.26` 扩展中找了一下，没有找到独立的 PhysX SDK 动态库或版本字符串（推测是静态链接进了插件），所以同样无法确认，维持"未核对"即可。
- **分组**：页面说按 0.2 分层自上而下分组，校验方没有逐行比对。本页没有可复跑的命令或实测断言。
- `tools/check_head_build.sh --worktree`（-W）通过。
