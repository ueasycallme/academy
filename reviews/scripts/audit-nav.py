"""T-AUDIT-02 检查 B-8：导航与标题对齐。

A. OUTLINE.md 每行（编号 | 页面 | …）↔ 该编号页面的 frontmatter `title` ↔ 页面 H1，三处文字不一致的列出
   （比较前去掉反引号、空白；只差这两项的另列"建议"）。OUTLINE 有、站点没有的编号，反之亦然，列"一般"。
B. toctree：每个正式页恰好出现在一个 toctree 里；同一 toctree 内按编号升序；toctree 条目或页面标题里不应再有"（待写）"。
   docs/index.md 的 toctree caption ↔ OUTLINE 的"## 第 N 部分 · …"标题；第 6 部分各小节 index 页的 title ↔ OUTLINE 的"### ①…"。
C. 各 index 页（docs/index.md 除进度表外、第 6 部分 7 个小节页）正文里指向正式页的链接：链接文字若含编号与标题，
   标题要与目标页 title 一致。第 6 部分小节页没有一句话简介的列"建议"。

用法：python3 reviews/scripts/audit-nav.py [--repo DIR] [--ref HEAD]
"""
import argparse, collections, os, re, subprocess, sys

PLACEHOLDER = ("<!-- placeholder:", "待写，见 OUTLINE")


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout


def norm(s):
    return re.sub(r"\s+", "", s.replace("`", "")).strip()


def numkey(n):
    return [(0, int(x)) if x.isdigit() else (1, x) for x in re.split(r"\.", n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="HEAD")
    a = ap.parse_args()
    outline = git(a.repo, "show", f"{a.ref}:OUTLINE.md")
    files = [f for f in git(a.repo, "ls-tree", "-r", "--name-only", a.ref, "docs").splitlines() if f.endswith(".md") and "/_build/" not in f]
    texts = {f: git(a.repo, "show", f"{a.ref}:{f}") for f in files}
    issues = []
    # OUTLINE
    out_rows, parts, subs = {}, {}, {}
    part = None
    for line in outline.splitlines():
        m = re.match(r"^## (第 \d+ 部分 · .+|附录)$", line)
        if m:
            part = m.group(1)
            pm = re.match(r"第 (\d+) 部分", part)
            parts[pm.group(1) if pm else "A"] = part
            continue
        m = re.match(r"^### ([①-⑦] .+)$", line)
        if m:
            subs[m.group(1)[0]] = m.group(1)
            continue
        m = re.match(r"^\| ((?:\d|A)(?:\.\d+)+) \| ([^|]+) \|", line)
        if m:
            out_rows[m.group(1)] = m.group(2).strip()
    # 站点页面
    pages = {}
    for f, t in texts.items():
        m = re.match(r"([0-9A]+(?:\.\d+)+)-", os.path.basename(f))
        if not m:
            continue
        fm = re.search(r"^---\n(.*?)\n---", t, re.S)
        title = re.search(r"^title:\s*(.+)$", fm.group(1), re.M).group(1).strip().strip('"') if fm else ""
        h1 = re.search(r"^# (.+)$", t, re.M)
        pages[m.group(1)] = dict(file=f, title=title, h1=h1.group(1).strip() if h1 else "", placeholder=any(p in t for p in PLACEHOLDER))
    n_cmp = 0
    for n in sorted(set(out_rows) | set(pages), key=numkey):
        if n not in pages:
            issues.append(("一般", "OUTLINE", f"{n}「{out_rows[n]}」在站点里没有页面", ""))
            continue
        if n not in out_rows:
            issues.append(("一般", pages[n]["file"][5:], f"{n} 不在 OUTLINE 里", ""))
            continue
        n_cmp += 1
        o, t, h = out_rows[n], pages[n]["title"], pages[n]["h1"]
        if norm(t) != norm(h):
            issues.append(("一般", pages[n]["file"][5:], "frontmatter title 与 H1 不一致", f"title「{t}」/ H1「{h}」"))
        if norm(o) != norm(t):
            issues.append(("人工看", pages[n]["file"][5:], "OUTLINE 标题与页面 title 不一致", f"OUTLINE「{o}」/ title「{t}」"))
        if "待写" in t or "待写" in h:
            issues.append(("一般", pages[n]["file"][5:], "标题里还有“待写”", t))
        if pages[n]["placeholder"]:
            issues.append(("一般", pages[n]["file"][5:], "仍是占位页", ""))
    # toctree
    seen = collections.Counter()
    for f, t in texts.items():
        for blk in re.findall(r"```\{toctree\}\n(.*?)```", t, re.S):
            cap = re.search(r"^:caption:\s*(.+)$", blk, re.M)
            entries = [e.strip() for e in blk.splitlines() if e.strip() and not e.strip().startswith(":")]
            nums = []
            for e in entries:
                path = os.path.normpath(os.path.join(os.path.dirname(f), e)) + ".md"
                seen[path] += 1
                if "待写" in e:
                    issues.append(("一般", f[5:], "toctree 条目带“待写”", e))
                m = re.match(r"([0-9A]+(?:\.\d+)+)-", os.path.basename(e))
                if m:
                    nums.append(m.group(1))
                if path not in texts:
                    issues.append(("一般", f[5:], f"toctree 条目 {e} 找不到文件", ""))
            if nums != sorted(nums, key=numkey):
                issues.append(("一般", f[5:], "toctree 条目没有按编号排序", " ".join(nums)))
            if cap and f == "docs/index.md":
                c = cap.group(1).strip()
                pm = re.match(r"第 (\d+) 部分", c)
                key = pm.group(1) if pm else ("A" if c == "附录" else None)
                if key in parts and norm(parts[key]) != norm(c):
                    issues.append(("建议", "index.md", "toctree caption 与 OUTLINE 部分标题不同", f"caption「{c}」/ OUTLINE「{parts[key]}」"))
    for n, d in pages.items():
        if seen[d["file"]] != 1:
            issues.append(("一般", d["file"][5:], f"出现在 {seen[d['file']]} 个 toctree 里（应为 1）", ""))
    # 第 6 部分小节 index
    for f, t in sorted(texts.items()):
        if not re.match(r"docs/6-galbot/\d-[\w-]+/index\.md$", f):
            continue
        title = re.search(r"^title:\s*(.+)$", t, re.M).group(1).strip()
        sub = subs.get(title[0])
        if sub and norm(sub) != norm(title):
            issues.append(("建议", f[5:], "小节 index 标题与 OUTLINE 的 ### 标题不同", f"「{title}」/「{sub}」"))
        body = t.split("\n# ", 1)[1].split("\n", 1)[1] if "\n# " in t else ""
        prose = re.sub(r"```.*?```", "", body, flags=re.S).strip()
        if not prose:
            issues.append(("建议", f[5:], "小节 index 页没有一句话简介（只有 toctree）", ""))
    # C：index 页里的链接文字
    by_file = {d["file"]: (n, d["title"]) for n, d in pages.items()}
    for f, t in texts.items():
        if not (f == "docs/index.md" or f.endswith("/index.md")):
            continue
        t2 = re.sub(r"<!-- progress:begin -->.*?<!-- progress:end -->", "", t, flags=re.S)
        for m in re.finditer(r"\[([^\]]+)\]\(([^)#]+\.md)(?:#[^)]*)?\)", t2):
            path = os.path.normpath(os.path.join(os.path.dirname(f), m.group(2)))
            if path not in by_file:
                continue
            n, title = by_file[path]
            txt = re.sub(r"^" + re.escape(n) + r"\s*", "", m.group(1))
            if norm(txt) != norm(title) and len(txt) > 3 and not txt.startswith(n):
                issues.append(("人工看", f[5:], f"链接文字与目标页 title 不同", f"「{m.group(1)}」/ {n}「{title}」"))
    for sev, where, what, extra in issues:
        print(f"{sev}\t{where}\t{what}\t{extra}")
    c = collections.Counter(i[0] for i in issues)
    print(f"[nav] OUTLINE 行 {len(out_rows)}；站点编号页 {len(pages)}；三方比对 {n_cmp}；toctree 条目 {sum(seen.values())}；"
          f"问题 {len(issues)}（一般 {c['一般']}，建议 {c['建议']}，人工看 {c['人工看']}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
