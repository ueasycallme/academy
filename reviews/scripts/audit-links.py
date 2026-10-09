"""T-AUDIT-01 检查 1：外链存活。

从 git HEAD 的 docs/**/*.md 抽取全部 http(s) 链接，逐个 GET（跟随重定向），
列出非 200、以及重定向到新地址的链接。403 按 CONVENTIONS 第 4 节单列为"抓取被拒"，
不直接判失效（同域名其他链接也 403 时多半是反爬）。

用法：python3 reviews/scripts/audit-links.py [--repo DIR] [--ref HEAD] [--out FILE.tsv]
                [--mirror isaac-sim/IsaacLab=/path/to/IsaacLab ...]
需要 curl。只读，不改任何文件（--out 只写到指定路径）。

GitHub 对并发抓取会回 429 / 503（限流，不是失效）。所以：
- 给了 --mirror 的仓库，blob/tree 链接用本地克隆核对：tag 存在、路径存在、#L 行号不超过文件行数（比抓网页更严）；
- 其余 github.com 链接限 2 个并发，429/503 时退避重试，最终仍是 429/503 的单列为"限流未核"，不算失效。
"""
import argparse, collections, concurrent.futures as cf, re, subprocess, sys, urllib.parse

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
URL_RE = re.compile(r"https?://[^\s)<>\"'`\]|]+")


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout


def md_files(repo, ref):
    return [p for p in git(repo, "ls-tree", "-r", "--name-only", ref, "docs").splitlines()
            if p.endswith(".md") and "/_build/" not in p]


def extract(repo, ref):
    urls = collections.defaultdict(list)  # url -> [page:line]
    for p in md_files(repo, ref):
        in_code = False
        for i, line in enumerate(git(repo, "show", f"{ref}:{p}").splitlines(), 1):
            if line.lstrip().startswith(("```", "~~~")):
                in_code = not in_code
            for u in URL_RE.findall(line):
                u = u.rstrip(".,;:，。；：）")
                if in_code and "github.com" not in u and "nvidia" not in u:
                    continue  # 代码块里的示例地址（localhost 等）不查
                if re.match(r"https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|<)", u):
                    continue
                urls[u].append(f"{p[5:]}:{i}")
    return urls


GH = __import__("threading").Semaphore(2)
MIRROR = {}


def local_check(u):
    m = re.match(r"https://github\.com/([^/]+/[^/]+)/(blob|tree)/([^/]+)/([^#]*)(?:#L(\d+)(?:-L(\d+))?)?$", u)
    if not m or m.group(1) not in MIRROR:
        return None
    repo, kind, ref, path, l1, l2 = m.groups()
    path = urllib.parse.unquote(path).rstrip("/")
    r = subprocess.run(["git", "-C", MIRROR[repo], "cat-file", "-t", f"{ref}:{path}" if path else ref],
                       capture_output=True, text=True)
    if r.returncode:
        return u, "404", "本地克隆：tag 或路径不存在", ""
    if l1:
        n = len(subprocess.run(["git", "-C", MIRROR[repo], "show", f"{ref}:{path}"], capture_output=True,
                               text=True).stdout.splitlines())
        if int(l2 or l1) > n:
            return u, "LINE", f"本地克隆：行号 L{l2 or l1} 超出文件 {n} 行", ""
    return u, "200", u, "local"


def fetch(u):
    loc = local_check(u)
    if loc:
        return loc
    target = u.split("#")[0]
    if "github.com" in target:
        import time
        with GH:
            for attempt in range(5):
                r = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-L", "--max-time", "25", "-A", UA,
                                    "-w", "%{http_code} %{url_effective}", target], capture_output=True, text=True)
                code = (r.stdout.split(" ", 1) + [""])[0] or "000"
                if code not in ("429", "503", "000"):
                    break
                time.sleep(5 * (attempt + 1))
            out = r.stdout.strip().split(" ", 1)
            return u, code, out[1] if len(out) > 1 else "", r.stderr.strip()[:80]
    for attempt in range(2):
        r = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-L", "--max-time", "25", "-A", UA,
                            "-w", "%{http_code} %{url_effective}", target], capture_output=True, text=True)
        out = r.stdout.strip().split(" ", 1)
        code = out[0] if out and out[0] else "000"
        eff = out[1] if len(out) > 1 else ""
        if code not in ("000", "429", "502", "503", "504"):
            break
    return u, code, eff, r.stderr.strip()[:80]


def norm(u):
    p = urllib.parse.urlsplit(u.split("#")[0])
    return (p.netloc.lower(), p.path.rstrip("/") or "/", p.query)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--out")
    ap.add_argument("-j", type=int, default=12)
    ap.add_argument("--mirror", action="append", default=[], help="owner/repo=本地克隆路径")
    a = ap.parse_args()
    for m in a.mirror:
        k, v = m.split("=", 1)
        MIRROR[k] = v
    urls = extract(a.repo, a.ref)
    with cf.ThreadPoolExecutor(a.j) as ex:
        res = sorted(ex.map(fetch, urls), key=lambda r: (r[1], r[0]))
    by_host_403 = collections.Counter(urllib.parse.urlsplit(u).netloc for u, c, _, _ in res if c == "403")
    host_total = collections.Counter(urllib.parse.urlsplit(u).netloc for u in urls)
    bad, blocked, redir, limited = [], [], [], []
    n_local = sum(1 for r in res if r[3] == "local")
    for u, c, eff, err in res:
        if c in ("429", "503") and "github.com" in u:
            limited.append(u)
            continue
        if c == "200":
            if eff and norm(eff) != norm(u):
                redir.append((u, eff))
        elif c == "403":
            blocked.append((u, c, eff))
        else:
            bad.append((u, c, eff, err))
    lines = []
    for u, c, eff, err in bad:
        lines.append(f"FAIL\t{c}\t{u}\t{eff}\t{err}\t{' '.join(urls[u][:4])}")
    for u, c, eff in blocked:
        h = urllib.parse.urlsplit(u).netloc
        lines.append(f"BLOCKED\t403\t{u}\t(同域 {by_host_403[h]}/{host_total[h]} 个 403)\t\t{' '.join(urls[u][:4])}")
    for u in limited:
        lines.append(f"LIMITED\t429/503\t{u}\t（GitHub 限流，未核）\t\t{' '.join(urls[u][:4])}")
    for u, eff in redir:
        lines.append(f"REDIRECT\t200\t{u}\t{eff}\t\t{' '.join(urls[u][:4])}")
    text = "\n".join(lines)
    if a.out:
        open(a.out, "w").write(text + "\n")
    print(text)
    print(f"[links] 唯一 URL {len(urls)}（引用 {sum(map(len, urls.values()))} 处）；"
          f"200 {sum(c == '200' for _, c, _, _ in res)}（其中本地克隆核对 {n_local}）；失效/异常 {len(bad)}；"
          f"403 {len(blocked)}；GitHub 限流未核 {len(limited)}；重定向 {len(redir)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
