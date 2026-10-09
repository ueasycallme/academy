# T-A.3 校验报告：官方资源导航

- 校验日期：2026-10-09
- 校验 session：isaac-academy-examine
- 范围：`docs/appendix/A.3-official-resources.md`

## 结论：通过

- **外部链接**：校验方从页面中提取出 **31** 个不同的 URL（实现方附记写 30，差别在计数口径，不影响结论），逐个 `curl -L` 检查：
  - 30 个第一次就返回 200；
  - NVIDIA 开发者论坛 Isaac Sim 板块（`forums.developer.nvidia.com/c/omniverse/simulation/69`）第一次超时，加长超时重试两次都是 200（2.1 s / 6.8 s），属于瞬时网络问题。
  - 以前对 curl 返回 403 的 Kit 手册（docs.omniverse.nvidia.com），这次返回 200。
- **bug 模板要点**：与 v2.3.2 `.github/ISSUE_TEMPLATE/bug.md` 一致。模板要求 Steps to reproduce、System Info（Commit、Isaac Sim Version、OS、GPU、CUDA、GPU Driver），Checklist 中两项是"no similar issue … (**required**)"与"not in running Isaac Sim itself"。页面的概括与此一致。
- **PhysX 版本**："链接为 5.6.1 版；Isaac Sim 5.1 内置的 SDK 具体版本本站未核对"，标注诚实。校验方在 pip 包的 `omni.physx-107.3.26` 扩展中找了一下，没有找到独立的 PhysX SDK 动态库或版本字符串（推测是静态链接进了插件），所以同样无法确认，维持"未核对"即可。
- **分组**：分组与 0.2 的分层一致；页面没有可复跑的命令或实测断言。
- `tools/check_head_build.sh --worktree`（-W）通过。
