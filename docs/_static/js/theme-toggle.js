// 颜色模式按钮改为两态：浅 ↔ 深，每点一次就切换（T-SITE-15）。
// pydata-sphinx-theme 0.16 的按钮是三态循环（auto → dark → light），系统为浅色时从 light 要点两次才到 dark。
// 本站默认浅色（D-020），不需要 auto。这里在捕获阶段接管按钮点击，主题自己的 cycleMode 就不会再执行；
// 设置的内容与主题 setTheme() 一致：<html> 的 data-mode / data-theme、下拉菜单的深色类、localStorage 的 mode / theme。
// 没有 JS 时按钮不可用，页面保持默认浅色。
(() => {
  const apply = (mode) => {
    const root = document.documentElement;
    root.dataset.mode = mode;
    root.dataset.theme = mode;
    document.querySelectorAll(".dropdown-menu").forEach((el) => el.classList.toggle("dropdown-menu-dark", mode === "dark"));
    try {
      localStorage.setItem("mode", mode);
      localStorage.setItem("theme", mode);
    } catch (e) {
      /* 无痕模式等情况下 localStorage 不可用，只切换当前页面 */
    }
  };
  // 以前存过 auto 的，立即按站点默认模式（浅色）改写，之后只在两态之间切换。放在顶层立即执行：主题脚本带 defer，
  // 会在 DOMContentLoaded 之前调用 setTheme(data-mode)；先改好，它读到的就是 light，也不会挂上"跟随系统"的监听。
  {
    const root = document.documentElement;
    let stored = null;
    try {
      stored = localStorage.getItem("mode");
    } catch (e) {
      /* 忽略 */
    }
    if (root.dataset.mode === "auto" || stored === "auto") apply(root.dataset.defaultMode === "dark" ? "dark" : "light");
  }
  const setup = () => {
    const root = document.documentElement;
    document.addEventListener(
      "click",
      (e) => {
        if (!e.target.closest || !e.target.closest(".theme-switch-button")) return;
        e.preventDefault();
        e.stopPropagation(); // 捕获阶段拦下，事件不会到达按钮上主题注册的处理函数
        apply(root.dataset.theme === "dark" ? "light" : "dark");
      },
      true,
    );
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setup);
  else setup();
})();
