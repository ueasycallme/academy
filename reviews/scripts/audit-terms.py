"""T-AUDIT-01 检查 3：术语中英使用（D-018 / CONVENTIONS 第 3 节）。

对 0.8 术语表里"中文术语"列含汉字、"英文"列为英文的词条（即"用中文，首次出现附英文"一类），
在每个正式页的正文里检查：
  A. 全页第一次出现该中文术语时，紧跟"（English）"；
  B. 之后正文里是否又单独用了英文词（不在括号对照里）。
另查"首字母大写"类：Prim、Term 在正文里写成小写 prim / term。

正文 = 去掉 frontmatter、代码块、行内代码、标题行、"学习目标"与"前置知识"框、脚注定义、HTML 注释、链接 URL 之后的文本。
中文术语是更长术语的一部分时（如"关节"在"mimic 关节"里）不算出现。
这是启发式检查：A 类假阳性少，B 类噪声大（类名、官方页面标题会被计入），报告里只作抽样参考。

用法：python3 reviews/scripts/audit-terms.py [--repo DIR] [--ref HEAD] [-v]
"""
import argparse, collections, re, subprocess, sys

CJK = re.compile(r"[一-鿿]")
PLACEHOLDER = ("<!-- placeholder:", "待写，见 OUTLINE")


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=True).stdout


def glossary(text):
    terms = []
    for line in text.splitlines():
        m = re.match(r"\| \[\*\*(.+?)\*\*\]\{#(term-[\w-]+)\} \| ([^|]+) \|[^|]*\| (?:\[[^\]]*\]\(\.\./([^)]+)\))?", line)
        if not m:
            continue
        zh, anchor, en, home = m.group(1).strip("`"), m.group(2), m.group(3).strip(), m.group(4) or ""
        zhs, ens = [s.strip() for s in zh.split(" / ")], [s.strip() for s in en.split(" / ")]
        if len(zhs) != len(ens):
            zhs, ens = [zhs[0]], [ens[0]]
        for z, e in zip(zhs, ens):
            ab = re.search(r"\((.*?)\)$", e)
            e = re.sub(r"\s*\(.*?\)$", "", e)  # "Discount Factor (γ)" -> "Discount Factor"
            terms.append(dict(zh=z, en=e, abbr=ab.group(1) if ab else "", anchor=anchor, home=home, kind="zh" if CJK.search(z) and z.lower() != e.lower() else "en"))
    return terms


def prose(text):
    """返回 [(行号, 文本)]，只含正文。"""
    out, lines = [], text.splitlines()
    i = 0
    if lines and lines[0].strip() == "---":
        i = lines.index("---", 1) + 1
    code = None          # 代码围栏 ``` / ~~~ ，整块跳过
    colon = []           # 冒号围栏栈：[(围栏, 是否前置知识框)]
    in_comment = False
    for n in range(i, len(lines)):
        l = lines[n]
        s = l.strip()
        if code:
            if s == code:
                code = None
            continue
        m = re.match(r"(`{3,}|~{3,})", s)
        if m:
            code = m.group(1)
            continue
        m = re.match(r"(:{3,})(.*)", s)
        if m:
            if colon and m.group(2).strip() == "" and len(m.group(1)) == len(colon[-1][0]):
                colon.pop()
            else:
                colon.append([m.group(1), False])
            continue
        if colon and s.startswith(":"):
            if s.startswith(":class:") and ("lead-prereq" in s or "lead-goals" in s):
                colon[-1][1] = True
            continue
        if any(c[1] for c in colon):
            continue
        if in_comment or "<!--" in l:
            in_comment = "-->" not in l
            continue
        if s.startswith("#") or re.match(r"\[\^[^\]]+\]:", s) or re.match(r"\((term-)?[\w.-]+\)=", s):
            continue
        l = re.sub(r"`[^`]*`", " ", l)
        l = re.sub(r"\[\^[^\]]+\]", " ", l)  # 脚注引用 [^term]
        l = re.sub(r"\]\([^)]*\)", "]", l)
        l = re.sub(r"\]\{[^}]*\}", "]", l)
        l = re.sub(r"https?://\S+", " ", l)
        out.append((n + 1, l))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    terms = glossary(git(a.repo, "show", f"{a.ref}:docs/0-map/0.8-glossary.md"))
    # D-018：“扩展”可以单独使用，不要求附 Extension
    zh_terms = [t for t in terms if t["kind"] == "zh" and t["zh"] != "扩展"]
    all_zh = sorted({t["zh"] for t in terms if CJK.search(t["zh"])}, key=len, reverse=True)
    files = [p for p in git(a.repo, "ls-tree", "-r", "--name-only", a.ref, "docs").splitlines()
             if p.endswith(".md") and "/_" not in p and not p.endswith(("0.8-glossary.md", "MIGRATION-NOTES.md"))]
    n_pages = n_checks = 0
    first_bad, en_after, case_bad = [], collections.defaultdict(list), []
    for p in files:
        text = git(a.repo, "show", f"{a.ref}:{p}")
        if any(m in text for m in PLACEHOLDER):
            continue
        n_pages += 1
        body = prose(text)
        joined = "\n".join(l for _, l in body)
        offsets, acc = [], 0
        for n, l in body:
            offsets.append((acc, n))
            acc += len(l) + 1

        def lineno(pos):
            ln = offsets[0][1]
            for o, n in offsets:
                if o > pos:
                    break
                ln = n
            return ln

        for t in zh_terms:
            z = t["zh"]
            longer = [L for L in all_zh if len(L) > len(z) and z in L]
            pos = None
            for m in re.finditer(re.escape(z), joined):
                inside = False
                for L in longer:
                    k = L.index(z)
                    if joined[max(0, m.start() - k): m.start() - k + len(L)] == L:
                        inside = True
                        break
                if not inside:
                    pos = m.start()
                    break
            if pos is None:
                continue
            n_checks += 1
            en_word = t["en"].split()[0].lower()

            def paired(at):
                after = re.sub(r"^\**\]?\**", "", joined[at + len(z): at + len(z) + 80])
                # 允许术语后紧跟至多 4 个汉字再接括号，如"执行器模型（actuator）""稀疏奖励（sparse reward）"
                ok = re.match(r"[\u4e00-\u9fff]{0,4}\**\s?[（(]([^）)]*)", after)
                return ok.group(1) if ok and re.search(r"[A-Za-z]", ok.group(1)) else None

            got = paired(pos)
            if got is None or (en_word not in got.lower() and t["en"].lower() not in got.lower()
                               and not (t["abbr"] and t["abbr"].lower() in got.lower())):
                elsewhere = any(paired(m.start()) for m in re.finditer(re.escape(z), joined) if m.start() != pos)
                note = "" if got is None else f"（括号里写的是：{got[:30]}）"
                first_bad.append((p[5:], lineno(pos), z, t["en"] + note,
                                  p.endswith(t["home"]) if t["home"] else False, elsewhere))
            # B：首次之后单独出现英文（不在紧跟中文术语的括号里）
            rest = joined[pos + len(z):]
            for m in re.finditer(r"(?<![\w-])" + re.escape(t["en"]) + r"(?![\w-])", rest, re.I):
                pre = rest[max(0, m.start() - 12): m.start()]
                if re.search(r"[（(][^）)]*$", pre):
                    continue  # 括号对照
                en_after[(p[5:], z, t["en"])].append(lineno(pos + len(z) + m.start()))
        for word in ("prim", "term"):
            for n, l in body:
                for m in re.finditer(r"(?<![\w./-])" + word + r"s?(?![\w/-])", l):
                    case_bad.append((p[5:], n, l[max(0, m.start() - 15): m.end() + 15].strip()))
    for f, n, z, en, home, elsewhere in first_bad:
        print(f"FIRST\t{f}:{n}\t{z}\t应附（{en}）\t{'首次详细讲解页' if home else ''}\t{'页内别处有对照' if elsewhere else '全页无对照'}")
    for (f, z, en), ns in sorted(en_after.items()):
        print(f"ENALONE\t{f}\t{z}/{en}\t{len(ns)} 处\t行 {ns[:6]}")
    for f, n, ctx in case_bad:
        print(f"CASE\t{f}:{n}\t{ctx}")
    print(f"[terms] 词条 {len(terms)}（中文附英文类 {len(zh_terms)}）；正式页 {n_pages}；页×词条 出现 {n_checks}；"
          f"首次未附英文 {len(first_bad)}（其中在首次详细讲解页 {sum(1 for x in first_bad if x[4])}，"
          f"页内别处有对照 {sum(1 for x in first_bad if x[5])}，全页无对照 {sum(1 for x in first_bad if not x[5])}）；"
          f"之后单独用英文 {len(en_after)} 组；Prim/Term 小写 {len(case_bad)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
