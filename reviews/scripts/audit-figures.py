"""T-AUDIT-02 检查 B-9：图表编号与引用。

A. 页内编号：图注（行首"*图 N：" 或 figure 指令里的"图 N："）与表注（行首"*表 N："）在页内从 1 起连续、不重号、按出现顺序递增。
B. 页内引用：正文里的"表 N""图 N"（不在图注 / 表注行首）要在本页存在。
   前面紧跟别的页编号（如"6.6.2 表 3""[6.4.5 表 5](…)"）的算跨页引用，到那一页去核对编号存在。
   "表 N 中""表 N 的"等都按引用算；"表 1–3""表 2、3"展开核对。

用法：python3 reviews/scripts/audit-figures.py [--repo DIR] [--ref HEAD]
局限：只认"表 / 图 + 阿拉伯数字"；"上表""下图"之类不核对。跨页引用只认"编号 + 空格 + 表/图 N"与指向 .md 的链接两种写法。
"""
import argparse, collections, os, re, subprocess, sys

PLACEHOLDER = ("<!-- placeholder:", "待写，见 OUTLINE")
CAP = re.compile(r"^(?:\*|\s*)?(表|图) ?(\d+)(?:\s*[–-]\s*(\d+))?[：:]")


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout


def strip(t):
    """去掉 frontmatter、普通代码块、HTML 注释（换成同样多的空行，行号不变）；figure / mermaid 指令块保留。"""
    t = re.sub(r"^---\n.*?\n---\n", lambda m: "\n" * m.group(0).count("\n"), t, flags=re.S)
    t = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), t, flags=re.S)
    out, fence, keep = [], None, False
    for line in t.split("\n"):
        m = re.match(r"^(\s*)(`{3,}|~{3,}|:{3,})(.*)$", line)
        if fence is None and m:
            fence, keep = m.group(2), m.group(3).startswith(("{figure}", "{mermaid}", "{admonition}", "{note}", "{tip}", "{warning}", "{important}"))
            out.append(line)
            continue
        if fence is not None and m and m.group(2) == fence and not m.group(3).strip():
            fence = None
            out.append(line)
            continue
        out.append(line if (fence is None or keep) else "")
    return "\n".join(out)


def captions(t):
    caps = []  # (kind, n, line)
    in_fig = False
    for ln, line in enumerate(t.splitlines(), 1):
        if line.startswith("```{figure}") or line.startswith(":::{figure}"):
            in_fig = True
            continue
        if in_fig and (line.startswith("```") or line.startswith(":::")):
            in_fig = False
            continue
        m = CAP.match(line)
        if m and (line.startswith("*") or in_fig or line.startswith(m.group(1))):
            for n in range(int(m.group(2)), int(m.group(3) or m.group(2)) + 1):
                caps.append((m.group(1), n, ln))
    return caps


def expand(s):
    out = []
    for part in re.split(r"[、，,]|与|和", s):
        m = re.match(r"\s*(\d+)\s*[–-]\s*(\d+)", part)
        if m:
            out += list(range(int(m.group(1)), int(m.group(2)) + 1))
        else:
            m = re.match(r"\s*(\d+)", part)
            if m:
                out.append(int(m.group(1)))
    return out


REF = re.compile(r"(?:\]\(([^)#\s]+\.md)[^)]*\)\s*|(\[?)((?:\d|A)(?:\.\d+)+)\s*)?(?<![A-Za-z0-9_.])(表|图) ?(\d+(?:\s*[–-]\s*\d+)?(?:\s*[、，和与]\s*(?:表|图)?\s*\d+(?![.\d]))*)(\]\(([^)#]+\.md)[^)]*\))?")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="HEAD")
    a = ap.parse_args()
    files = [f for f in git(a.repo, "ls-tree", "-r", "--name-only", a.ref, "docs").splitlines() if f.endswith(".md") and "/_build/" not in f]
    texts = {f: strip(git(a.repo, "show", f"{a.ref}:{f}")) for f in files}
    texts = {f: t for f, t in texts.items() if not any(p in t for p in PLACEHOLDER)}
    caps = {f: captions(t) for f, t in texts.items()}
    have = {f: {(k, n) for k, n, _ in c} for f, c in caps.items()}
    by_num = {}
    for f in texts:
        m = re.match(r"([0-9A]+(?:\.\d+)+)-", os.path.basename(f))
        if m:
            by_num[m.group(1)] = f
    issues = []
    n_cap = n_ref = n_xref = 0
    for f, c in sorted(caps.items()):
        for kind in ("表", "图"):
            seq = [(n, ln) for k, n, ln in c if k == kind]
            n_cap += len(seq)
            nums = [n for n, _ in seq]
            dup = [n for n, cnt in collections.Counter(nums).items() if cnt > 1]
            if dup:
                issues.append(("一般", f[5:], f"{kind}注重号：{kind} {dup}", ""))
            if nums and sorted(set(nums)) != list(range(1, max(nums) + 1)):
                issues.append(("一般", f[5:], f"{kind}注编号不连续", " ".join(map(str, nums))))
            elif nums != sorted(nums):
                issues.append(("一般", f[5:], f"{kind}注编号没有按出现顺序递增", " ".join(map(str, nums))))
    for f, t in sorted(texts.items()):
        if f.endswith("A.5-changelog.md"):
            continue  # 更新日志的"一句话"摘自各页提交信息，里面的"表 N"指那一页
        caplines = {ln for _, _, ln in caps[f]}
        for ln, line in enumerate(t.splitlines(), 1):
            if line.startswith("[^") and "]:" in line[:40]:
                continue
            for m in REF.finditer(line):
                kind, nums = m.group(4), expand(re.sub(r"[表图]", "", m.group(5)))
                if ln in caplines and m.start() < 3:
                    continue  # 图注 / 表注本身
                target, xpage = f, None
                link = m.group(7) or m.group(1)
                if link:
                    p = os.path.normpath(os.path.join(os.path.dirname(f), link))
                    if p != f:
                        target, xpage = p, p
                elif m.group(3):
                    p = by_num.get(m.group(3))
                    if p and p != f:
                        target, xpage = p, p
                    elif not p:
                        continue  # "Isaac Sim 5.1 表 2" 之类的版本号，不是页编号
                if target not in have:
                    continue
                for n in nums:
                    if xpage:
                        n_xref += 1
                    else:
                        n_ref += 1
                    if (kind, n) not in have[target]:
                        where = f"跨页引用 {target[5:]}" if xpage else "本页"
                        issues.append(("一般", f"{f[5:]}:{ln}", f"引用的 {kind} {n} 在{where}不存在", line.strip()[max(0, m.start() - 20):m.end() + 10]))
    for sev, where, what, extra in issues:
        print(f"{sev}\t{where}\t{what}\t{extra}")
    print(f"[figures] 正式页 {len(texts)}；图注 / 表注 {n_cap}；页内引用 {n_ref}；跨页引用 {n_xref}；问题 {len(issues)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
