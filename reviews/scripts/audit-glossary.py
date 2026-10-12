"""T-AUDIT-02 检查 B-5：术语表指向、英文拼写一致性、术语候选。

A. 指向：0.8 每个词条"首次详细讲解"列的链接，在构建好的 HTML 里找到目标页与锚点所在的 <section>，
   看这一节的正文里有没有出现该词条（中文名任一，或英文名）。没出现的列"一般"；
   只出现 1 次的列"人工看"（可能只是提到，不是讲解）。没有锚点的链接按整页算。
B. 拼写：全站正文里"中文（English）"形式的对照，同一个中文词配了不同的英文（忽略大小写后仍不同）列出；
   只差大小写的单列一档。中文词取括号前连续的汉字（最多 8 个），英文取括号内以拉丁字母开头、不含汉字的部分。
C. 候选：同一个"中文（English）"对出现在 ≥ 2 个正式页、而中文词不在术语表里的，列为候选（给下一批术语表卡）。

用法：python3 reviews/scripts/audit-glossary.py --repo DIR --html DIR [--ref HEAD] [--min-pages 2]
  --html 是 Sphinx 在同一 ref 上构建的 HTML 目录（audit-all.sh 里的 $OUT/html）。
局限：A 只能判断"该节有没有这个词"，"是讲解还是提到"要人工；B、C 是启发式，中文词的左边界按汉字串截断，
"的""是"之类会被吃进去（脚本去掉常见虚词前缀，仍有噪声）。
"""
import argparse, collections, html.parser, os, re, subprocess, sys

CJK = r"一-鿿"
PLACEHOLDER = ("<!-- placeholder:", "待写，见 OUTLINE")
STOP_PREFIX = re.compile(r"^.*?(?:的|是|为|和|与|或|叫|称|即|把|用|在|做|对|中|个|种|了|讲|见|写|按|由|从|到|指|如|及|等)(?=[" + CJK + r"]{2,})")


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout


def glossary(text):
    rows = []
    for line in text.splitlines():
        m = re.match(r"\| \[\*\*(.+?)\*\*\]\{#(term-[\w-]+)\} \| ([^|]+) \|[^|]*\| ([^|]*)\|", line)
        if not m:
            continue
        zh = [s.strip().strip("`") for s in m.group(1).split(" / ")]
        en = [re.sub(r"\s*\(.*?\)$", "", s.strip()) for s in m.group(3).split(" / ")]
        links = re.findall(r"\]\(\.\./([^)#]+)(?:#([^)]+))?\)", m.group(4))
        rows.append(dict(zh=zh, en=en, anchor=m.group(2), link=links[0] if links else None, cell=m.group(4).strip()))
    return rows


class Sections(html.parser.HTMLParser):
    """收集 .bd-article 内每个带 id 的元素所在 <section> 的文本（含子节）。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # [(tag, ids)]
        self.text = collections.defaultdict(list)
        self.in_article = 0
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if "bd-article" in cls:
            self.in_article = 1
        ids = [a["id"]] if a.get("id") else []
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("br", "img", "hr", "meta", "link", "input", "wbr"):
            if ids and tag == "span":
                pass
            return
        self.stack.append((tag, ids))

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if not self.in_article or self.skip:
            return
        self.text["__page__"].append(data)
        for tag, ids in self.stack:
            if tag == "section":
                for i in ids:
                    self.text[i].append(data)
        # 非 section 的 id（如 span 锚点）：记到最近的外层 section
        sec = next((ids for tag, ids in reversed(self.stack) if tag == "section" and ids), None)
        for tag, ids in self.stack:
            if tag != "section" and ids and sec:
                for i in ids:
                    self.text.setdefault("@" + i, sec)


def section_text(html_dir, page, anchor, cache={}):
    p = os.path.join(html_dir, page[:-3] + ".html")
    if p not in cache:
        if not os.path.exists(p):
            cache[p] = None
        else:
            s = Sections()
            s.feed(open(p, encoding="utf-8").read())
            cache[p] = s.text
    t = cache[p]
    if t is None:
        return None
    if not anchor:
        return "".join(t["__page__"])
    if anchor in t and isinstance(t[anchor], list):
        return "".join(t[anchor])
    if "@" + anchor in t:
        return "".join(t[t["@" + anchor][0]])
    return None


def body(text):
    t = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    t = re.sub(r"```.*?```", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = re.sub(r"^\[\^[^\]]+\]:.*$", "", t, flags=re.M)
    t = re.sub(r"`[^`\n]*`", "", t)
    t = re.sub(r"\]\([^)]*\)", "]", t)
    return t


PAIR = re.compile(r"([" + CJK + r"][" + CJK + r"A-Za-z0-9·]{0,10})（([A-Za-z][^（）" + CJK + r"]{0,60}?)）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--html", required=True)
    ap.add_argument("--min-pages", type=int, default=2)
    a = ap.parse_args()
    files = [p for p in git(a.repo, "ls-tree", "-r", "--name-only", a.ref, "docs").splitlines() if p.endswith(".md")]
    texts = {p[5:]: git(a.repo, "show", f"{a.ref}:{p}") for p in files}
    texts = {p: t for p, t in texts.items() if not any(m in t for m in PLACEHOLDER) and "/_build/" not in p}
    rows = glossary(texts["0-map/0.8-glossary.md"])
    # MyST 给中文标题生成的锚点在 HTML 里变成 idN，所以链接目标从构建好的术语表 HTML 里取
    gh = open(os.path.join(a.html, "0-map/0.8-glossary.html"), encoding="utf-8").read()
    hrefs = {}
    for tr in re.findall(r"<tr.*?</tr>", gh, re.S):
        m = re.search(r'id="(term-[\w-]+)"', tr)
        tds = re.findall(r"<td>(.*?)</td>", tr, re.S)
        if m and len(tds) >= 4:
            h = re.search(r'href="\.\./([^"#]+)(?:#([^"]+))?"', tds[3])
            if h:
                hrefs[m.group(1)] = (h.group(1)[:-5] + ".md", h.group(2) or "")
    for r in rows:
        if r["link"] and r["anchor"] in hrefs:
            r["md_link"] = r["link"]
            r["link"] = hrefs[r["anchor"]]
    issues = []
    # A. 指向
    n_link = n_once = 0
    for r in rows:
        if not r["link"]:
            issues.append(("建议", "0-map/0.8", f"{r['anchor']}：首次详细讲解列没有站内链接", r["cell"][:40]))
            continue
        n_link += 1
        page, anchor = r["link"]
        txt = section_text(a.html, page, anchor)
        if txt is None:
            issues.append(("一般", "0-map/0.8", f"{r['anchor']}：链接目标 {page}#{anchor} 在 HTML 里找不到", ""))
            continue
        names = [z for z in r["zh"] if z] + [e for e in r["en"] if e]
        cnt = sum(txt.count(z) for z in r["zh"]) or max((txt.lower().count(e.lower()) for e in r["en"] if len(e) > 2), default=0)
        where = "#".join(x for x in r.get("md_link", r["link"]) if x)
        if cnt == 0:
            issues.append(("一般", "0-map/0.8", f"{r['anchor']}：目标 {where} 里没有出现“{' / '.join(names)}”", ""))
        elif cnt == 1:
            n_once += 1
            issues.append(("人工看", "0-map/0.8", f"{r['anchor']}：目标 {where} 里只出现 1 次，可能只是提到", ""))
    # B / C. 对照对
    gl_zh = {z for r in rows for z in r["zh"]}
    gl_en = {e.lower() for r in rows for e in r["en"]}
    pairs = collections.defaultdict(lambda: collections.defaultdict(set))  # zh -> en -> pages
    for p, t in texts.items():
        if p.startswith("0-map/0.8"):
            continue
        for m in PAIR.finditer(body(t)):
            zh = STOP_PREFIX.sub("", m.group(1))
            en = m.group(2).strip()
            if not re.search(r"[A-Za-z]{2}", en) or re.match(r"^(?:L\d|v\d|n\.|e\.g)", en):
                continue
            # 已知中文词：取术语表里能匹配的最长后缀
            hit = max((z for z in gl_zh if zh.endswith(z)), key=len, default=None)
            pairs[hit or zh][en].add(p)
    n_var = 0
    for zh, ens in sorted(pairs.items()):
        low = collections.defaultdict(set)
        for e in ens:
            low[re.sub(r"[\s\-]+", " ", e.lower())].add(e)
        if len(low) > 1 and zh in gl_zh:
            n_var += 1
            det = "；".join(f"{e}（{len(ps)} 页：{', '.join(sorted(ps)[:3])}{'…' if len(ps) > 3 else ''}）" for e, ps in sorted(ens.items()))
            issues.append(("人工看", "全站", f"“{zh}”的英文写法不一", det))
        elif len(ens) > 1 and len(low) == 1 and zh in gl_zh:
            issues.append(("建议", "全站", f"“{zh}”的英文只差大小写或连字符", "、".join(sorted(ens))))
    n_cand = 0
    for zh, ens in sorted(pairs.items()):
        if zh in gl_zh or len(zh) < 2:
            continue
        pages = set().union(*ens.values())
        if len(pages) < a.min_pages:
            continue
        if all(e.lower() in gl_en for e in ens):
            continue
        n_cand += 1
        issues.append(("候选", "全站", f"{zh}（{' / '.join(sorted(ens))}）", f"{len(pages)} 页：{', '.join(sorted(pages)[:4])}{'…' if len(pages) > 4 else ''}"))
    for sev, where, what, extra in issues:
        print(f"{sev}\t{where}\t{what}\t{extra}")
    c = collections.Counter(i[0] for i in issues)
    print(f"[glossary] 词条 {len(rows)}（有站内链接 {n_link}）；指向：一般 {c['一般']}、只出现 1 次 {n_once}；"
          f"英文写法不一 {n_var}；候选 {n_cand}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
