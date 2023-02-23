# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from pathlib import Path

THIS_DIR = Path(__file__).parent


def get_version(filepath: Path) -> str:
    with open(filepath, encoding="utf-8") as fd:
        for line in fd.readlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        raise RuntimeError("Unable to find version string.")


version = get_version(THIS_DIR.parent.parent / "labgraph" / "__init__.py")

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "LabGraph"
copyright = "2022, Rishi E Kumar"
author = "Rishi E Kumar"
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "recommonmark",
    "sphinx_autodoc_typehints",
]

add_module_names = False
typehints_fully_qualified = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"

html_theme_options = {
    "repository_url": "https://github.com/rekumar/labgraph",
    "use_repository_button": True,
    "home_page_in_toc": True,
    "show_navbar_depth": 0,
}

# html_logo = (Path(__file__).parent / "_static" / "logo.png").as_posix()
html_title = "LabGraph"


def run_apidoc(_):
    from pathlib import Path

    ignore_paths = []

    ignore_paths = [
        (Path(__file__).parent.parent.parent / p).absolute().as_posix()
        for p in ignore_paths
    ]

    argv = [
        "-f",
        "-e",
        "-o",
        Path(__file__).parent.as_posix(),
        (Path(__file__).parent.parent.parent / "labgraph").absolute().as_posix(),
    ] + ignore_paths

    try:
        # Sphinx 1.7+
        from sphinx.ext import apidoc

        apidoc.main(argv)
    except ImportError:
        # Sphinx 1.6 (and earlier)
        from sphinx import apidoc

        argv.insert(0, apidoc.__file__)
        apidoc.main(argv)


def setup(app):
    app.connect("builder-inited", run_apidoc)
