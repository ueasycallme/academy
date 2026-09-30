"""Material for MkDocs Markdown → MyST Markdown 机械转换（原型用）。

用法：
    python tools/md2myst.py ../docs/0-map/0.2-layers.md 0-map/0.2-layers.md

处理的语法（对照表见 MIGRATION-NOTES.md）：
    !!! type "标题"        → :::{admonition} 标题 / :class: <映射后的类>
    ??? type "标题"        → :::{dropdown} 标题（sphinx-design）
    === "标签"             → ::::{tab-set} / :::{tab-item} 标签
    ```mermaid            → ```{mermaid}
    YAML frontmatter、脚注、GFM 表格、相对 .md 链接：MyST 原生支持，原样保留

只做行级机械转换，不理解语义；转换后请跑 `sphinx-build -W` 检查。
"""

from __future__ import annotations

import re
import sys

# Material admonition 类型 → pydata-sphinx-theme 已有配色的类
ADMONITION_CLASS = {
    "note": "note",
    "tip": "tip",
    "warning": "warning",
    "danger": "danger",
    "abstract": "hint",  # 学习目标
    "info": "note",  # 前置知识
}

ADMON_RE = re.compile(r'^(?P<indent>\s*)(?P<mark>!!!|\?\?\?\+?)\s+(?P<type>\w+)(?:\s+"(?P<title>[^"]*)")?\s*$')
TAB_RE = re.compile(r'^(?P<indent>\s*)===\s+"(?P<label>[^"]*)"\s*$')
FENCE_RE = re.compile(r"^(?P<indent>\s*)(?P<fence>`{3,})(?P<info>.*)$")


def _block(lines: list[str], start: int, indent: str) -> tuple[list[str], int]:
    """收集 start 起、缩进比 indent 多 4 个空格的块（允许空行），返回去缩进后的行和结束位置。"""
    inner = indent + "    "
    body: list[str] = []
    i = start
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            body.append("")
            i += 1
            continue
        if not line.startswith(inner):
            break
        body.append(line[len(inner) :])
        i += 1
    while body and body[-1] == "":
        body.pop()
    return body, i


def convert(lines: list[str], depth: int = 0) -> list[str]:
    out: list[str] = []
    i = 0
    in_fence = None
    while i < len(lines):
        line = lines[i]
        m = FENCE_RE.match(line)
        if m and in_fence is None:
            in_fence = m.group("fence")
            info = m.group("info").strip()
            if info == "mermaid":
                out.append(f"{m.group('indent')}{in_fence}{{mermaid}}")
            else:
                out.append(line)
            i += 1
            continue
        if in_fence is not None:
            if line.strip() == in_fence:
                in_fence = None
            out.append(line)
            i += 1
            continue

        m = ADMON_RE.match(line)
        if m:
            indent = m.group("indent")
            body, i = _block(lines, i + 1, indent)
            body = convert(body, depth + 1)
            colons = ":" * (3 + _nesting(body))
            title = m.group("title") or m.group("type").capitalize()
            if m.group("mark").startswith("???"):
                out.append(f"{indent}{colons}{{dropdown}} {title}")
            else:
                cls = ADMONITION_CLASS.get(m.group("type"), m.group("type"))
                out.append(f"{indent}{colons}{{admonition}} {title}")
                out.append(f"{indent}:class: {cls}")
            out.append("")
            out.extend(indent + b if b else "" for b in body)
            out.append(f"{indent}{colons}")
            out.append("")
            continue

        m = TAB_RE.match(line)
        if m:
            indent = m.group("indent")
            items: list[tuple[str, list[str]]] = []
            while i < len(lines):
                t = TAB_RE.match(lines[i])
                if not t or t.group("indent") != indent:
                    break
                body, i = _block(lines, i + 1, indent)
                items.append((t.group("label"), convert(body, depth + 1)))
                while i < len(lines) and lines[i].strip() == "" and i + 1 < len(lines) and TAB_RE.match(lines[i + 1]):
                    i += 1
            inner = ":" * (3 + max(_nesting(b) for _, b in items))
            outer = inner + ":"
            out.append(f"{indent}{outer}{{tab-set}}")
            out.append("")
            for label, body in items:
                out.append(f"{indent}{inner}{{tab-item}} {label}")
                out.extend(indent + b if b else "" for b in body)
                out.append(f"{indent}{inner}")
                out.append("")
            out.append(f"{indent}{outer}")
            out.append("")
            continue

        out.append(line)
        i += 1
    return out


def _nesting(body: list[str]) -> int:
    """块内已有冒号围栏的最大额外层数，外层围栏需要比它多一个冒号。"""
    depth = 0
    for b in body:
        m = re.match(r"^\s*(:{3,})\{", b)
        if m:
            depth = max(depth, len(m.group(1)) - 2)
    return depth


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        lines = f.read().split("\n")
    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(convert(lines)))


if __name__ == "__main__":
    main()
