👩‍💻 Development
=================

The quickest way to get started developing this package is to clone it and
build it out::

    git clone https://github.com/NASA-PDS/pds-deep-archive.git
    cd pds-deep-archive
    python3 bootstrap.py
    bin/buildout

.. note:: The above series of commands assume you have the corresponding
    development tools and familiarity with invoking them from the
    command line or "terminal". Shells, operating systems, and command
    invocation varies.

At this point, you'll have the ``pds-deep-archive``, ``aipgen``, ``sipgen``
programs ready to run as ``bin/pds-deep-archive``, ``bin/aipgen``, and
``bin/sipgen`` that's set up to use source Python code under ``src``.
Changes you make to the code are reflected in ``bin/sipgen`` immediately.

The documentation is in ``docs/source``, formatted as reStructuredText_ and
structured with Sphinx_.  To build the HTML from the documentation, run
``bin/docbuilder``. It will write HTML output to ``build/docs/html``.

You can also build local distributions or run any ``setuptools`` command via
the buildout refrain::

    bin/buildout setup . --help-commands

Commits back to GitHub will trigger workflows in GitHub Actions_ that
re-publish the project website_ as well as send artifacts to the testing_
Python Package Index. (The official Python Package Index gets updated only
with official release tags.)


Testing
-------

The code base finally includes unit and functional tests. Once you've built
out, you can run the entire test suite easily with::

    bin/test

If you'd like to integrate test data output with a CI/CD system such as
Jenkins_, add the ``--xml`` option to make a machine-readable reports in the
``parts/test`` directory.  Try ``bin/test --help`` for lots of other options.


..  note::

    Integration testing is not yet implemented, but could be if the need
    arises.


Making Releases
---------------

As mentioned in the parenthetical above, the official Python Package Index is
updated with an official release of this software is created with a release tag.
To ensure coherency with the GitHub release, first update the file::

    src/pds/aipgen/version.txt

and enter the release version number you'd like to appear when running the
commands with ``--version`` and on the official Python Package Index.  Commit
and push this, then, on GitHub (and with appropriate permissions), visit:

    https://github.com/NASA-PDS/pds-deep-archive/releases/new

and enter a release tag with the same version number plus any release notes.
This will trigger a GitHub Actions release to the official PyPI 🤞.

To deploy to the official PyPi manually:

1. Place the appropriate credentials in ``~/.pypirc``
2. Create the package::

    python setup.py sdist
    … or …
    bin/buildout setup . sdist

3. Deploy to PyPi::

    pip install twine
    twine upload dist/*.tar.gz

.. note:: The same admonitions mentioned earlier about command line
    invocations also apply to the above example.

Contribute
----------

Source Code: https://github.com/NASA-PDS/pds-deep-archive


.. _reStructuredText: https://docutils.sourceforge.io/rst.html
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _testing: https://test.pypi.org/
.. _Actions: https://github.com/features/actions
.. _website: https://nasa-pds.github.io/pds-deep-archive/
.. _Jenkins: https://jenkins-ci.org/
