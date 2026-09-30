// 表格内行内代码的断行点（T-SITE-09）。
// 长类名、长路径没有空格，会把表格列撑宽。这里在 "." "/" "_" 之后插入 <wbr>（可选断行点），
// 让浏览器优先在这些位置换行，而不是在单词中间任意断开。<wbr> 不会被复制，复制出的代码不变。
(() => {
  const BREAK_AFTER = /([./_])(?=.)/g;
  const addBreaks = (code) => {
    const walker = document.createTreeWalker(code, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => {
      const parts = node.textContent.split(BREAK_AFTER);
      if (parts.length < 2) return;
      const frag = document.createDocumentFragment();
      parts.forEach((part) => {
        if (!part) return;
        frag.appendChild(document.createTextNode(part));
        if (part.length === 1 && "./_".includes(part)) frag.appendChild(document.createElement("wbr"));
      });
      node.replaceWith(frag);
    });
  };
  const run = () => document.querySelectorAll(".bd-article table code").forEach(addBreaks);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
})();
