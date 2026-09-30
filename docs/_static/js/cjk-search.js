// 中文短语搜索（T-SITE-08）。
// Sphinx 的 searchtools.js 只在"非字母字符"处切分查询，连写的中文短语（如"导入路径"）被当成一个词；
// 而索引端 sphinx/search/zh.py 用 jieba.cut_for_search 切分，且只收录长度 > 1 的词。
// 这里在 searchtools.js 之前定义全局 splitQuery（searchtools.js 只在它未定义时才用默认实现）：
// 先按默认规则切分，再把每段中连续的汉字按索引词表做正向最长匹配。
// 匹配不上的单个汉字丢弃（索引端同样不收录单字）；匹配不上的连续多字原样保留，
// 这样查询索引里没有的词时仍然返回 0 条，而不是被放宽成别的词。
(() => {
  const DEFAULT_SPLIT = /[^\p{Letter}\p{Number}_\p{Emoji_Presentation}]+/gu;
  const HAN = /(\p{Script=Han}+)/u;
  const MAX_WORD = 8;

  const inIndex = (word) => {
    const index = typeof Search !== "undefined" ? Search._index : null;
    if (!index) return false;
    return (
      Object.prototype.hasOwnProperty.call(index.terms, word) ||
      Object.prototype.hasOwnProperty.call(index.titleterms, word)
    );
  };

  const segmentHan = (run, out) => {
    if (inIndex(run)) { out.push(run); return; }
    let unmatched = "";
    const flush = () => {
      if (unmatched.length > 1) out.push(unmatched);
      unmatched = "";
    };
    let i = 0;
    while (i < run.length) {
      let found = 0;
      for (let len = Math.min(MAX_WORD, run.length - i); len >= 2; len--) {
        if (inIndex(run.substr(i, len))) { found = len; break; }
      }
      if (found) {
        flush();
        out.push(run.substr(i, found));
        i += found;
      } else {
        unmatched += run[i];
        i += 1;
      }
    }
    flush();
  };

  window.splitQuery = (query) => {
    const out = [];
    query.split(DEFAULT_SPLIT).forEach((token) => {
      if (!token) return;
      token.split(HAN).forEach((part) => {
        if (!part) return;
        if (HAN.test(part)) segmentHan(part, out);
        else out.push(part);
      });
    });
    return out;
  };
})();
