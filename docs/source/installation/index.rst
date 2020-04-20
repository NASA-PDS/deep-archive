📦 Installation
===============

This section describes how to install the PDS Deep Archive.


Requirements
------------

Prior to installing this software, ensure your system meets the following
requirements:

•  Python_ 3. This software requires Python 3; it will work with 3.6, 3.7, or
   3.8.  Python 2 will absolutely *not* work, and indeed Python 2 came to its
   end of life on the first of January, 2020.  Run ``python3 --version`` to
   check.
•  ``libxml2`` version 2.9.2; later 2.9 versions are fine.  Run ``xml2-config
   --version`` to find out.
•  ``libxslt`` version 1.1.28; later 1.1 versions are OK too.  Run
   ``xslt-config`` to see.

Consult your operating system instructions or system administrator to install
the required packages.


Doing the Installation
----------------------

The easiest way to install this software is to use Pip_, the Python Package
Installer. If you have Python on your system, you probably already have Pip;
you can run ``pip3 --help`` to check.

It's best install the PDS Deep Archive into a `virtual environment`_ so it
won't interfere with—or be interfered by—other packages.  To do so::

    mkdir -p $HOME/.virtualenvs
    python3 -m venv $HOME/.virtualenvs/pds-deep-archive
    source $HOME/.virtualenvs/pds-deep-archive/bin/activate
    pip3 install pds.deeparchive

It's also possible to use ``easy_install`` if you prefer, or to install it
via a Buildout_, or (if you must) into the system Python.

You can then run ``aipgen --help`` or ``sipgen --help`` to get a usage message
and ensure it's properly installed.


..  note::

    The above commands will install last approved release from the Python
    Package Index ("Cheeseshop_"). The latest, cutting edge release is posted
    at the Test Package Index, but these releases may not be fully confirmed
    to be operational. If you like taking risks, add
    ``--index-url https://test.pypi.org/simple`` and
    ``--extra-index-url https://pypi.org/simple`` to the ``pip3 install``
    command.


.. References:
.. _Pip: https://pip.pypa.io/en/stable/
.. _Python: https://www.python.org/
.. _`virtual environment`: https://docs.python.org/3/library/venv.html
.. _Buildout: http://www.buildout.org/
.. _Cheeseshop: https://pypi.org/
