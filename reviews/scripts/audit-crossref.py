"""T-AUDIT-02 检查 B-6：示例与文档互指。

A. docs 里提到的 `examples/…` 路径与 `scripts/xxx.py`、`ros2/xxx.py`、`tests/…` 这类相对路径，在 git 中存在。
   相对路径按"examples 下任一文件以它结尾"判断（第 6 部分项目里的 scripts/ 与 8.5 的 scripts/ 都算）。
B. 孤儿：examples/** 里的 .py / .sh / .usda 等源文件，文件名没有在任何 docs 页面、也没有在任何 examples 下的
   README / .md 里出现过。包内模块（source/ 下）与 __init__.py 只要所在包目录被提到就算有主。
C. 每个示例目录（examples/<版本>/<编号-名字>/，第 6 部分项目按 scripts/、ros2/、tests/ 子目录）有 README，
   且 README 列出了本目录（不含子包）的每个脚本文件名。
D. `git ls-files` 里不应有 __pycache__ / .pyc。
E. 建议级：示例头注的验证日期晚于所在页 frontmatter 的 sources_checked（说明代码后来又验证过，页面的核对日期可能该更新）。

用法：python3 reviews/scripts/audit-crossref.py [--repo DIR] [--ref HEAD]
局限：只认反引号或链接里的路径；正文里不带路径、只写"本页示例"的提法不算引用。
"""
import argparse, collections, os, re, subprocess, sys

SRC_EXT = (".py", ".sh", ".usda", ".yaml", ".yml", ".json", ".ini", ".txt", ".toml", ".cfg", ".kit")
PLACEHOLDER = ("<!-- placeholder:", "待写，见 OUTLINE")
DATE = r"20\d\d-\d\d-\d\d"
UPSTREAM = {"scripts/create_description.py"}  # Galbot 描述仓库自己的脚本（6.1.1、3.5 讲的），不在本站 examples 里


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="HEAD")
    a = ap.parse_args()
    all_files = git(a.repo, "ls-tree", "-r", "--name-only", a.ref).splitlines()
    ex = [f for f in all_files if f.startswith("examples/")]
    exset = set(ex)
    docs = {f: git(a.repo, "show", f"{a.ref}:{f}") for f in all_files if f.startswith("docs/") and f.endswith(".md")}
    docs = {f: t for f, t in docs.items() if not any(m in t for m in PLACEHOLDER)}
    ex_md = {f: git(a.repo, "show", f"{a.ref}:{f}") for f in ex if f.endswith(".md")}
    issues = []
    # A
    n_ref = 0
    pat = re.compile(r"(?<![\w./-])((?:examples/[\w./+-]+)|(?:(?:scripts|ros2|tests|source|bin)/[\w./+-]+\.(?:py|sh|txt|ini)))")
    for f, t in sorted(docs.items()):
        t2 = re.sub(r"^\[\^[^\]]+\]:.*$", "", t, flags=re.M)  # 脚注里的 GitHub 路径（如 IsaacLab 的 scripts/）不算
        for ln, line in enumerate(t2.splitlines(), 1):
            if "github.com" in line and "examples/" not in line:
                continue
            for m in pat.finditer(line):
                p = m.group(1).rstrip(".,;:)）。")
                if "<" in p or "*" in p or "…" in p or p in UPSTREAM:
                    continue
                n_ref += 1
                if p.startswith("examples/"):
                    ok = p in exset or any(x.startswith(p.rstrip("/") + "/") for x in ex)
                else:
                    ok = any(x.endswith("/" + p) for x in ex)
                    if not ok and (p.startswith("scripts/rsl_rl") or p.startswith("scripts/reinforcement_learning") or p.startswith("scripts/tools") or p.startswith("scripts/imitation_learning") or p.startswith("scripts/environments") or p.startswith("scripts/benchmarks") or p.startswith("scripts/demos") or p.startswith("scripts/tutorials") or p.startswith("source/isaaclab")):
                        ok = True  # Isaac Lab 仓库自己的脚本，不在本站 examples 里
                if not ok:
                    issues.append(("一般", f"{f[5:]}:{ln}", f"提到的 {p} 在 examples 里不存在", ""))
    # B
    corpus = "\n".join(docs.values()) + "\n".join(ex_md.values())
    names = collections.Counter(os.path.basename(x) for x in ex)
    n_src = 0
    for x in ex:
        b = os.path.basename(x)
        if not b.endswith(SRC_EXT) or "__pycache__" in x or b in ("__init__.py", "README.md"):
            continue
        n_src += 1
        rel = x.split("/", 2)[2]  # 去掉 examples/<版本>/
        cands = {b, rel}
        parts = x.split("/")
        # 包内文件：任一上级目录名被提到即可
        if "/tests/" in x:  # 测试按目录提（7.4："tests/unit/，13 个"）
            cands |= {"/".join(parts[i:-1]) + "/" for i in range(3, len(parts) - 1)}
            sev_override = "建议"
        else:
            sev_override = None
        if "/source/" in x or "/tasks/" in x or "/academy_demo/" in x:
            cands |= {"/".join(parts[i:-1]) for i in range(3, len(parts) - 1)}
            cands |= {parts[-2]}
        if not any(c in corpus for c in cands):
            sev = sev_override or ("一般" if b.endswith((".py", ".sh")) else "建议")
            issues.append((sev, x, "孤儿：文件名没有在任何页面或 README 里出现" + ("（所在 tests 子目录被提到）" if sev_override and any(c in corpus for c in cands if c.endswith("/")) else ""), ""))
    # C
    dirs = collections.defaultdict(list)
    for x in ex:
        parts = x.split("/")
        if len(parts) < 4:
            continue
        d = "/".join(parts[:3])
        if parts[2] in ("6-galbot-project", "8.5-galbot-reach") and len(parts) == 5 and parts[3] in ("scripts", "ros2", "tests"):
            dirs[d].append(parts[4])
        elif len(parts) == 4:
            dirs[d].append(parts[3])
    n_dir = 0
    for d, fs in sorted(dirs.items()):
        n_dir += 1
        readme = ex_md.get(d + "/README.md")
        scripts = [f for f in fs if f.endswith((".py", ".sh")) and f not in ("__init__.py", "conftest.py")]
        if readme is None:
            if scripts:
                issues.append(("一般", d, "示例目录没有 README", "、".join(scripts)))
            continue
        miss = [f for f in scripts if f not in readme]
        if miss:
            issues.append(("建议", d + "/README.md", f"README 没有列出 {len(miss)} 个脚本", "、".join(sorted(miss))))
    # D
    bad = [f for f in all_files if "__pycache__" in f or f.endswith(".pyc")]
    for f in bad:
        issues.append(("一般", f, "git 跟踪了缓存文件", ""))
    # E
    page_of = {}
    for f, t in docs.items():
        for m in re.finditer(r"examples/(isaaclab-[\d.]+/[\w.+-]+)", t):
            page_of.setdefault(m.group(1), f)
    for x in ex:
        if not x.endswith(".py"):
            continue
        key = "/".join(x.split("/")[1:3])
        if key.endswith(("6-galbot-project", "8.5-galbot-reach")):
            continue  # 项目目录被多页共用，无法对到单页的 sources_checked
        p = page_of.get(key)
        if not p:
            continue
        head = git(a.repo, "show", f"{a.ref}:{x}")[:1500]
        dm = re.findall(DATE, head)
        fm = re.search(r"sources_checked:\s*\"?(" + DATE + ")", docs[p])
        if dm and fm and max(dm) > fm.group(1):
            issues.append(("建议", x, f"头注日期 {max(dm)} 晚于 {p[5:]} 的 sources_checked {fm.group(1)}", ""))
    for sev, where, what, extra in issues:
        print(f"{sev}\t{where}\t{what}\t{extra}")
    c = collections.Counter(i[0] for i in issues)
    print(f"[crossref] 页面引用路径 {n_ref} 处；examples 源文件 {n_src} 个；示例目录 {n_dir} 个；缓存文件 {len(bad)}；"
          f"问题 {len(issues)}（一般 {c['一般']}，建议 {c['建议']}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
