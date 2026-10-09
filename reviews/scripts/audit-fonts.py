"""T-AUDIT-01 检查 4：图中文字的最小渲染字号（D-025：≥ 12px，1440 与 2560 两档）。

在构建好的 HTML 上，用 headless Chrome 打开一个同源测试页，逐页用 iframe（宽度 = 档位）加载，
等 Mermaid 渲染完后量：
  - Mermaid 图：每个文字元素的 computed font-size × (渲染宽度 / viewBox 宽度)，取最小值
    （与 reviews/scripts/diagram-fontprobe.js 同一口径）；
  - 正文里的 <img>：渲染宽度 / 原始宽度（位图里的字号无法从 DOM 量，缩放比 < 1 的列出来人工看）。

用法：python3 reviews/scripts/audit-fonts.py HTML_DIR [--widths 1440,2560]
需要 google-chrome。会在 HTML_DIR 根目录写一个 _audit_fonts.html（HTML_DIR 应是临时构建目录），
起一个 127.0.0.1 的临时 http 服务，结束时按 PID 关掉。
"""
import argparse, html, json, os, re, socket, subprocess, sys, time

HARNESS = r"""<!doctype html><html><head><meta charset="utf-8"></head><body>
<iframe id="f" style="width:__W__px;height:1000px;border:0"></iframe>
<script>
const pages = __PAGES__;
const sleep = ms => new Promise(r => setTimeout(r, ms));
function probe(win, doc) {
  const res = {mermaid: [], img: []};
  const art = doc.querySelector(".bd-article") || doc.body;
  art.querySelectorAll("pre.mermaid, div.mermaid").forEach((pre, i) => {
    const s = pre.querySelector("svg");
    if (!s) { res.mermaid.push({i: i + 1, skip: "未渲染出 svg"}); return; }
    const vb = s.viewBox && s.viewBox.baseVal;
    if (!vb || vb.width < 50) { res.mermaid.push({i: i + 1, skip: "无 viewBox：" + s.outerHTML.slice(0, 160)}); return; }
    const r = s.getBoundingClientRect();
    const scale = r.width / vb.width;
    const px = [...s.querySelectorAll("text, foreignObject span, foreignObject div, foreignObject p")]
      .filter(e => e.textContent.trim() && !e.querySelector("span,div,p"))
      .map(e => parseFloat(win.getComputedStyle(e).fontSize) * scale).filter(v => v > 0).sort((a, b) => a - b);
    if (!px.length) { res.mermaid.push({i: i + 1, skip: `量不到文字（渲染宽 ${r.width.toFixed(0)}）`}); return; }
    res.mermaid.push({i: i + 1, scale: +scale.toFixed(3), min: +px[0].toFixed(1),
      median: +px[Math.floor(px.length / 2)].toFixed(1), h: Math.round(r.height)});
  });
  art.querySelectorAll("img").forEach(im => {
    if (!im.naturalWidth) return;
    res.img.push({src: im.getAttribute("src"), nat: im.naturalWidth, w: Math.round(im.getBoundingClientRect().width),
      scale: +(im.getBoundingClientRect().width / im.naturalWidth).toFixed(3)});
  });
  return res;
}
(async () => {
  const out = {};
  const ready = doc => [...doc.querySelectorAll("pre.mermaid, div.mermaid")].every(e => {
    // Mermaid 逐张渲染，未完成的图先有一个没有 viewBox 的临时 svg，要等全部带上 viewBox
    const s = e.querySelector("svg"); return s && s.viewBox && s.viewBox.baseVal && s.viewBox.baseVal.width > 0; });
  for (const p of pages) {
    // 每页用新的 iframe；连续加载多页时，偶有一张图停在临时 svg 上（单独加载同一页正常），
    // 所以等不到就换一个新 iframe 重载，最多 3 次，次数记在结果里
    for (let attempt = 1; attempt <= 3; attempt++) {
      document.getElementById("f").remove();
      const f = document.createElement("iframe");
      f.id = "f"; f.style.cssText = "width:__W__px;height:1000px;border:0";
      const loaded = new Promise(r => { f.onload = r; });
      f.src = p; document.body.prepend(f);
      await loaded;
      const doc = f.contentDocument, win = f.contentWindow;
      for (let t = 0; t < 80 && !ready(doc); t++) await sleep(250);
      await sleep(800);
      try { out[p] = probe(win, doc); out[p].attempts = attempt; } catch (e) { out[p] = {error: String(e)}; }
      if (ready(doc)) break;
    }
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
    ap.add_argument("--widths", default="1440,2560")
    ap.add_argument("--min", type=float, default=12.0)
    ap.add_argument("--only", help="只量路径含此子串的页面（调试用）")
    a = ap.parse_args()
    root = os.path.abspath(a.html)
    pages = []
    for d, ds, fs in os.walk(root):
        ds[:] = [x for x in ds if not x.startswith("_")]
        for f in fs:
            if f.endswith(".html") and f not in ("genindex.html", "search.html") and not f.startswith("_audit"):
                t = open(os.path.join(d, f), encoding="utf-8").read()
                art = t[t.find("bd-article"):]
                if 'class="mermaid"' in art or "<img" in art:
                    pages.append(os.path.relpath(os.path.join(d, f), root))
    pages.sort()
    if a.only:
        pages = [p for p in pages if a.only in p]
    port = free_port()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "-d", root],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    results = {}
    try:
        time.sleep(1)
        def run(w, pp):
            name = f"_audit_fonts_{w}.html"
            open(os.path.join(root, name), "w", encoding="utf-8").write(
                HARNESS.replace("__W__", str(w)).replace("__PAGES__", json.dumps(pp)))
            r = subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-first-run",
                                f"--window-size={w + 40},1100", "--virtual-time-budget=600000",
                                "--dump-dom", f"http://127.0.0.1:{port}/{name}"],
                               capture_output=True, text=True, timeout=900)
            os.remove(os.path.join(root, name))
            m = re.search(r'data-probe="([^"]*)"', r.stdout)
            return json.loads(html.unescape(m.group(1))) if m else {}

        for w in [int(x) for x in a.widths.split(",")]:
            results[w] = run(w, pages)
            # 同一个 Chrome 里连续加载多页时，个别图会停在未完成的临时 svg 上（单独加载同一页正常，
            # 原因未查）。这些页单独再开一个 Chrome 重量一次，结果里记 rerun。
            for p in pages:
                if any("skip" in m for m in results[w].get(p, {}).get("mermaid", [])) or p not in results[w]:
                    again = run(w, [p]).get(p)
                    if again:
                        again["rerun"] = True
                        results[w][p] = again
    finally:
        srv.kill()
    n_fig = n_img = 0
    bad, small_img = [], []
    for w, res in results.items():
        for p in pages:
            d = res.get(p, {"error": "无结果"})
            if "error" in d:
                bad.append(f"ERROR\t{w}\t{p}\t{d['error']}")
                continue
            for m in d["mermaid"]:
                if "skip" in m:
                    bad.append(f"ERROR\t{w}\t{p}\t图{m['i']}：{m['skip']}")
                    continue
                n_fig += 1
                line = (f"{w}\t{p}\t图{m['i']}\tmin {m['min']}px\tmedian {m['median']}px\tscale {m['scale']}\th {m['h']}"
                        + ("\t(单独重量)" if d.get("rerun") else ""))
                (bad.append("SMALL\t" + line) if m["min"] < a.min else None)
                print("FIG\t" + line)
            for im in d["img"]:
                n_img += 1
                line = f"{w}\t{p}\t{im['src']}\t{im['w']}/{im['nat']}px\tscale {im['scale']}"
                print("IMG\t" + line)
                if im["scale"] < 0.999 and not im["src"].endswith(".svg"):
                    small_img.append(line)
    for b in bad:
        print(b)
    print(f"[fonts] 页面 {len(pages)}；档位 {list(results)}；Mermaid 图×档 {n_fig}，最小字号 < {a.min}px 的 "
          f"{sum(b.startswith('SMALL') for b in bad)}；位图×档 {n_img}，被缩小显示的 {len(small_img)}（需人工看字）；"
          f"出错 {sum(b.startswith('ERROR') for b in bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
