---
title: 渲染检查页
verified: "n/a"
orphan: true
updated: 2026-09-30
sources_checked: 2026-09-30
---

# 渲染检查页

本页不进导航，用于确认站点的 Markdown 扩展渲染正常，也可作为写作模板参考。

:::{admonition} 学习目标
:class: lead-goals

读完本页你能：

- 确认 admonition、Mermaid、代码 tabs、脚注均可渲染
:::

:::{admonition} 前置知识
:class: lead-prereq

- 无
:::

## Mermaid

下图是一个自底向上的依赖示意，用于检查 Mermaid 在浅色/深色模式下的可读性。

```{mermaid}
flowchart BT
    A[GPU 驱动 / CUDA] --> B[Omniverse Kit]
    B --> C[Isaac Sim]
    C --> D[Isaac Lab]
    D -.->|可选| E[RL 库]
```

## Admonition

:::{admonition} note
:class: note

说明性补充。
:::

:::{admonition} tip
:class: tip

实用技巧。
:::

:::{admonition} warning
:class: warning

常见坑，"常见坑"一节的每一条都用这种框。
:::

:::{admonition} danger
:class: danger

可能造成数据丢失或硬件损坏的操作。
:::

:::{dropdown} 可折叠（pymdownx.details）

折叠内容。
:::

## 代码 tabs

::::{tab-set}

:::{tab-item} Python

```python
import torch

x = torch.zeros(4, device="cuda")
```
:::

:::{tab-item} Shell

```bash
echo "hello"
```
:::

::::

## 公式

行内公式：关节驱动力矩 $\tau = K_p (q^* - q) + K_d (\dot q^* - \dot q)$，字面美元符号写成 \$5 或 `$5`。

独立公式：

$$
\tau = K_p \,(q^* - q) + K_d \,(\dot q^* - \dot q)
$$

其中 $K_p$ 为刚度（N·m/rad），$K_d$ 为阻尼（N·m·s/rad），$q^*$、$\dot q^*$ 为目标位置与目标速度，$q$、$\dot q$ 为当前值。

长公式（检查窄屏下是否撑破正文）：

$$
J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_{t=0}^{T} \gamma^t\, r(s_t, a_t)\right] + \lambda_1 \lVert \theta \rVert_2^2 + \lambda_2 \sum_{i=1}^{N} \max\left(0,\; \lvert q_i \rvert - q_i^{\max}\right)^2 + \lambda_3 \sum_{t=0}^{T-1} \lVert a_{t+1} - a_t \rVert^2
$$

## 脚注

这是一句带来源的断言[^1]。

[^1]: 来源示例：[MkDocs Material 文档](https://squidfunk.github.io/mkdocs-material/)。

## 常见坑

（无）

## 延伸阅读

- [MkDocs Material Reference](https://squidfunk.github.io/mkdocs-material/reference/)

## 版本说明

与 Isaac 版本无关。
