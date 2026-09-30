// sphinxcontrib-mermaid 以 ES module 方式 `import mermaid from ...` 加载 Mermaid。
// 这里复用 T-SITE-02 的 UMD 构建 mermaid.min.js（11.17.2）。它必须作为经典脚本执行：
// 在 module 作用域里它的顶层 var 不是全局变量，最后一行读取 globalThis 上的命名空间会失败。
// 所以用 <script> 标签加载，等它设置好 globalThis.mermaid 后再导出。
await new Promise((resolve, reject) => {
  const script = document.createElement("script");
  script.src = new URL("./mermaid.min.js", import.meta.url).href;
  script.onload = resolve;
  script.onerror = reject;
  document.head.appendChild(script);
});
export default globalThis.mermaid;
