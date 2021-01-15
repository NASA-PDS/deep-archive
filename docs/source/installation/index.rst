📦 Installation
===============

This section describes how to install the PDS Deep Archive.


Requirements
------------

Prior to installing this software, ensure your system meets the following
requirements:

•  Python_ 3. This software requires Python 3; it will work with 3.6, 3.7, or
   3.8.  Python 2 will absolutely *not* work, and indeed Python 2 came to its
   end of life on the first of January, 2020.  Run ``python3 --version``, or ``python3 --version``, to
   check it is installed.
•  ``libxml2`` version 2.9.2; later 2.9 versions are fine.  Run ``xml2-config
   --version`` to find out.
•  ``libxslt`` version 1.1.28; later 1.1 versions are OK too.  Run
   ``xslt-config`` to see.

..  note:: Windows Users

    It is highly recommended you install using `Python Anaconda <https://www.anaconda.com/products/individual>`_ as it comes pre-packaged with the necessary dependencies to run the application.

    During installation, be sure to check the box to add the Anaconda distribution to PATH.


Consult your operating system instructions or system administrator to install
the required packages. For those without system administrator access and are 
feeling anxious, you could try a local (home directory) Python_ 3 installation 
using a Miniconda_ installation.


Doing the Installation
----------------------


.. note::

    Some things to be aware of regarding examples below:

    * The octothorp characters `#` below indicate comments and need not be typed in.

    * The location of where you choose to create a Python virtual environment is entirely your preference.

    * The examples below should be seen only as suggestions. Invoking command lines below are demonstrative.

    * Please consult your system documentation for the appropriate invocations for your operating system, command shell (or "terminal"), and so forth.


The easiest way to install this software is to use Pip_, the Python Package
Installer. If you have Python on your system, you probably already have Pip;
you can run ``pip3 --help`` to check.

It's best install the PDS Deep Archive into a `virtual environment`_ so it
won't interfere with—or be interfered by—other packages.  To do so::

    # For Linux / Mac / other Unix systems
    # Example assumes bash command shell. For others, consult shell documentation.
    mkdir -p $HOME/.virtualenvs
    python3 -m venv $HOME/.virtualenvs/pds-deep-archive
    source $HOME/.virtualenvs/pds-deep-archive/bin/activate
    pip3 install pds.deeparchive

    # For Windows
    mkdir virtualenvs
    python -m venv virtualenvs\\pds-deep-archive
    virtualenvs\\pds-deep-archive\\Scripts\\activate
    pip3 install pds.deeparchive

It's also possible to use ``easy_install`` if you prefer, or to install it
via a Buildout_, or (if you must) into the system Python.

You can then run ``pds-deep-archive --help`` to get a usage message and ensure
it's properly installed.


..  note::

    The above commands will install last approved release from the Python
    Package Index ("Cheeseshop_"). The latest, cutting edge release is posted
    at the Test Package Index, but these releases may not be fully confirmed
    to be operational. If you like taking risks, run the following to create a
    new virtual environment and install the latest development version of the
    software::
    
      mkdir -p $HOME/.virtualenvs
      python3 -m venv $HOME/.virtualenvs/pds-deep-archive
      source $HOME/.virtualenvs/pds-deep-archive/bin/activate
      pip3 install --index-url https://test.pypi.org/simple --extra-index-url https://pypi.org/simple`` pds.deeparchive
    

Upgrade Software
----------------

To check and install an upgrade to the software, run the following command in your 
virtual environment::

    source $HOME/.virtualenvs/pds-deep-archive/bin/activate
    pip install pds.deeparchive --upgrade

.. note:: The same admonitions mentioned earlier about command line
    invocations also apply to the above example.



.. References:
.. _Pip: https://pip.pypa.io/en/stable/
.. _Python: https://www.python.org/
.. _`virtual environment`: https://docs.python.org/3/library/venv.html
.. _Buildout: http://www.buildout.org/
.. _Cheeseshop: https://pypi.org/
.. _Miniconda: https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html
