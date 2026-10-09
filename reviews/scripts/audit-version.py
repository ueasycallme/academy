"""T-AUDIT-01 检查 5：版本说明一致性。

A. 每个正式页（非占位页）的"## 版本说明"一节末尾有 T-8.6b 的固定句，且链接按目录层级正确；
   没有"## 版本说明"一节的正式页列出来。
B. 8.6 表 2：每行列出的页面，其 frontmatter `sources_checked` 与"最后核对"列一致；
   "其余 N 页"的 N 与实际一致，且这些页的版本说明确实写了"未核对"；表注里的总页数与实际一致。

用法：python3 reviews/scripts/audit-version.py [--repo DIR] [--ref HEAD]
"""
import argparse, os, re, subprocess, sys

FIXED = "3.0 的差异以 [8.6 版本追踪]({link}) 为准，本页最后核对的版本见该页核对状态表。"
PLACEHOLDER = ("<!-- placeholder:", "待写，见 OUTLINE")
DATE = r"20\d\d-\d\d-\d\d"


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout


def num_of(path):
    b = os.path.basename(path)
    m = re.match(r"([0-9A]+(?:\.\d+)*)-", b)
    return m.group(1) if m else None


def section(text, title="## 版本说明"):
    i = text.find("\n" + title)
    if i < 0:
        return None
    rest = text[i + 1 + len(title):]
    j = [k for k in (rest.find("\n## "), rest.find("\n[^")) if k >= 0]
    return rest[: min(j)] if j else rest


def expand(cell):
    """'0.1、0.2、3.1–3.5、A.2' -> {'0.1','0.2','3.1',...,'3.5','A.2'}"""
    out = set()
    # 链接只取链接文字的第一个词（编号），"1.5 安装 Isaac Sim 6.1 + …" 里的 6.1 不算
    cell = re.sub(r"\[([^\]\s]*)[^\]]*\]\([^)]*\)", r"\1", cell)
    for tok in re.split(r"[、，,\s]+", cell):
        m = re.match(r"^([0-9A])\.(\d+)[–-]\1?\.?(\d+)$", tok)
        if m:
            out |= {f"{m.group(1)}.{k}" for k in range(int(m.group(2)), int(m.group(3)) + 1)}
            continue
        m = re.match(r"^([0-9A]+(?:\.\d+)+)", tok)
        if m:
            out.add(m.group(1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="HEAD")
    a = ap.parse_args()
    files = [p for p in git(a.repo, "ls-tree", "-r", "--name-only", a.ref, "docs").splitlines()
             if p.endswith(".md") and "/_build/" not in p]
    pages = {}
    for p in files:
        t = git(a.repo, "show", f"{a.ref}:{p}")
        if any(m in t for m in PLACEHOLDER):
            continue
        fm = re.search(r"^---\n(.*?)\n---", t, re.S)
        sc = re.search(r"sources_checked:\s*\"?(" + DATE + ")", fm.group(1)) if fm else None
        pages[p] = dict(text=t, num=num_of(p), sources_checked=sc.group(1) if sc else None, ver=section(t))
    issues = []
    # A
    n_with = n_fixed = 0
    for p, d in sorted(pages.items()):
        rel = p[5:]
        if d["ver"] is None:
            if os.path.basename(p) not in ("index.md",) and "MIGRATION-NOTES" not in p and "8.6-version" not in p:
                issues.append(("一般", rel, "没有“## 版本说明”一节", ""))
            continue
        n_with += 1
        if rel.startswith("8-frontier/8.6") or rel.startswith("0-map/_"):
            continue
        link = os.path.relpath("docs/8-frontier/8.6-version-tracking.md", os.path.dirname(p))
        want = FIXED.format(link=link)
        lines = [l.strip() for l in d["ver"].strip().splitlines() if l.strip()]
        if want in d["ver"]:
            n_fixed += 1
            if lines[-1] != want:
                issues.append(("建议", rel, "固定句不在版本说明的最后一行", f"最后一行：{lines[-1][:40]}"))
        elif "3.0 的差异以" in d["ver"]:
            issues.append(("一般", rel, "固定句写法或链接与模板不一致", lines[-1][:80]))
        else:
            if rel.startswith("appendix/"):
                issues.append(("建议", rel, "版本说明缺 T-8.6b 固定句", "附录页，T-8.6b 按范围未覆盖"))
            else:
                issues.append(("一般", rel, "版本说明缺 T-8.6b 固定句", ""))
    # B
    t86 = pages.get("docs/8-frontier/8.6-version-tracking.md", {}).get("text", "")
    sec = t86[t86.find("## 本站核对状态"):]
    rows = [r for r in sec.splitlines() if r.startswith("| ") and not r.startswith("| 页面") and not r.startswith("|---")]
    # 表 2 到"其余 N 页"那一行为止（按第一格判断；别的行的日期格里也会出现"其余"二字）
    rows = rows[: next((i for i, r in enumerate(rows) if r.strip("| ").startswith("其余")), len(rows)) + 1]
    by_num = {d["num"]: p for p, d in pages.items() if d["num"]}
    listed = set()
    rest_n = None
    n_cmp = 0
    for r in rows:
        cells = [c.strip() for c in r.strip("|").split("|")]
        if cells[0].startswith("其余"):
            rest_n = int(re.search(r"\d+", cells[0]).group())
            continue
        nums = expand(cells[0])
        listed |= nums
        when = cells[3]
        for n in sorted(nums):
            p = by_num.get(n)
            if not p:
                issues.append(("一般", "8-frontier/8.6", f"表 2 列了 {n}，但找不到这个正式页", r[:60]))
                continue
            sc = pages[p]["sources_checked"]
            m = re.search(re.escape(n) + r"[^；。，]*?为 (" + DATE + ")", when) or \
                re.search(r"(?:、|^|：)[^：]*?" + re.escape(n) + r"[^0-9][^；。]*?为 (" + DATE + ")", when)
            exp = m.group(1) if m else (re.search(r"其余为 (" + DATE + ")", when) or re.search("(" + DATE + ")", when) or [None, None])[1]
            n_cmp += 1
            if exp and sc != exp:
                issues.append(("一般", p[5:], f"8.6 表 2 写最后核对 {exp}，页面 sources_checked 为 {sc}", ""))
    note = re.search(r"共 (\d+) 页.*?逐页归类 (\d+) 页", sec)
    excluded = {"3.11", "A.5"}
    rest = [p for p, d in pages.items() if d["ver"] is not None and d["num"] and d["num"] not in listed
            and d["num"] not in excluded and "8.6-version" not in p]
    not_unver = [p[5:] for p in rest if "未核对" not in pages[p]["ver"]]
    if rest_n is None:
        issues.append(("一般", "8-frontier/8.6", "表 2 里找不到“其余 N 页”一行，脚本没能核对", ""))
    elif rest_n != len(rest):
        issues.append(("一般", "8-frontier/8.6", f"表 2“其余 {rest_n} 页”，实际 {len(rest)} 页", ""))
    for p in not_unver:
        issues.append(("一般", p, "归入 8.6 表 2“其余”行（未核对），但版本说明里没有“未核对”", ""))
    if note and int(note.group(1)) != n_with:
        issues.append(("一般", "8-frontier/8.6", f"表注写含版本说明的页面 {note.group(1)} 页，实际 {n_with} 页", ""))
    for sev, where, what, extra in issues:
        print(f"{sev}\t{where}\t{what}\t{extra}")
    print(f"[version] 正式页 {len(pages)}；含版本说明 {n_with}；有固定句 {n_fixed}；"
          f"8.6 表 2 逐页列出 {len(listed)} 页（日期逐页比对 {n_cmp} 页）+ 其余 {len(rest)} 页；问题 {len(issues)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
