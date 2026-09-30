"""Isaac Academy — Sphinx 原型（T-SITE-03）。

与 docs/ 下的 MkDocs 站并存；用户对比后再决定是否切换。
不使用 nvidia-sphinx-theme 及 NVIDIA 的 logo、字体、图标；只借用官方站的色值（见 _static/css/academy.css）。
"""

project = "Isaac Academy"
author = "Isaac Academy"
copyright = "2026, Isaac Academy"
language = "zh_CN"

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
]

source_suffix = {".md": "markdown"}
exclude_patterns = ["_build", ".venv", "tools", "MIGRATION-NOTES.md", "requirements-sphinx.txt"]

# -- MyST ---------------------------------------------------------------------
myst_enable_extensions = ["colon_fence", "attrs_inline", "attrs_block", "deflist"]
myst_heading_anchors = 3  # 让 [..](page.md#标题) 形式的链接可以解析
myst_footnote_transition = False

# -- Mermaid（本地，不走 CDN）--------------------------------------------------
mermaid_use_local = "js/mermaid-shim.mjs"
mermaid_version = ""  # 与 use_local 配合：不生成任何 CDN 地址
mermaid_include_elk = False
mermaid_d3_zoom = False
mermaid_fullscreen = False
mermaid_height = "auto"
mermaid_light_theme = "neutral"  # 灰黑配色，比 default 的紫/黄更接近官方站的中性色调
mermaid_dark_theme = "dark"

# -- HTML ---------------------------------------------------------------------
html_theme = "pydata_sphinx_theme"
html_title = "Isaac Academy"
html_static_path = ["_static"]
html_css_files = [
    # 字体（D-015 允许 CDN）：官方站用 NVIDIA Sans / RobotoMono（专有、NVIDIA 托管，不能用），
    # 这里用度量相近的开源字体：Inter 替代 NVIDIA Sans，Roboto Mono（Apache-2.0）同名开源版，中文 Noto Sans SC。
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&family=Roboto+Mono:wght@400;500;700&display=swap",
    "css/academy.css",
]
html_js_files = ["js/mermaid-size.js"]
html_templates_path = ["_templates"]
templates_path = ["_templates"]
html_show_sourcelink = False
html_copy_source = False
html_search_language = "zh"  # 依赖 jieba 分词

html_theme_options = {
    # 版式对齐 docs.isaacsim.omniverse.nvidia.com：左侧标题，右侧搜索框 + 深浅色切换，无顶部导航标签
    "logo": {"text": "Isaac Academy", "image_light": "_static/img/academy-logo.svg", "image_dark": "_static/img/academy-logo.svg", "alt_text": "Isaac Academy"},
    "navbar_start": ["navbar-logo", "academy-subtitle"],
    "navbar_center": [],
    "navbar_end": ["search-button-field", "theme-switcher", "navbar-icon-links"],
    "navbar_persistent": [],
    # 仓库地址待用户提供（T-SITE-05），暂指向 GitHub 首页
    "icon_links": [{"name": "GitHub", "url": "https://github.com", "icon": "fa-brands fa-github", "type": "fontawesome"}],
    "announcement": "主线版本：Isaac Sim 5.1.0 + Isaac Lab 2.3.2；3.0 前沿专栏基于 Isaac Lab 3.0.0-EA，内容可能变动。",
    "primary_sidebar_end": [],
    "secondary_sidebar_items": ["page-toc"],
    "footer_start": ["academy-footer"],
    "footer_center": [],
    "footer_end": [],
    "show_toc_level": 2,
    "navigation_depth": 3,
    "collapse_navigation": False,
    "show_nav_level": 1,
    "pygments_light_style": "tango",
    "pygments_dark_style": "monokai",
    "show_prev_next": True,
}
# pydata-sphinx-theme 0.16 通过 html_context 设置默认深浅色；官方站为 auto（跟随系统），本站按用户要求固定默认浅色
html_context = {"default_mode": "light"}  # 默认浅色（T-SITE-04 用户要求）
html_sidebars = {"**": ["academy-toc-title", "academy-nav"]}
