#!/usr/bin/env python3
"""从 git log 生成附录 A.5（更新日志）的条目表。

    python3 tools/gen_changelog.py           # 重写 docs/appendix/A.5-changelog.md 中两个标记之间的表格
    python3 tools/gen_changelog.py --check   # 只比较，不写；不一致时退出码 1

规则（与 tasks/T-A.5.md 一致）：
- 只看 2026-09-30 起改动了 docs/**.md 的提交；不计 A.5 本身、不进站点的文件（conf.py 的 exclude_patterns），也不计占位页。
- 现在已不存在的页面（移走或删除）只写当时的标题并注明"页面已移除"，不加链接。
- 同一页面同一天的多次改动合并为一行。
- "新增"：这一版之前该页不存在或还是占位页；"版本核对"：提交属于 T-8.6 的后续微任务（T-8.6a、T-8.6b…）；其余为"修订"。
- 只改了脚本维护区块（如首页 progress 进度表）的改动不成行。
- 一句话：提交标题按"；"拆成任务段，每段只给其任务卡（tasks/T-<编号>.md）"产出"行列出的页面；产出行没写具体页面的段
  （如全站统一修改）给其余没有被认领的页面；没有任务编号的段不分配。去掉 T-/D- 编号和括号里的过程说明。
  一段也没分到的页面写"随《主页面标题》修订"，首页写"首页进度表更新"。个别历史提交可在 OVERRIDES 里手工改写。
- 任务编号放在最后一列。

合并流程（tools/merge_task.sh）先提交、再重生成、再 amend 进同一提交，所以页面里的表总是包含 HEAD 自己；
--check 直接与全部提交生成的结果比较（2026-10-09 设计 session 改，原先"提交前生成、检查时跳过最新提交"的做法
在"本次提交没改 A.5"时必然失败）。
"""

import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = "docs/appendix/A.5-changelog.md"
BEGIN, END = "<!-- changelog:begin -->", "<!-- changelog:end -->"
SINCE = "2026-09-30"
PLACEHOLDER_MARK = "placeholder: 由 tools/gen_placeholders.py"
# 不进站点的文件（docs/conf.py 的 exclude_patterns 里的 .md），不列入更新日志
EXCLUDED = {"docs/" + x for x in re.findall(r'"([^"]+\.md)"', re.search(r"^exclude_patterns\s*=\s*\[(.*)\]", (ROOT / "docs/conf.py").read_text(encoding="utf-8"), re.M).group(1))}
TASK_RE = re.compile(r"T-[0-9A-Z][0-9A-Za-z.\-]*[0-9A-Za-z]")


def is_placeholder(text: str) -> bool:
    """占位页：gen_placeholders 生成的（带标记），或更早手写的"待写，见 OUTLINE …"，或一级标题以"（待写）"结尾。"""
    return (PLACEHOLDER_MARK in text or "待写，见 OUTLINE" in text
            or re.search(r"^# .*（待写）\s*$", text, re.M) is not None)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def file_at(rev: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def docs_commits() -> list[dict]:
    """改动了 docs/**.md 的提交，新的在前。"""
    out = git("log", f"--since={SINCE} 00:00", "--date=short", "--format=%x00%H|%ad|%s", "--name-only", "--", "docs/")
    commits = []
    for block in out.split("\x00")[1:]:
        head, *files = block.strip("\n").split("\n")
        sha, date, subject = head.split("|", 2)
        md = [f for f in files if f.endswith(".md") and f.startswith("docs/") and not f.startswith("docs/_")]
        if md:
            commits.append({"sha": sha, "date": date, "subject": subject, "files": md})
    return commits


def page_title(path: str, rev: str) -> str:
    """取该提交时的页面标题：frontmatter 的 title，没有就用第一个一级标题。用提交时的版本，结果不随以后的改名变化。"""
    text = file_at(rev, path) or ""
    m = re.search(r"^title:\s*(.+)$", text, re.M) or re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else Path(path).stem


# 少数历史提交的标题是内部过程说明，读者看不懂，这里手工改写：(提交 sha 前缀, 页面) → 一句话
OVERRIDES = {
}
GENERIC_INDEX = "首页进度表更新"
# 括号里出现这些词的，是过程说明，整个括号删掉
PROCESS_WORDS = ("上一提交", "正文随", "同步", "site-sphinx", "截图", "自检")


def card_pages(task: str) -> list[str] | None:
    """任务卡"产出"行列出的 docs 页面（HEAD 上的卡）。卡不存在返回 None；产出行没有写具体页面返回 []。"""
    text = file_at("HEAD", f"tasks/{task}.md")  # 读已提交的卡，不读工作区，避免未提交的改动让 --check 漂移
    if text is None:
        return None
    m = re.search(r"^产出[:：](.*)$", text, re.M)
    return re.findall(r"`(docs/[^`]+\.md)`", m.group(1)) if m else []


def clean(text: str) -> str:
    """去掉任务编号、裁断编号和过程说明，只留读者能看懂的标题。"""
    text = re.sub(r"（[^（）]*）", lambda m: "" if TASK_RE.search(m.group(0)) or re.search(r"D-\d", m.group(0))
                  or any(w in m.group(0) for w in PROCESS_WORDS) else m.group(0), text)
    text = re.sub(rf"(?:按\s*)?D-\d+\s*", "", text)
    text = re.sub(rf"\[?{TASK_RE.pattern}\]?(?:\s*[、,，]\s*)?", "", text)
    text = re.sub(r"^[\s:：、,，]+|[\s:：、,，]+$", "", text)
    return text


def split_segments(subject: str) -> list[tuple[list[str], str]]:
    """按"；"拆成任务段：(段内的任务编号, 去掉编号后的标题)。"""
    return [(TASK_RE.findall(p), clean(p)) for p in re.split(r"[；;]", subject) if p.strip()]


def strip_generated(text: str) -> str:
    """去掉由脚本维护的区块（<!-- x:begin --> 到 <!-- x:end -->），用来判断一次改动是否只动了这些区块。"""
    return re.sub(r"<!-- (\w+):begin -->.*?<!-- \1:end -->", "", text, flags=re.S)


def notes_for(c: dict, pages: list[str]) -> dict[str, list[str]]:
    """一次提交里每个页面的一句话。每个任务段只给它的任务卡"产出"行列出的页面；
    产出行没写具体页面的段（如全站统一修改），给本次提交里其余所有页面；没有任务编号的段不分配。
    一个段也没分到的页面写"随 <主页面标题> 修订"（首页写"首页进度表更新"）。"""
    segs = split_segments(c["subject"])
    if not any(tasks for tasks, _ in segs):  # 整条提交没有任务编号：标题给所有页面
        return {f: [t for _, t in segs if t] for f in pages}
    owner: dict[str, list[str]] = {f: [] for f in pages}
    # 先分配产出行写了具体页面的段，再把"没写具体页面"的段给剩下没人认领的页面
    resolved = []
    for tasks, title in segs:
        cps = [card_pages(t) for t in tasks]
        explicit = set().union(*[set(cp) for cp in cps if cp]) & set(pages) if any(cps) else set()
        resolved.append((title, explicit, any(cp == [] for cp in cps)))
    claimed = set().union(*[e for _, e, _ in resolved]) if resolved else set()
    for title, explicit, open_ended in resolved:
        targets = explicit or ({f for f in pages if f not in claimed} if open_ended else set())
        for f in pages:
            if f in targets and title not in owner[f]:
                owner[f].append({"": "小修", "回链": "补回链"}.get(title, title))
    primary = next((f for f in pages if owner[f] and not f.endswith("/index.md")), None)
    for f in pages:
        if (c["sha"][:7], f) in OVERRIDES:
            owner[f] = [OVERRIDES[(c["sha"][:7], f)]]
        elif not owner[f]:
            if f == "docs/index.md":
                owner[f] = [GENERIC_INDEX]
            elif primary:
                owner[f] = [f"随《{page_title(primary, c['sha'])}》修订"]
            else:
                owner[f] = ["小修"]
    return owner


def build_rows(commits: list[dict]) -> list[tuple]:
    rows: "OrderedDict[tuple, dict]" = OrderedDict()
    for c in commits:  # 新的在前
        tasks = sorted(set(TASK_RE.findall(c["subject"])))
        pages = []
        kinds = {}
        for f in c["files"]:
            if f == PAGE or f in EXCLUDED:
                continue
            now = file_at(c["sha"], f)
            if now is None or is_placeholder(now):
                continue  # 删除，或这一版还是占位页
            before = file_at(c["sha"] + "^", f)
            if before is not None and strip_generated(before) == strip_generated(now):
                continue  # 只改了脚本维护的区块（如首页进度表）
            if before is None or is_placeholder(before):
                kinds[f] = "新增"
            elif any(re.match(r"T-8\.6[a-z]$", t) for t in tasks):
                kinds[f] = "版本核对"
            else:
                kinds[f] = "修订"
            pages.append(f)
        notes = notes_for(c, pages)
        for f in pages:
            kind = kinds[f]
            r = rows.setdefault((c["date"], f), {"kinds": [], "notes": [], "tasks": [], "sha": c["sha"]})  # sha：这一天最新的那次提交
            if kind not in r["kinds"]:
                r["kinds"].append(kind)
            for note in notes[f]:
                if note and (kind, note) not in r["notes"]:
                    r["notes"].append((kind, note))
            r["tasks"] += [t for t in tasks if t not in r["tasks"]]
    out = []
    for (date, f), r in rows.items():
        kind = "新增" if "新增" in r["kinds"] else ("修订" if "修订" in r["kinds"] else r["kinds"][0])
        # 同一天既有正文改动又有统一的版本核对时，只写正文改动的说明
        notes = [n for k, n in reversed(r["notes"]) if k != "版本核对" or kind == "版本核对"]
        generic = [n for n in notes if n.startswith("随") or n in (GENERIC_INDEX, "小修")]
        notes = [n for n in notes if n not in generic] or generic[:1]  # 有具体说明时不再拼通用说法
        title = page_title(f, r["sha"])
        # 后来被移走或删除的页面只写标题，不加链接（否则 -W 构建报 xref 警告）
        page = f"[{title}](../{f[len('docs/'):]})" if (ROOT / f).exists() else f"{title}（页面已移除）"
        out.append((date, page, kind, "；".join(notes), "、".join(sorted(r["tasks"]))))
    out.sort(key=lambda x: x[0], reverse=True)  # 日期倒序；同一天内按提交先后（新的在前），排序稳定
    return out


def render(rows: list[tuple]) -> str:
    lines = [BEGIN, "", "| 日期 | 页面 | 变化 | 一句话 | 任务 |", "|---|---|---|---|---|"]
    lines += [f"| {d} | {p} | {k} | {n.replace('|', '／')} | {t} |" for d, p, k, n, t in rows]
    lines += ["", END]
    return "\n".join(lines)


def main() -> int:
    page_path = ROOT / PAGE
    text = page_path.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        print(f"{PAGE} 中没有 {BEGIN} / {END} 标记", file=sys.stderr)
        return 1
    commits = docs_commits()
    # 设计 session 的 merge_task.sh 在提交后重生成并 amend，所以页面里的表总是包含 HEAD 自己；--check 直接与全部提交比较
    expected = render(build_rows(commits))
    current = text[text.index(BEGIN): text.index(END) + len(END)]
    if "--check" in sys.argv:
        if current != expected:
            print(f"{PAGE} 与 git log 生成的结果不一致，请运行 python3 tools/gen_changelog.py", file=sys.stderr)
            return 1
        print("更新日志与 git log 一致")
        return 0
    page_path.write_text(text.replace(current, expected), encoding="utf-8")
    print(f"已写入 {PAGE}：{expected.count(chr(10)) - 5} 行")
    return 0


if __name__ == "__main__":
    sys.exit(main())
