import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

project = "huti"
author = "José Antonio Puértolas Montañés"
copyright = "2023, José Antonio Puértolas Montañés"
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_click",
    "sphinx.ext.intersphinx",
]
autoclass_content = "both"
autodoc_default_options = {"members": True, "member-order": "bysource",
                           "undoc-members": True, "show-inheritance": True}
autodoc_typehints = "description"
html_theme = "furo"
html_title, html_last_updated_fmt = "huti docs", "%Y-%m-%dT%H:%M:%S"
inheritance_alias = {}
nitpicky = True
nitpick_ignore = [('py:class', '*')]
toc_object_entries = True
toc_object_entries_show_parents = "all"
pygments_style, pygments_dark_style = "sphinx", "monokai"
extlinks = {
    "issue": ("https://github.com/j5pu/huti/issues/%s", "#%s"),
    "pull": ("https://github.com/j5pu/huti/pull/%s", "PR #%s"),
    "user": ("https://github.com/%s", "@%s"),
}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "packaging": ("https://packaging.pypa.io/en/latest", None),
}
