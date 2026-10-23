"""T-SITE-17 检查 12：页面里不该出现的本站内部叫法。

读者看不到三个 session 的分工，也看不到 reviews/ 与 tasks/，所以页面里：
  一般：出现"校验方""实现方"、"设计会话 / 实现会话 / 校验会话"（28fbf31 裁断计入）、
        "……的会话 / 两个独立会话 / 微任务"这类内部流程用语（95dfe68 裁断计入；"终端会话"不算），引用 reviews/ 路径，
        或决策编号 D-xxx（0edfa3e 裁断计入）；
  建议：正文出现任务卡号（T-6.1.5b、T-SITE-15、T-GA-01、T-6-common 之类），逐条人工判断。
        6.1.7 演示 commit message 的示例可以保留，要在附记说明。
排除：A.5 更新日志（"任务"列本来就是卡号）、docs/MIGRATION-NOTES.md 与 _ 开头的文件（不是站点页面）。

用法：python3 reviews/scripts/audit-internal.py [--repo DIR] [--ref HEAD]
"""
import argparse, posixpath, re, subprocess

EXCLUDE = {"docs/appendix/A.5-changelog.md", "docs/MIGRATION-NOTES.md"}
ROLE = re.compile(r"校验方|实现方|设计会话|实现会话|校验会话|reviews/|(?<!终端)(?<!设计)(?<!实现)(?<!校验)会话|微任务"
                  r"|(?<![A-Za-z0-9_/.\-])D-\d{3}(?![0-9])")
# 前面不能是字母、数字、下划线、/、.、-，以免把 URL 或文件名里的 T- 当成卡号
CARD = re.compile(r"(?<![A-Za-z0-9_/.\-])T-(?:\d+(?:\.\d+)*[a-z]?|[A-Z]+(?:-[0-9A-Z]+)*[a-z]?)(?:-[a-z]+)?(?![A-Za-z0-9])")


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="HEAD")
    a = ap.parse_args()
    files = [p for p in git(a.repo, "ls-tree", "-r", "--name-only", a.ref, "docs").splitlines()
             if p.endswith(".md") and p not in EXCLUDE and not posixpath.basename(p).startswith("_")]
    general, advice = [], []
    for p in sorted(files):
        for i, line in enumerate(git(a.repo, "show", f"{a.ref}:{p}").splitlines(), 1):
            for m in ROLE.finditer(line):
                general.append(f"一般\t{p}:{i}\t{m.group(0)}\t{line.strip()[:120]}")
            for m in CARD.finditer(line):
                advice.append(f"建议\t{p}:{i}\t{m.group(0)}\t{line.strip()[:120]}")
    for row in general + advice:
        print(row)
    pages = len({r.split("\t")[1].rsplit(":", 1)[0] for r in general + advice})
    print(f"[internal] 页面 {len(files)} 个；内部角色名、流程用语、reviews/ 与决策编号 {len(general)} 处（一般），"
          f"任务卡号 {len(advice)} 处（建议，逐条判断）；涉及 {pages} 页")


if __name__ == "__main__":
    main()
