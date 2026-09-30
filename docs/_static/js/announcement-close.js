// 公告条关闭按钮（D-020 用户要求）。
// 另外负责把公告条中的站内链接改写为相对路径（见 localizeLinks）。
// 点击 × 后隐藏公告条，并在 localStorage 记下"已关闭"；键名包含公告文案的哈希，
// 因此公告文案一改就会重新显示。没有 JS 或 localStorage 不可用时，公告条照常显示。
(() => {
  const hash = (text) => {
    let h = 0;
    for (let i = 0; i < text.length; i++) h = (Math.imul(31, h) + text.charCodeAt(i)) | 0;
    return (h >>> 0).toString(36);
  };
  // 把公告条里带 data-academy-local 的链接改写为相对当前页面的路径（按 Sphinx 写在 <html> 上的 data-content_root），
  // 这样站点部署在域名根目录、子路径或本地预览时都能跳到本站页面。
  const localizeLinks = (bar) => {
    const root = document.documentElement.dataset.content_root;
    if (root === undefined) return;
    bar.querySelectorAll("a[data-academy-local]").forEach((a) => {
      a.setAttribute("href", root + a.dataset.academyLocal);
    });
  };
  const setup = () => {
    const bar = document.querySelector(".bd-header-announcement");
    if (!bar) return;
    localizeLinks(bar);
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
