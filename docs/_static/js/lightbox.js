// 正文图片点击放大（T-SITE-14）：在当前页打开悬浮层，不跳转到图片文件。
// 作用范围：.bd-article 内的 <img>；排除 Mermaid 图（是 SVG，不是 <img>）、徽章与图标类小图（显示宽高都小于 48px，或在 .sd-badge 等徽章里）。
// 关闭：右上角 ×、ESC、点击遮罩。打开时禁止页面滚动，关闭后焦点回到原图。没有 JS 时图片照常显示。
(() => {
  const MIN = 48;
  let box = null, last = null;
  const close = () => {
    if (!box) return;
    box.remove(); box = null;
    document.documentElement.classList.remove("academy-lightbox-open");
    document.removeEventListener("keydown", onKey);
    if (last) last.focus({ preventScroll: true });
  };
  const onKey = (e) => { if (e.key === "Escape") close(); };
  const open = (img) => {
    last = img;
    box = document.createElement("div");
    box.className = "academy-lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", img.alt || "图片");
    const big = document.createElement("img");
    big.src = img.currentSrc || img.src;
    big.alt = img.alt;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "academy-lightbox-close";
    btn.setAttribute("aria-label", "关闭");
    btn.textContent = "×";
    box.append(big, btn);
    box.addEventListener("click", (e) => { if (e.target !== big) close(); });  // 遮罩与 × 都关闭，点图本身不关
    document.body.append(box);
    document.documentElement.classList.add("academy-lightbox-open");
    document.addEventListener("keydown", onKey);
    btn.focus();
  };
  const eligible = (img) =>
    img.closest(".bd-article") && !img.closest(".sd-badge, .badge, .academy-lightbox") &&
    (img.width >= MIN || img.height >= MIN);
  // 光标与键盘焦点：每张图加载完（尺寸确定）后再判断，已加载的立即判断
  const mark = (img) => {
    if (!eligible(img)) return;
    img.classList.add("academy-zoomable");
    if (!img.hasAttribute("tabindex")) img.tabIndex = 0;
  };
  const scan = () => document.querySelectorAll(".bd-article img").forEach((img) => {
    if (img.complete) mark(img); else img.addEventListener("load", () => mark(img), { once: true });
  });
  // 点击与回车用事件委托，不依赖脚本执行时机；捕获阶段拦截，外层 <a> 不会跳转
  document.addEventListener("click", (e) => {
    const img = e.target.closest && e.target.closest("img");
    if (!img || !eligible(img)) return;
    e.preventDefault(); e.stopPropagation(); open(img);
  }, true);
  document.addEventListener("keydown", (e) => {
    const img = document.activeElement;
    if ((e.key === "Enter" || e.key === " ") && img && img.tagName === "IMG" && img.classList.contains("academy-zoomable")) { e.preventDefault(); open(img); }
  });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", scan); else scan();
})();
