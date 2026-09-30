"""从 OUTLINE.md 生成 Sphinx 原型的全站页面树（T-SITE-05）。

- 已有正式页（docs/ 下内容不是"待写"的页面）：用 md2myst 转换后放入对应路径。
- 其余页面：生成占位页（标题 + "待写，见 OUTLINE x.y"）。
- 生成首页 toctree（每个部分一个带 :caption: 的 toctree）与第 6 部分 ①–⑦ 子组的索引页。

用法（在 site-sphinx/ 下）：
    env -u PYTHONPATH .venv/bin/python tools/gen_site.py

目录规则见 CONVENTIONS.md 第 1 节；slug 与 docs/ 已有页面保持一致。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
REPO = SITE.parent
sys.path.insert(0, str(HERE))
from md2myst import convert  # noqa: E402

PART_DIR = {
    "0": "0-map", "1": "1-env", "2": "2-usd-kit", "3": "3-isaacsim", "4": "4-isaaclab",
    "5": "5-rl", "6": "6-galbot", "7": "7-infra", "8": "8-frontier", "9": "9-source", "A": "appendix",
}
SUB_DIR = {"1": "1-asset", "2": "2-scene", "3": "3-sim-align", "4": "4-task", "5": "5-train", "6": "6-eval", "7": "7-deploy"}

# 页面编号 → slug。已在 docs/ 中使用的 slug 保持不变（D-007 / D-011）。
SLUG = {
    "0.1": "overview", "0.2": "layers", "0.3": "lineage", "0.4": "isaac-names", "0.5": "sim-lab-boundary",
    "0.6": "one-step", "0.7": "learning-paths", "0.8": "glossary",
    "1.1": "compat-matrix", "1.2": "version-decision", "1.3": "hardware", "1.4": "install-51-232",
    "1.5": "install-61-30", "1.6": "container", "1.7": "install-methods", "1.8": "dev-tools", "1.9": "install-troubleshooting",
    "2.1": "why-usd", "2.2": "usd-concepts", "2.3": "layers-composition", "2.4": "physics-schema",
    "2.5": "usd-python", "2.6": "what-is-kit", "2.7": "extensions", "2.8": "nucleus",
    "3.1": "sim-loop", "3.2": "simulation-app", "3.3": "rigid-collision", "3.4": "articulation",
    "3.5": "urdf-mjcf-import", "3.6": "sensors", "3.7": "cloner", "3.8": "rendering", "3.9": "replicator",
    "3.10": "ros2-bridge", "3.11": "api-map",
    "4.1": "why-isaac-lab", "4.2": "repo-map", "4.3": "configclass", "4.4": "simulation-context",
    "4.5": "interactive-scene", "4.6": "assets", "4.7": "actuators", "4.8": "sensors",
    "4.9": "manager-based-env", "4.10": "observation-action", "4.11": "reward-termination-curriculum",
    "4.12": "event-randomization", "4.13": "command-manager", "4.14": "direct-env", "4.15": "task-registration",
    "4.16": "rl-wrappers", "4.17": "multi-agent", "4.18": "extension-template", "4.19": "mimic", "4.20": "teleop-devices",
    "5.1": "mdp", "5.2": "policy-value", "5.3": "ppo", "5.4": "parallel-envs", "5.5": "reward-design",
    "5.6": "observation-design", "5.7": "il-vs-rl", "5.8": "training-debug",
    "6.1.1": "galbot-repo", "6.1.2": "import-urdf", "6.1.3": "vendor-vs-imported-usd", "6.1.4": "collision-mass-inertia",
    "6.1.5": "joint-drive-tuning", "6.1.6": "articulation-cfg", "6.1.7": "asset-versioning",
    "6.2.1": "workbench-scene", "6.2.2": "wrist-camera", "6.2.3": "cloning-performance",
    "6.3.1": "physics-tuning", "6.3.2": "sim-vs-real",
    "6.4.1": "reach", "6.4.2": "domain-randomization", "6.4.3": "lift", "6.4.4": "reach-direct",
    "6.4.5": "base-navigation", "6.4.6": "teleop-demos", "6.4.7": "mimic",
    "6.5.1": "train-reach-rsl-rl", "6.5.2": "hyperparameters", "6.5.3": "experiment-management", "6.5.4": "multi-gpu",
    "6.6.1": "play-replay", "6.6.2": "evaluation",
    "6.7.1": "policy-export", "6.7.2": "ros2-closed-loop", "6.7.3": "sim2real-checklist",
    "7.1": "headless-remote", "7.2": "profiling", "7.3": "debugging", "7.4": "testing-ci", "7.5": "data-management", "7.6": "team-conventions",
    "8.1": "what-changed", "8.2": "multi-backend", "8.3": "newton", "8.4": "migration-23-30", "8.5": "galbot-reach-30", "8.6": "version-tracking",
    "9.1": "rl-env-step", "9.2": "scene-cloning", "9.3": "articulation-data", "9.4": "train-script", "9.5": "franka-lift",
    "A.1": "api-cheatsheet", "A.2": "error-index", "A.3": "official-resources", "A.4": "community-projects", "A.5": "changelog",
}


def parse_outline() -> list[dict]:
    """返回 [{caption, pages:[(num,title)] 或 subs:[{title, pages}]}]。"""
    parts: list[dict] = []
    part = None
    for line in (REPO / "OUTLINE.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (第 (\d) 部分 · (.+)|附录)\s*$", line)
        if m:
            if m.group(1) == "附录":
                caption, key = "附录", "A"
            else:
                caption = f"第 {m.group(2)} 部分 · " + re.sub(r"（.*?）", "", m.group(3)).strip()
                key = m.group(2)
            part = {"caption": caption, "key": key, "pages": [], "subs": []}
            parts.append(part)
            continue
        if part is None:
            continue
        m = re.match(r"^### (.+)$", line)
        if m and part["key"] == "6":
            part["subs"].append({"title": m.group(1).strip(), "pages": []})
            continue
        m = re.match(r"^\| ([0-9A]\.[0-9.]+) \| ([^|]+) \|", line)
        if m:
            entry = (m.group(1), m.group(2).strip())
            (part["subs"][-1]["pages"] if part["subs"] else part["pages"]).append(entry)
    return parts


def rel_path(num: str) -> Path:
    head = num.split(".")[0]
    base = Path(PART_DIR[head])
    if head == "6":
        base = base / SUB_DIR[num.split(".")[1]]
    return base / f"{num}-{SLUG[num]}.md"


def is_real(src: Path) -> bool:
    return src.exists() and "待写，见 OUTLINE" not in src.read_text(encoding="utf-8")


def write_page(num: str, title: str) -> str:
    path = rel_path(num)
    src = REPO / "docs" / path
    dst = SITE / path
    dst.parent.mkdir(parents=True, exist_ok=True)
    if is_real(src):
        dst.write_text("\n".join(convert(src.read_text(encoding="utf-8").split("\n"))), encoding="utf-8")
        kind = "real"
    else:
        plain = title.replace("`", "")
        dst.write_text(f"---\ntitle: {plain}\n---\n\n# {title}\n\n待写，见 OUTLINE {num}。\n", encoding="utf-8")
        kind = "stub"
    return kind


def toctree(entries: list[str], caption: str | None = None, hidden: bool = True) -> str:
    opts = []
    if hidden:
        opts.append(":hidden:")
    if caption:
        opts.append(f":caption: {caption}")
    body = "\n".join(entries)
    return "```{toctree}\n" + "\n".join(opts) + "\n\n" + body + "\n```\n"


def main() -> None:
    parts = parse_outline()
    counts = {"real": 0, "stub": 0}
    blocks = []
    for part in parts:
        entries = []
        for num, title in part["pages"]:
            counts[write_page(num, title)] += 1
            entries.append(str(rel_path(num).with_suffix("")))
        for i, sub in enumerate(part["subs"], start=1):
            sub_dir = Path(PART_DIR["6"]) / SUB_DIR[str(i)]
            sub_entries = []
            for num, title in sub["pages"]:
                counts[write_page(num, title)] += 1
                sub_entries.append(rel_path(num).relative_to(sub_dir).with_suffix("").as_posix())
            index = SITE / sub_dir / "index.md"
            index.write_text(f"---\ntitle: {sub['title']}\n---\n\n# {sub['title']}\n\n" + toctree(sub_entries, hidden=False), encoding="utf-8")
            entries.append((sub_dir / "index").as_posix())
        blocks.append(toctree(entries, caption=part["caption"]))
    index = SITE / "index.md"
    text = index.read_text(encoding="utf-8")
    text = text.split("<!-- toctree:begin -->")[0].rstrip() + "\n\n<!-- toctree:begin -->\n" + "\n".join(blocks)
    index.write_text(text, encoding="utf-8")
    print(f"real pages: {counts['real']}, stubs: {counts['stub']}")


if __name__ == "__main__":
    main()
