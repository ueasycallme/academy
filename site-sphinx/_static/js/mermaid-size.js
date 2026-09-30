// 让 Mermaid 图按原始尺寸显示：sphinxcontrib-mermaid 的样式 `max-width: 100% !important`
// 会覆盖 Mermaid 自己写的 inline max-width（即图的原始宽度），导致小图被放大。
// 这里在每次渲染（含深浅色切换后的重渲染）后，按 viewBox 宽度重新设置带 !important 的 max-width。
(() => {
  const fit = (svg) => {
    const vb = svg.viewBox && svg.viewBox.baseVal;
    if (!vb || !vb.width) return;
    const cap = `min(100%, ${Math.ceil(vb.width)}px)`;
    if (svg.style.getPropertyValue("max-width") !== cap) {
      svg.style.setProperty("max-width", cap, "important");
    }
  };
  const scan = () => document.querySelectorAll("pre.mermaid > svg").forEach(fit);
  const start = () => {
    scan();
    new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
