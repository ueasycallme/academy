// 公告条关闭按钮（D-020 用户要求）。
// 点击 × 后隐藏公告条，并在 localStorage 记下"已关闭"；键名包含公告文案的哈希，
// 因此公告文案一改就会重新显示。没有 JS 或 localStorage 不可用时，公告条照常显示。
(() => {
  const hash = (text) => {
    let h = 0;
    for (let i = 0; i < text.length; i++) h = (Math.imul(31, h) + text.charCodeAt(i)) | 0;
    return (h >>> 0).toString(36);
  };
  const setup = () => {
    const bar = document.querySelector(".bd-header-announcement");
    if (!bar) return;
    const text = bar.textContent.trim();
    if (!text) return;
    const key = "academy-announcement-closed-" + hash(text);
    let closed = false;
    try { closed = localStorage.getItem(key) === "1"; } catch (e) { /* 存储不可用时不记忆 */ }
    if (closed) { bar.hidden = true; bar.style.display = "none"; return; }
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "academy-announcement-close";
    btn.setAttribute("aria-label", "关闭公告");
    btn.textContent = "×";
    btn.addEventListener("click", () => {
      bar.hidden = true;
      bar.style.display = "none";
      try { localStorage.setItem(key, "1"); } catch (e) { /* 忽略 */ }
    });
    bar.style.position = "relative";
    bar.appendChild(btn);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setup);
  else setup();
})();
