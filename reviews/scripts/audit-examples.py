"""T-AUDIT-01 检查 7：examples 文件头注（CONVENTIONS 第 5 节）。

对 git 里 examples/**/*.py，看文件开头（第一行代码之前的注释与模块 docstring，最多 40 行）是否写了：
  验证版本（"验证版本"或"未验证"）、验证日期（YYYY-MM-DD）、GPU 型号（"GPU"一行）。
写了"未验证"的文件只要求有这一标记。__init__.py 单列（多为包声明，按"建议"报）。
分类：头注是 Isaac Lab 版权行的（由 Isaac Lab 模板生成器生成、本站未改头注）记"模板"；
只缺 GPU、且所在示例目录的 README 写了 GPU 的记"GPU 在 README"。
另顺带查 `omni.isaac.` 旧命名的 import（CONVENTIONS 第 5 节：除非在讲迁移）。

用法：python3 reviews/scripts/audit-examples.py [--repo DIR] [--ref HEAD]
"""
import argparse, re, subprocess, sys


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout


def header(t):
    out, in_doc = [], None
    for i, l in enumerate(t.splitlines()[:40]):
        s = l.strip()
        if in_doc:
            out.append(l)
            if in_doc in s:
                in_doc = None
            continue
        if s.startswith("#") or not s:
            out.append(l)
            continue
        m = re.match(r'[rRuU]?("""|\'\'\')', s)
        if m:
            out.append(l)
            if s.count(m.group(1)) == 1:
                in_doc = m.group(1)
            continue
        break
    return "\n".join(out)


_readme = {}


def readme_gpu(a, p):
    """从文件所在目录往上找 examples/isaaclab-2.3/<示例目录>/README.md，看是否写了 GPU。"""
    parts = p.split("/")
    d = "/".join(parts[:3])
    if d not in _readme:
        try:
            _readme[d] = bool(re.search(r"GPU[：:]|RTX", git(a.repo, "show", f"{a.ref}:{d}/README.md")))
        except subprocess.CalledProcessError:
            _readme[d] = False
    return _readme[d]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="HEAD")
    a = ap.parse_args()
    files = [p for p in git(a.repo, "ls-tree", "-r", "--name-only", a.ref, "examples").splitlines() if p.endswith(".py")]
    issues, n_ok = [], 0
    for p in files:
        t = git(a.repo, "show", f"{a.ref}:{p}")
        h = header(t)
        init = p.endswith("__init__.py")
        if "未验证" in h:
            n_ok += 1
        else:
            miss = [k for k, pat in (("验证版本", r"验证版本"), ("验证日期", r"验证日期[：:]\s*20\d\d-\d\d-\d\d"),
                                     ("GPU", r"GPU[：:]|显卡[：:]|RTX")) if not re.search(pat, h)]
            if miss:
                tag = ""
                if "The Isaac Lab Project Developers" in h:
                    tag = "模板"
                elif miss == ["GPU"] and readme_gpu(a, p):
                    tag = "GPU 在 README"
                if init and len(t.strip().splitlines()) <= 15:
                    sev = "建议"
                elif tag:
                    sev = "建议"
                elif miss == ["GPU"]:
                    sev = "建议" if not re.search(r"isaaclab|isaacsim|torch|AppLauncher|SimulationApp", t) else "一般"
                else:
                    sev = "一般"
                issues.append((sev, p, "头注缺：" + "、".join(miss) + (f"（{tag}）" if tag else "")))
            else:
                n_ok += 1
        for n, l in enumerate(t.splitlines(), 1):
            if re.match(r"\s*(from|import)\s+omni\.isaac\.", l):
                issues.append(("建议", f"{p}:{n}", "使用 omni.isaac.* 旧命名：" + l.strip()[:60]))
    for sev, p, what in sorted(issues):
        print(f"{sev}\t{p}\t{what}")
    print(f"[examples] .py 文件 {len(files)}；头注齐全或标未验证 {n_ok}；问题 {len(issues)}"
          f"（一般 {sum(i[0] == '一般' for i in issues)}，建议 {sum(i[0] == '建议' for i in issues)}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
