"""T-AUDIT-01 检查 6：占位页的"现在可以读什么"。

独立于 tools/gen_placeholders.py 的逻辑再核一遍（只读 git 里的文件，不调用生成器）：
  A. 列表里每个链接的目标文件存在，且是正式页（不是占位页）；
  B. 链接文字里的编号与标题和目标页一致（标题取目标页的一级标题）；
  C. 同一目录下的正式页都列出来了（列表"齐不齐"；0.7 学习路线图那一项不计）；
  D. 占位页不进 toctree 的约定：frontmatter 是否有 orphan（只统计，不判错，按 CONVENTIONS 第 2 节）。

用法：python3 reviews/scripts/audit-placeholders.py [--repo DIR] [--ref HEAD]
"""
import argparse, os, posixpath, re, subprocess, sys

MARKS = ("<!-- placeholder:", "待写，见 OUTLINE")


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout


def title_of(t):
    m = re.search(r"^# (.+)$", t, re.M)
    return m.group(1).strip() if m else ""


def num_of(p):
    m = re.match(r"([0-9A]+(?:\.\d+)*)-", posixpath.basename(p))
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="HEAD")
    a = ap.parse_args()
    files = [p for p in git(a.repo, "ls-tree", "-r", "--name-only", a.ref, "docs").splitlines()
             if p.endswith(".md") and "/_" not in p]
    text = {p: git(a.repo, "show", f"{a.ref}:{p}") for p in files}
    ph = {p for p, t in text.items() if any(m in t for m in MARKS)}
    issues, n_links = [], 0
    for p in sorted(ph):
        t = text[p]
        i = t.find("## 现在可以读什么")
        if i < 0:
            issues.append(("一般", p[5:], "占位页没有“现在可以读什么”一节", ""))
            continue
        sec = t[i: i + 5 + t[i + 5:].find("\n## ")] if t[i + 5:].find("\n## ") >= 0 else t[i:]
        listed = set()
        for txt, href in re.findall(r"- \[([^\]]+)\]\(([^)]+)\)", sec):
            n_links += 1
            tgt = posixpath.normpath(posixpath.join(posixpath.dirname(p), href.split("#")[0]))
            if tgt not in text:
                issues.append(("阻塞", p[5:], f"链接目标不存在：{href}", txt))
                continue
            if tgt in ph:
                issues.append(("一般", p[5:], f"链接到的仍是占位页：{href}", txt))
            listed.add(tgt)
            n = num_of(tgt)
            want = f"{n} {title_of(text[tgt])}" if n else title_of(text[tgt])
            if "0.7-learning-paths" not in tgt and txt != want:
                issues.append(("建议", p[5:], "链接文字与目标页编号/标题不一致", f"“{txt}” vs “{want}”"))
        same_dir = {q for q in files if posixpath.dirname(q) == posixpath.dirname(p) and q not in ph
                    and num_of(q) and q != p}
        missing = sorted(same_dir - listed)
        if missing:
            issues.append(("一般", p[5:], "同目录的正式页没有列出", "、".join(posixpath.basename(m) for m in missing)))
        if "并无" in sec or "暂时没有已完成" in sec:
            if same_dir:
                issues.append(("一般", p[5:], "写“本部分暂时没有已完成的页面”，但同目录有正式页", ""))
    n_orphan = sum(1 for p in ph if re.search(r"^orphan:\s*true", text[p], re.M))
    for sev, where, what, extra in issues:
        print(f"{sev}\t{where}\t{what}\t{extra}")
    print(f"[placeholders] 占位页 {len(ph)}（frontmatter 带 orphan 的 {n_orphan}）；列表链接 {n_links}；问题 {len(issues)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
