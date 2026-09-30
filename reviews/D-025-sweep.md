# D-025 图字号普查（2026-09-30，工作区构建）

方法：同源 iframe 分别以 1440 / 2560 宽加载全部含 Mermaid 图的页面（14 页），对每张图计算 `getComputedStyle(label).fontSize × (渲染宽度 / viewBox 宽度)`，取最小值。脚本：`reviews/scripts/diagram-fontprobe.js`。

| 页面 | 1440 最小字号 | 2560 最小字号 | 是否满足 D-025（≥ 12 px） |
|---|---|---|---|
| 0.1 overview | 16.0 | 16.0 | ✓ |
| 0.2 layers | 16.0 | 16.0 | ✓ |
| 0.3 lineage | 13.0 | 13.0 | ✓ |
| 0.4 isaac-names | 13.0 | 13.0 | ✓ |
| 0.6 one-step | 14.1 | 16.0 | ✓ |
| **0.7 learning-paths** | **10.3**（缩放 0.64） | 12.1 | ✗（1440） |
| _template-check | 16.0 | 16.0 | ✓ |
| **1.2 version-decision** | **9.4**（缩放 0.59） | **11.0** | ✗（两档） |
| 2.1 why-usd | 16.0 | 16.0 | ✓ |
| 3.1 sim-loop | 12.0（缩放 0.75） | 14.0 | ✓（1440 恰好在线上） |
| 4.1 why-isaac-lab | 16.0 | 16.0 | ✓ |
| 4.7 actuators | 15.5 | 16.0 | ✓ |
| 4.9 manager-based-env（工作区现状） | 14.6 | 16.0 | ✓（待 T-4.9 复核时确认） |
| 4.10 observation-action（草稿） | 12.7 | 15.0 | ✓（待校验时确认） |
