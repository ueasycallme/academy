#!/usr/bin/env python3
# Copyright (c) 2026, Isaac Academy.
# SPDX-License-Identifier: BSD-3-Clause
"""从 OUTLINE.md 统一生成占位页，并统计建设进度（T-SITE-12）。

占位页的识别：正文含生成标记 PLACEHOLDER_MARK，或旧的"待写，见 OUTLINE"。
正式页（不是占位页）不会被改动。

    python3 tools/gen_placeholders.py                 # 重写全部占位页，并刷新首页的"建设进度"表
    python3 tools/gen_placeholders.py --check         # 只检查：每个占位页都与现在生成的内容一致；不一致时返回 1

"现在可以读什么"会列出同一部分已完成的页面。所以某页从占位变为正式页之后，同部分其他占位页的列表就过时了，
--check 会报告，重新运行一次本脚本即可。首页的进度表也由本脚本写入（两个标记之间），不在 --check 范围内。
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTLINE = ROOT / "OUTLINE.md"
INDEX = DOCS / "index.md"
PLACEHOLDER_MARK = "<!-- placeholder: 由 tools/gen_placeholders.py 生成，请勿手改 -->"
OLD_MARK = "待写，见 OUTLINE"
PROGRESS_BEGIN = "<!-- progress:begin -->"
PROGRESS_END = "<!-- progress:end -->"
PRIORITY_TEXT = "P1 是黄金路径与核心概念，最先编写；P2 是第二阶段；P3 是长期补充。"


def parse_outline():
    """返回 [(编号, 标题, 优先级, 说明, 部分名)]。表格行的列数不统一，优先级列按 P1/P2/P3 识别。"""
    entries, part = [], ""
    for line in OUTLINE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (第 \d+ 部分 · .+|附录)\s*$", line)
        if m:
            part = m.group(1)
            continue
        if not re.match(r"^\| *([0-9]+(\.[0-9]+)+|A\.[0-9]+) *\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        prio_idx = next((i for i, c in enumerate(cells) if re.fullmatch(r"P[1-3]", c)), None)
        if prio_idx is None:
            continue
        desc = cells[prio_idx + 1] if prio_idx + 1 < len(cells) else ""
        desc = re.sub(r"\s*←\s*(.+)$", r"（建议先读 \1）", desc)  # 大纲里的"← 4.8"表示前置页面
        entries.append((cells[0], cells[1], cells[prio_idx], desc, part))
    return entries


def page_files():
    """编号 → 页面文件（docs 下以"编号-"开头的 .md，跳过 _build）。"""
    found = {}
    for p in DOCS.rglob("*.md"):
        if "_build" in p.parts:
            continue
        m = re.match(r"^([0-9]+(?:\.[0-9]+)+|A\.[0-9]+)-", p.name)
        if m:
            found[m.group(1)] = p
    return found


def is_placeholder(text: str) -> bool:
    return PLACEHOLDER_MARK in text or OLD_MARK in text


def split_frontmatter(text: str):
    if text.startswith("---\n"):
        end = text.index("\n---\n", 4) + 5
        return text[:end], text[end:]
    return "", text


def page_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    m = re.search(r"^title:\s*(.+)$", fm, re.M)
    if m:
        return m.group(1).strip().strip('"')
    m = re.search(r"^# (.+)$", body, re.M)
    return m.group(1).replace("（待写）", "").strip() if m else path.stem


def rel(src: Path, dst: Path) -> str:
    return os.path.relpath(dst, src.parent).replace(os.sep, "/")


def section_key(num: str) -> str:
    """同一部分的判定：第 6 部分按小节（6.1、6.2…），其余按部分（0、1…、A）。"""
    parts = num.split(".")
    return ".".join(parts[:2]) if parts[0] == "6" else parts[0]


def render(path: Path, num: str, title: str, prio: str, desc: str, done: list) -> str:
    fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    lines = [
        f"# {title}（待写）",
        "",
        PLACEHOLDER_MARK,
        "",
        ":::{note}",
        "本页尚未编写。下面是它的计划内容，以及现在可以先读的页面。",
        ":::",
        "",
        "## 计划内容",
        "",
        desc or "大纲中只列了标题，内容待定。",
        "",
        "## 优先级",
        "",
        f"本页优先级为 **{prio}**。{PRIORITY_TEXT}",
        "",
        "## 现在可以读什么",
        "",
        f"- [0.7 学习路线图]({rel(path, DOCS / '0-map' / '0.7-learning-paths.md')})：按目标挑选已完成的页面",
    ]
    if done:
        lines += [f"- [{n} {t}]({rel(path, p)})" for n, t, p in done]
    else:
        lines.append("- 本部分暂时没有已完成的页面")
    lines += ["", "## 进度", "", "全站的建设进度见首页的 {ref}`建设进度 <build-progress>`。", ""]
    return fm + "\n" + "\n".join(lines)


def build():
    entries = parse_outline()
    files = page_files()
    status = {}  # 编号 → (路径, 是否占位)
    for num, *_ in entries:
        if num in files:
            status[num] = (files[num], is_placeholder(files[num].read_text(encoding="utf-8")))
    pages = {}
    for num, title, prio, desc, part in entries:
        if num not in status or not status[num][1]:
            continue
        path = status[num][0]
        key = section_key(num)
        done = [(n, page_title(status[n][0]), status[n][0]) for n, *_ in entries
                if n in status and not status[n][1] and section_key(n) == key]
        pages[path] = render(path, num, page_title(path), prio, desc, done)
    return entries, status, pages


def progress_table(entries, status) -> str:
    rows, totals = {}, {}
    order = []
    for num, _, prio, _, part in entries:
        if num not in status:
            continue
        if part not in rows:
            rows[part] = {p: [0, 0] for p in ("P1", "P2", "P3")}
            order.append(part)
        rows[part][prio][1] += 1
        rows[part][prio][0] += 0 if status[num][1] else 1
        totals.setdefault(prio, [0, 0])
        totals[prio][1] += 1
        totals[prio][0] += 0 if status[num][1] else 1
    fmt = lambda d, t: f"{d} / {t}" if t else "—"
    out = ["| 部分 | P1 已完成 / 总数 | P2 | P3 |", "|---|---|---|---|"]
    for part in order:
        r = rows[part]
        out.append(f"| {part} | {fmt(*r['P1'])} | {fmt(*r['P2'])} | {fmt(*r['P3'])} |")
    t = {p: totals.get(p, [0, 0]) for p in ("P1", "P2", "P3")}
    out.append(f"| **合计** | **{fmt(*t['P1'])}** | **{fmt(*t['P2'])}** | **{fmt(*t['P3'])}** |")
    out += ["", f"*由 `tools/gen_placeholders.py` 统计，生成于 {datetime.date.today().isoformat()}。"
                f'{PRIORITY_TEXT}未完成的页面在目录里标有"（待写）"。*']
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="只检查占位页是否与生成内容一致")
    args = parser.parse_args()
    entries, status, pages = build()
    if args.check:
        bad = [p for p, text in pages.items() if p.read_text(encoding="utf-8") != text]
        for p in bad:
            print(f"占位页与模板不一致（运行 tools/gen_placeholders.py 重新生成）：{p.relative_to(ROOT)}")
        print(f"占位页 {len(pages)} 个，不一致 {len(bad)} 个")
        sys.exit(1 if bad else 0)
    for p, text in pages.items():
        p.write_text(text, encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    if PROGRESS_BEGIN in index:
        i, j = index.index(PROGRESS_BEGIN) + len(PROGRESS_BEGIN), index.index(PROGRESS_END)
        index = index[:i] + "\n" + progress_table(entries, status) + "\n" + index[j:]
        INDEX.write_text(index, encoding="utf-8")
        print("已刷新首页的建设进度表")
    else:
        print(f"首页没有 {PROGRESS_BEGIN} 标记，未写进度表")
    missing = [n for n, *_ in entries if n not in status]
    print(f"已重写占位页 {len(pages)} 个；OUTLINE 中没有对应页面文件的条目：{missing or '无'}")


if __name__ == "__main__":
    main()
