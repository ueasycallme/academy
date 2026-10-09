"""T-AUDIT-01 检查 2：站内锚点。

sphinx-build -W 不检查 `page.md#anchor` 的锚点是否真的存在。本脚本在构建好的 HTML 上核对：
每个站内链接（相对路径，含 {ref} 生成的链接）的目标文件存在，且 `#id` 在目标页里有对应 id。

用法：python3 reviews/scripts/audit-anchors.py HTML_DIR
HTML_DIR 用 HEAD 的干净克隆构建：
    git clone -q . $S/repo && (cd $S/repo && sphinx-build -E -a -q -b html docs $S/html)
"""
import os, sys, urllib.parse
from bs4 import BeautifulSoup

SKIP_DIRS = {"_static", "_sources", "_images", "_downloads"}
SKIP_FILES = {"genindex.html", "search.html", "py-modindex.html"}


def pages(root):
    for d, ds, fs in os.walk(root):
        ds[:] = [x for x in ds if x not in SKIP_DIRS]
        for f in fs:
            if f.endswith(".html") and f not in SKIP_FILES:
                yield os.path.join(d, f)


def main():
    root = os.path.abspath(sys.argv[1])
    ids = {}

    def ids_of(p):
        if p not in ids:
            s = BeautifulSoup(open(p, encoding="utf-8"), "html.parser")
            ids[p] = {e["id"] for e in s.find_all(id=True)} | {e["name"] for e in s.find_all("a", attrs={"name": True})}
        return ids[p]

    n_links = n_frag = 0
    bad = []
    for p in sorted(pages(root)):
        s = BeautifulSoup(open(p, encoding="utf-8"), "html.parser")
        art = s.select_one("article.bd-article") or s  # 只查正文；导航栏/侧栏由主题生成
        for a in art.find_all("a", href=True):
            h = a["href"]
            if h.startswith(("http:", "https:", "mailto:", "javascript:")) or h == "#":
                continue
            n_links += 1
            path, _, frag = h.partition("#")
            tgt = os.path.normpath(os.path.join(os.path.dirname(p), urllib.parse.unquote(path))) if path else p
            rel = os.path.relpath(p, root)
            if os.path.isdir(tgt):
                tgt = os.path.join(tgt, "index.html")
            if not os.path.exists(tgt):
                if not tgt.endswith(".html") and os.path.exists(tgt):
                    continue
                bad.append((rel, h, "目标文件不存在", a.get_text().strip()[:40]))
                continue
            if frag and tgt.endswith(".html"):
                n_frag += 1
                if urllib.parse.unquote(frag) not in ids_of(tgt):
                    bad.append((rel, h, "锚点不存在", a.get_text().strip()[:40]))
    for rel, h, why, txt in bad:
        print(f"BAD\t{rel}\t{h}\t{why}\t{txt}")
    print(f"[anchors] 站内链接 {n_links}（带 # 的 {n_frag}）；问题 {len(bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
