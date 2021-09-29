# Sphinx Configuration 🐈
# =======================
#
# See the full Sphinx config docs at::
#     https://www.sphinx-doc.org/en/master/usage/configuration.html


# Project Metadata
# ----------------
#
# There's both ``version`` and ``release`` here per Sphinx quickstart; is
# there a way to get parity with ``setup.py`` though? 🤔

project            = 'PDS Deep Archive'
author             = 'NASA Planetary Data System'
copyright          = '2020 California Institute of Technology'
language           = 'en'


# Sphinx Setup
# ------------
#
# Stuff that controls Sphinx.
#
#
# Settings
# ~~~~~~~~
#
# Note that some of these settings are for certain extensions, see below.

exclude_patterns   = []
html_static_path   = ['_static']
html_theme         = 'sphinx_rtd_theme'
master_doc         = 'index'
pygments_style     = 'sphinx'
source_suffix      = '.rst'
templates_path     = ['_templates']
todo_include_todos = True

# -- Read the docs config -------

html_logo = '_static/images/PDS_Planets.png'

html_context = {
    'css_files': [
        '_static/theme_overrides.css',  # override wide tables in RTD theme
    ],
}

html_theme_options = {
    'canonical_url': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Extensions
# ~~~~~~~~~~
#
# These are add-ons, most of which we don't use (for now).

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosummary',
    'sphinx_rtd_theme',
    'sphinxarg.ext',
]

# Other Options
# ~~~~~~~~~~~~~
#
# Not used here, but we could include in the future:
#
# • HTMLHelp formatting
# • LaTeX output
# • Man page generation
# • TeXinfo output
