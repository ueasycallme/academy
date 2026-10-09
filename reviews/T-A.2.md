# T-A.2 校验报告：常见错误信息索引

- 校验日期：2026-10-09
- 校验 session：isaac-academy-examine
- 范围：`docs/appendix/A.2-error-index.md`；顺带改动的 `docs/5-rl/5.6-observation-design.md` L71
- 核对脚本：`reviews/scripts/T-A.2-check-links.py`（解析构建后的 HTML，沿实际 href 找到目标小节，检查错误片段是否出现在该小节文字中）

## 结论：退回

链接、覆盖与排序都没问题。退回只为一行片段，它与真实报错对不上，读者用 Ctrl+F 或 grep 会搜不到。改一行即可，同样的写法也出现在 2.5。

## 问题表

| # | 位置 | 问题 | 依据 | 建议 | 严重度 |
|---|---|---|---|---|---|
| 1 | 表 1 第 1 行 `Accessed invalid expired prim`（同样的写法也在 2.5 L173） | USD 的原文在 expired 与 prim 之间插入了 Prim 的类型名，比如 `Accessed invalid expired 'Xform' prim </Robot>`。所以这个片段与日志并不逐字相同，只有无类型的 Prim 才对得上 | ① 用 usd-core 26.08 复现：`Usd.Stage.Open(p).GetPrimAtPath('/Robot')` 之后访问，报 `RuntimeError: Accessed invalid expired 'Xform' prim </Robot>`。② Isaac Sim 5.1 自带的 USD 24.05（`omni.usd.libs-1.0.1/bin/libusd_usd.so`）里，`Usd_ThrowExpiredPrimAccessError` 的描述格式串是 `%s%s%sprim %s<%s>`，前面是 `expired `、`'%s' `（类型名）两段，版本相同 | 片段改为 `Accessed invalid expired`（只取前缀），或写成 `Accessed invalid expired '…' prim`；2.5 L173 建议同步改为带类型名的原文 | 低 |

## 核对结果

**链接与片段**（全部 47 个站内链接）：

- 47 个链接都能解析到目标小节。只有一个链接没有锚点，就是指向 6.1.5 整页的那个，这是有意的。
- 表 1 的 32 个片段都出现在所链接小节的正文里。片段中用 ` / `、`…`、`...` 分开的各段分别检查。
- 第一列有两页时，第二页也用 grep 核对了，都讲到了该错误：
  - 7.1 有 DISPLAY；
  - 6.1.6 有 `__del__` 和 Multiple matches；
  - 3.4 有 Failed to find；
  - 4.4 有 gpu_* 参数；
  - 6.5.2 有显存不足；
  - 4.12 有 RuntimeError；
  - 6.1.2 有 Unresolved reference；
  - 4.6 有 out of the limits。
- 表 2 的 12 条症状，链接的小节标题都与症状对得上。

**1.9 的覆盖**：1.9 共 18 个三级标题，与表 1 中的 13 行、表 2 中的 5 行一一对应，没有遗漏。

**抽查原文**（12 行；对照 v2.3.2 源码、校验方以前的复跑日志，或现场复现）：

| 片段 | 原文出处 | 结果 |
|---|---|---|
| `The following joints have default positions out of the limits` | `assets/articulation/articulation.py` | 一致 |
| `Failed to find an articulation` / `a single articulation` | 同上 | 一致 |
| `Failed to create articulation at` | 同上；`t616/demo_unfix_root.log` | 一致 |
| `Multiple matches` | `utils/string.py`（测试中有）；`t47/r5.log` | 一致 |
| `Missing values detected` | `utils/configclass.py` | 一致 |
| `No runs present … match` | `isaaclab_tasks/utils/parse_cfg.py` L207：`No runs present in the directory: '…' match: '…'` | 一致（`…` 省略了路径） |
| `USD file not found at path` | `sim/spawners/from_files/from_files.py`；`t616/demo_missing_usd.log` | 一致 |
| `was not found in the URDF file` | `sim/converters/urdf_converter.py`；`t612/bad.log` | 一致 |
| `Can't find extension` | 校验方 T-2.7 复跑日志 `t27/prefail_3.log` | 一致 |
| `Unable to find the Isaac Sim directory` / `any Python executable at path` | `isaaclab.sh` | 一致 |
| `ValueError: [Config]: Incorrect type under namespace` | 校验方 T-5.6 复跑 `reviews/scripts/T-5.6-rerun.txt` L14 | 一致 |
| `Accessed invalid expired prim` | 现场复现 + USD 24.05 格式串 | **不一致**，见问题 1 |

`Patch buffer overflow` 来自实现方 6.5.2 的 16384 环境实测。校验方因主机内存限制没有跑 16384，未独立复现，但不阻塞。

**其他**：

- 表 1 按片段字母顺序（不区分大小写）排列，经核对无误。
- 5.6 L71 补的报错原文与校验方 T-5.6 的复跑日志逐字一致（日志在其后还有 `. Expected: <class 'NoneType'>, Received: <class 'int'>`）。
- 怎么用、维护规则、版本说明都在。
- `tools/check_head_build.sh --worktree`（-W）通过。

---

## 第二轮（2026-10-09）：通过

- 问题 1 已修：
  - 表 1 第 1 行改为 `Accessed invalid expired`；
  - 2.5 L173 改为原文 `RuntimeError: Accessed invalid expired 'Xform' prim </Robot>`，与校验方用 usd-core 复现的报错逐字一致。
- 重新构建后再跑 `T-A.2-check-links.py`：
  - 47 个链接都能解析到小节；
  - 32 个片段都能在所链接的小节里找到（新片段同样在 2.5 的"常见坑"里）。
- 表 1 仍为 32 行。
- 注：本轮构建出现 2 条警告，都在 `A.5-changelog.md`（L209、L230）。那是另一张卡正在写的页面，与本卡无关；本卡的页面没有警告。
