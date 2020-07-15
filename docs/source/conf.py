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
version            = '1.0'
release            = '1.0.0'
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
html_theme         = 'alabaster'
master_doc         = 'index'
pygments_style     = 'sphinx'
source_suffix      = '.rst'
templates_path     = ['_templates']
todo_include_todos = True

# Alabaster Theme
# ~~~~~~~~~~~~~~~
#
# The "alabaster" theme requires these settings

html_theme_options = {
    'logo': 'PDS_Planets.png',
    'github_user': 'NASA-PDS',
    'github_repo': 'pds-deep-archive'
}

html_sidebars = {
    '**': [
        'about.html',
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
        'navigation.html'
    ]
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
