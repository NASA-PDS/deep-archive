👩‍💻 Development
=================

The quickest way to get started developing this package is to clone it and
build it out::

    git clone https://github.com/NASA-PDS/pds-deep-archive.git
    cd pds-deep-archive
    python3.13 -m venv venv
    source venv/bin/activate
    pip install --editable '.[dev]'

.. note:: The above series of commands assume you have the corresponding
    development tools and familiarity with invoking them from the
    command line or "terminal". Shells, operating systems, and command
    invocation varies.

At this point, you'll have the ``pds-deep-archive``,
``pds-deep-registry-archive``, and other programs ready to run as
``venv/bin/pds-deep-archive``, ``venv/bin/deep-registry-archive``, etc.,
that's set up to use source Python code under ``src``. Changes you make to
the code are reflected in immediately.

The documentation is in ``docs/source``, formatted as reStructuredText_ and
structured with Sphinx_.  To build the HTML from the documentation, run
``sphinx-build -b html docs/source docs/build``. It will write HTML output to
``docs/build`` and you can open ``docs/build/index.html`` in your browser.

Commits back to GitHub will trigger workflows in GitHub Actions_ that
re-publish the project website_ as well as send artifacts to the testing_
Python Package Index via the "unstable" workflow. The official Python Package
Index gets updated only with official release tags via the "stable"
workflow.


Testing
-------

The code base finally includes unit and functional tests. Once you've run
``pip install --editable '.[dev]'`` you can run the entire test suite
easily with::

    tox -e py313


Making Releases
---------------

That's what our continuous integration is for—the "stable" workflow.


Contribute
----------

Before contributing please review our `contributor's guide`_ which delineates
the kinds of contributions we accept. Our `code of conduct`_ outlines the
standards of behavior we practice and expect by everyone who participates
with our software.

The `source code is on GitHub`_.


.. _reStructuredText: https://docutils.sourceforge.io/rst.html
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _testing: https://test.pypi.org/
.. _Actions: https://github.com/features/actions
.. _website: https://nasa-pds.github.io/pds-deep-archive/
.. _Jenkins: https://jenkins-ci.org/
.. _`contributor's guide`: https://github.com/NASA-PDS/.github/blob/main/CONTRIBUTING.md
.. _`code of conduct`: https://github.com/NASA-PDS/.github/blob/main/CODE_OF_CONDUCT.md
.. _`source code is on GitHub`: https://github.com/NASA-PDS/pds-deep-archive
