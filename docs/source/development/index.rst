👩‍💻 Development
=================

The quickest way to get started developing this package is to clone it and
build it out::

    git clone https://github.com/NASA-PDS-Incubator/pds-deep-archive.git
    cd pds-deep-archive
    python3 bootstrap.py
    bin/buildout

At this point, you'll have the ``sipgen`` program ready to run as
``bin/sipgen`` that's set up to use source Python code under ``src``. Changes
you make to the code are reflected in ``bin/sipgen`` immediately.

The documentation is in ``docs/source``, formatted as reStructuredText_ and
structured with Sphinx_.  To build the HTML from the documentation, run
``bin/docbuilder``. It will write HTML output to ``build/docs/html``.

You can also build local distributions or run any ``setuptools`` command via
the buildout refrain::

    bin/buildout setup . --help-commands

Commits back to GitHub will trigger workflows in GitHub Actions_ that
re-publish the project website_ as well as send artifacts to testing_ Python
Package Index.  (The official Python Package Index gets updated only with
official release tags.)


.. _reStructuredText: https://docutils.sourceforge.io/rst.html
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _testing: https://test.pypi.org/
.. _Actions: https://github.com/features/actions
.. _website: https://nasa-pds-incubator.github.io/pds-deep-archive/
