"""T-AUDIT-02b：手机宽度（默认 390 px）下页面是否被撑破。

在构建好的 HTML 上，用 headless Chrome 打开同源测试页，逐页用宽度为 390 的 iframe 加载（iframe 的宽度就是页面视口，
主题的移动端媒体查询按它生效），等 Mermaid 渲染完后量：
  - 页面级：documentElement.scrollWidth − clientWidth > 1 即出现水平滚动条（"撑破"）；
    主题的 .bd-article-container 自带 overflow-x:auto，超宽元素会让整篇正文横滚而页面本身不出滚动条，
    所以它的 scrollWidth − clientWidth > 1 也算撑破；
  - 元素级：右边缘超出视口、且没有任何祖先把它裁掉或放进横向滚动容器（overflow-x 不是 visible）的元素，
    只报最外层的那个（它的父元素没有超出），给出标签、class、宽度与开头的文字；
  - 分类统计：正文表格 / 代码块 / Mermaid 图各有多少个、其中多少个比所在容器宽（靠横向滚动显示，算正常）、
    多少个真的超出视口。

用法：python3 reviews/scripts/audit-mobile.py HTML_DIR [--width 390] [--pages LIST_FILE] [--only 子串]
  LIST_FILE 每行一个 docs/ 下的 .md 路径（如 docs/2-usd-kit/2.8-nucleus.md），不给就量全部正式页。
需要 google-chrome；起 127.0.0.1 的临时 http 服务，结束时按 PID 关掉。会在 HTML_DIR 写临时测试页，用完删掉。
局限：只看水平方向；"能滚动"不等于"好读"，很宽的表在手机上要滚很远，这类只列出宽度供人工判断。
"""
import argparse, html, json, os, re, socket, subprocess, sys, time

HARNESS = r"""<!doctype html><html><head><meta charset="utf-8"></head><body>
<iframe id="f" style="width:__W__px;height:900px;border:0"></iframe>
<script>
const pages = __PAGES__;
const sleep = ms => new Promise(r => setTimeout(r, ms));
function clipped(win, el, stop) {
  // .bd-article-container 自带 overflow-x:auto，被它"接住"的元素会让整篇正文一起横滚，仍算撑破，所以到它为止
  for (let a = el.parentElement; a && a !== stop && !(a.classList && a.classList.contains("bd-article-container")); a = a.parentElement) {
    const o = win.getComputedStyle(a).overflowX;
    if (o !== "visible") return true;
  }
  return false;
}
function desc(el) {
  const cls = (el.className && el.className.baseVal !== undefined) ? el.className.baseVal : (el.className || "");
  return `${el.tagName.toLowerCase()}${el.id ? "#" + el.id : ""}${cls ? "." + String(cls).trim().split(/\s+/).slice(0, 3).join(".") : ""}`;
}
function probe(win, doc, W) {
  const de = doc.documentElement;
  const ac = doc.querySelector(".bd-article-container");
  const res = {overflow: de.scrollWidth - de.clientWidth, article_overflow: ac ? ac.scrollWidth - ac.clientWidth : 0, vw: win.innerWidth, offenders: [], tables: [0, 0, 0], pre: [0, 0, 0], mermaid: [0, 0, 0]};
  const vw = ac ? ac.getBoundingClientRect().right : de.clientWidth;
  const all = [...doc.body.querySelectorAll("*")];
  const out = new Set(all.filter(e => {
    const r = e.getBoundingClientRect();
    return r.width > 0 && r.right > vw + 1 && win.getComputedStyle(e).position !== "fixed" && !clipped(win, e, doc.body);
  }));
  for (const e of out) {
    if (out.has(e.parentElement)) continue;
    const r = e.getBoundingClientRect();
    res.offenders.push({el: desc(e), right: Math.round(r.right), w: Math.round(r.width),
      text: (e.textContent || "").trim().replace(/\s+/g, " ").slice(0, 60),
      path: (() => { const p = []; for (let a = e.parentElement; a && a !== doc.body && p.length < 4; a = a.parentElement) p.push(desc(a)); return p.join(" < "); })()});
  }
  // 文字本身溢出（无空格的长串是纯文本时，没有子元素的盒子超出，只能看块元素自己的 scrollWidth）
  (doc.querySelector(".bd-article") || doc.body).querySelectorAll("p, li, dd, dt, h1, h2, h3, h4, figcaption, .caption-text").forEach(e => {
    if (e.closest(".pst-scrollable-table-container, pre, .highlight")) return;
    if (win.getComputedStyle(e).overflowX !== "visible") return;
    if (e.scrollWidth > e.clientWidth + 1 && e.getBoundingClientRect().left + e.scrollWidth > vw + 1 && !clipped(win, e, doc.body)
        && ![...e.children].some(c => out.has(c))) {
      res.offenders.push({el: desc(e) + "（文字溢出）", right: Math.round(e.getBoundingClientRect().left + e.scrollWidth), w: e.scrollWidth,
        text: (e.textContent || "").trim().replace(/\s+/g, " ").slice(0, 60), path: desc(e.parentElement)});
    }
  });
  const art = doc.querySelector(".bd-article") || doc.body;
  const count = (sel, key, inner) => art.querySelectorAll(sel).forEach(el => {
    const x = inner ? (el.querySelector(inner) || el) : el;
    res[key][0]++;
    const box = (el.parentElement || el).getBoundingClientRect();
    if (x.scrollWidth > x.clientWidth + 1 || x.getBoundingClientRect().width > box.width + 1) res[key][1]++;
    if (x.getBoundingClientRect().right > vw + 1 && !clipped(win, x, doc.body)) res[key][2]++;
  });
  count("table", "tables");
  count("pre:not(.mermaid)", "pre");
  count("pre.mermaid, div.mermaid", "mermaid", "svg");
  return res;
}
(async () => {
  const out = {};
  const ready = doc => [...doc.querySelectorAll("pre.mermaid, div.mermaid")].every(e => {
    const s = e.querySelector("svg"); return s && s.viewBox && s.viewBox.baseVal && s.viewBox.baseVal.width > 0; });
  for (const p of pages) {
    document.getElementById("f").remove();
    const f = document.createElement("iframe");
    f.id = "f"; f.style.cssText = "width:__W__px;height:900px;border:0";
    const loaded = new Promise(r => { f.onload = r; });
    f.src = p; document.body.prepend(f);
    await loaded;
    const doc = f.contentDocument, win = f.contentWindow;
    for (let t = 0; t < 60 && !ready(doc); t++) await sleep(250);
    await sleep(600);
    try { out[p] = probe(win, doc, __W__); out[p].mermaid_ready = ready(doc); } catch (e) { out[p] = {error: String(e)}; }
  }
  document.body.setAttribute("data-probe", JSON.stringify(out));
})();
</script></body></html>"""


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--width", type=int, default=390)
    ap.add_argument("--pages", help="页面清单文件，每行一个 docs/…/*.md")
    ap.add_argument("--only")
    a = ap.parse_args()
    root = os.path.abspath(a.html)
    if a.pages:
        pages = []
        for line in open(a.pages, encoding="utf-8"):
            line = line.strip()
            if line.endswith(".md"):
                pages.append(re.sub(r"^docs/", "", line)[:-3] + ".html")
    else:
        pages = []
        for d, ds, fs in os.walk(root):
            ds[:] = [x for x in ds if not x.startswith("_")]
            for f in fs:
                if f.endswith(".html") and f not in ("genindex.html", "search.html") and not f.startswith("_audit"):
                    pages.append(os.path.relpath(os.path.join(d, f), root))
    pages.sort()
    if a.only:
        pages = [p for p in pages if a.only in p]
    port = free_port()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "-d", root],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    name = f"_audit_mobile_{a.width}.html"
    try:
        time.sleep(1)
        open(os.path.join(root, name), "w", encoding="utf-8").write(
            HARNESS.replace("__W__", str(a.width)).replace("__PAGES__", json.dumps(pages)))
        r = subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-first-run", "--password-store=basic",
                            f"--window-size={a.width + 40},1000", "--virtual-time-budget=600000",
                            "--dump-dom", f"http://127.0.0.1:{port}/{name}"],
                           capture_output=True, text=True, timeout=900)
        m = re.search(r'data-probe="([^"]*)"', r.stdout)
        res = json.loads(html.unescape(m.group(1))) if m else {}
    finally:
        srv.kill()
        if os.path.exists(os.path.join(root, name)):
            os.remove(os.path.join(root, name))
    n_bad = n_err = 0
    tot = {"tables": [0, 0, 0], "pre": [0, 0, 0], "mermaid": [0, 0, 0]}
    for p in pages:
        d = res.get(p)
        if not d or "error" in d:
            n_err += 1
            print(f"ERROR\t{p}\t{(d or {}).get('error', '无结果')}")
            continue
        for k in tot:
            tot[k] = [x + y for x, y in zip(tot[k], d[k])]
        state = "撑破" if d["overflow"] > 1 or d["article_overflow"] > 1 or d["offenders"] else "正常"
        n_bad += state == "撑破"
        print(f"{state}\t{p}\t水平溢出 页面 {d['overflow']} / 正文 {d['article_overflow']} px\t表格 {d['tables'][0]}（需横滚 {d['tables'][1]}，超出视口 {d['tables'][2]}）"
              f"\t代码块 {d['pre'][0]}（需横滚 {d['pre'][1]}，超出 {d['pre'][2]}）\tMermaid {d['mermaid'][0]}（超出 {d['mermaid'][2]}）"
              + ("" if d.get("mermaid_ready", True) else "\tMermaid 未渲染完"))
        for o in d["offenders"]:
            print(f"  超出\t{o['el']}\tright {o['right']} / w {o['w']}\t{o['path']}\t{o['text']}")
    print(f"[mobile] 宽度 {a.width}px；页面 {len(pages)}；撑破 {n_bad}；出错 {n_err}；"
          f"表格 {tot['tables'][0]}（需横滚 {tot['tables'][1]}，超出视口 {tot['tables'][2]}）；"
          f"代码块 {tot['pre'][0]}（需横滚 {tot['pre'][1]}，超出 {tot['pre'][2]}）；Mermaid {tot['mermaid'][0]}（超出 {tot['mermaid'][2]}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
