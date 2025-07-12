# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "stapy116"
copyright = "2025, driller"
author = "driller"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser", "sphinx_revealjs", "sphinx_design"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".venv"]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

myst_enable_extensions = ["colon_fence"]

revealjs_style_theme = "serif"
revealjs_static_path = ["_static"]
revealjs_script_plugins = [
    {
        "src": "revealjs/plugin/highlight/highlight.js",
        "name": "RevealHighlight",
    },
]
revealjs_css_files = [
    "revealjs/plugin/highlight/zenburn.css",
    "custom.css"
]
revealjs_script_conf = {
    "height": 900,
}