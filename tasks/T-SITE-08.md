# T-SITE-08 中文短语搜索

状态: 待实现
优先级: P1（上线前）
类型: 基础设施
依赖: T-SITE-06
来源: reviews/T-SITE-03.md（"导入路径""弃用警告"等多词短语返回 0 条）

## 目标

中文连写短语能搜到。

## 必须完成

1. 定位：Sphinx 前端 `searchtools.js` 的 `splitQuery` 不分中文；后端索引已用 jieba 分词。
2. 方案二选一并说明理由：(a) 覆盖 `splitQuery`，前端用与后端一致的规则切分（把连续汉字按 2-gram 或按索引里已有词表切分）；(b) 后端在 `html_search_options` 或自定义 `SearchLanguage` 里把索引改为 2-gram，前端同样 2-gram。以能命中 reviews/T-SITE-03.md 列出的失败用例为准。
3. 测试用例 ≥ 8（含单词、双词短语、中英混合如"Isaac Lab 边界"、英文），结果写附记。
4. 不引入外部搜索服务。

## 附记

（实现/校验 session 写）
