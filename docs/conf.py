"""Isaac Academy 站点配置（Sphinx + MyST + pydata-sphinx-theme）。

D-020 起为唯一站点源；源文件在 docs/，构建见仓库 README。
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
exclude_patterns = ["_build", "MIGRATION-NOTES.md"]

# -- MyST ---------------------------------------------------------------------
myst_enable_extensions = ["colon_fence", "attrs_inline", "attrs_block", "deflist", "dollarmath", "amsmath"]  # dollarmath、amsmath：D-022
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
# 站点图标（T-SITE-11）：SVG 作主图标；PNG 16/32 与 apple-touch-icon 由 _templates/layout.html 加进 <head>
# （pydata-sphinx-theme 0.16 的 theme.conf 不再声明 favicons 选项，写进 html_theme_options 会报 unsupported theme option）。
# 图形由 _static/img/academy-logo.svg 简化而来，PNG 由 docs/_tools/make_favicons.py 生成。
html_favicon = "_static/img/favicon/favicon.svg"
html_static_path = ["_static"]
# 原样复制到产物根目录：CNAME（自定义域名）与 .nojekyll（让 GitHub Pages 不经 Jekyll 处理 _static 等下划线目录）
html_extra_path = ["_extra"]
html_baseurl = "https://academy.kiloong.com/"
html_css_files = [
    # 字体（D-015 允许 CDN）：官方站用 NVIDIA Sans / RobotoMono（专有、NVIDIA 托管，不能用），
    # 这里用度量相近的开源字体：Inter 替代 NVIDIA Sans，Roboto Mono（Apache-2.0）同名开源版，中文 Noto Sans SC。
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&family=Roboto+Mono:wght@400;500;700&display=swap",
    "css/academy.css",
]
html_js_files = ["js/mermaid-size.js", "js/announcement-close.js", "js/cjk-search.js", "js/table-code-wbr.js"]
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
    "icon_links": [{"name": "GitHub", "url": "https://github.com/ueasycallme/academy", "icon": "fa-brands fa-github", "type": "fontawesome"}],
    # 公告条是原样输出的 HTML，Sphinx 不会按页面层级改写其中的链接。这里写成自定义域名下的绝对地址
    # （无 JS 时也可用）；_static/js/announcement-close.js 会把它改写为相对 data-content_root 的路径，
    # 使站点在子路径（如 ueasycallme.github.io/academy/）或本地预览下同样可用。
    "announcement": "主线：Isaac Sim 5.1.0（官方已停止支持）+ Isaac Lab 2.3.2；3.0 前沿专栏基于 EA。<a href='https://academy.kiloong.com/1-env/1.2-version-decision.html' data-academy-local='1-env/1.2-version-decision.html'>为何仍选 5.1.0 →</a>",
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
html_context = {
    "default_mode": "light",
    # 仓库信息（pydata-sphinx-theme 的 edit-this-page 等功能使用），D-020
    "github_user": "ueasycallme",
    "github_repo": "academy",
    "github_version": "main",
    "doc_path": "docs",
}  # 默认浅色（T-SITE-04 用户要求）
html_sidebars = {"**": ["academy-toc-title", "academy-nav"]}


# 术语表锚点（CONVENTIONS 第 2 节：行内写 [**术语**]{#term-xxx}）。
# MyST 解析 `page.md#id` 形式的链接时只查标题锚点（env.metadata[doc]["myst_slugs"]），
# 行内属性生成的 id 查不到，会报 myst.xref_missing（链接本身仍然正确）。
# 这里在读入文档后把 term- 开头的 id 补进该表，使术语链接能通过 -W 构建。
def _register_term_ids(app, doctree):
    from docutils import nodes

    slugs = app.env.metadata[app.env.docname].setdefault("myst_slugs", {})
    for node in doctree.findall(nodes.Element):
        for node_id in node.get("ids", []):
            if node_id.startswith("term-") and node_id not in slugs:
                slugs[node_id] = (node.line or 0, node_id, node.astext())


def setup(app):
    app.connect("doctree-read", _register_term_ids)
