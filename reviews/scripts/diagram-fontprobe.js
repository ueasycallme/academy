// rendered font px = computed font-size of each label * (rendered svg width / viewBox width)
window.__probeFonts = () => {
  const out = [];
  document.querySelectorAll(".bd-article svg").forEach((s, i) => {
    const vb = s.viewBox && s.viewBox.baseVal;
    if (!vb || vb.width < 50 || !s.closest(".mermaid, pre.mermaid, div.mermaid")) return;
    const scale = s.getBoundingClientRect().width / vb.width;
    const els = [...s.querySelectorAll("text, foreignObject span, foreignObject div, foreignObject p")]
      .filter(e => e.textContent.trim());
    const px = els.map(e => parseFloat(getComputedStyle(e).fontSize) * scale).filter(v => v > 0);
    if (!px.length) return;
    px.sort((a, b) => a - b);
    out.push(`fig${i+1}: scale=${scale.toFixed(2)} min=${px[0].toFixed(1)}px median=${px[Math.floor(px.length/2)].toFixed(1)}px h=${Math.round(s.getBoundingClientRect().height)}`);
  });
  return out.join(" ; ") || "none";
};
