****************************
 PDS Deep Archive Utilities
****************************

Software for the Planetary Data System (PDS_) to generate Archive Information
Package (AIP) and Submission Information Package (SIP) products, based upon Open
Archival Information System (OAIS_) standards.


Features
========

• Provides an exectuble Python script ``pds-deep-archive``. Run ``pds-deep-archive --help`` for
  more details.
• Provides an exectuble Python script ``aipgen``. Run ``aipgen --help`` for
  more details.
• Provides an exectuble Python script ``sipgen``. Run ``sipgen --help`` for
  more details.


Installation
============

First, this requires Python 3.6, 3.7, or 3.8. Are you still using Python 2? It
reached end-of-life on January 1st, 2020_.

Make a virtualenv_ and run ``pip install pds-deep-archive`` into it. Or use a buildout_
or, if you absolutely must, install it into your system python you monster.
This software depends on the lxml_ library which your Python installer should
take care of, but your *system* will require ``libxml2`` 2.9.2 or later as
well as ``libxsl2`` 1.1.28 or later.

1. Download the tar.gz distribution

2. Create a virtualenv and activate::

    bash> mkdir -p $HOME/.virtualenvs
    bash> virtualenv $HOME/.virtualenvs/pds-deep-archive
    bash> $HOME/.virtualenvs/pds-deep-archive/bin/activate

3. Use the downloaded tar.gz from step 1 and pip to install pds-deep-archive and all of its dependencies::

    (pds-deep-archive) bash> pip install pds.deeparchive-0.0.0.tar.gz
    
4. You should now be able to run the deep archive utilities::

    (pds-deep-archive) bash> pds-deep-archive --help
    (pds-deep-archive) bash> aipgen --help
    (pds-deep-archive) bash> sipgen --help


Build
=====

To build the software for distribution:

1. Boostrap the buildout (if needed)::

    bash> python3 bootstrap.py
    bash> bin/buildout

2. Create an install package::

    bash> buildout setup . sdist

3. A tar.gz should now be available in the ``dist/`` directory for distribution.


Documentation
=============

Installation and Usage information can be found in the documentation online at https://nasa-pds-incubator.github.io/pds-deep-archive/ or the latest version is maintained under the ``docs`` directory.



Translations
============

This product has not been translated into any other languages than US English.


Contribute
==========

• Issue Tracker: https://github.com/NASA-PDS-Incubator/pds-deep-archive/issues
• Source Code: https://github.com/NASA-PDS-Incubator/pds-deep-archive
• Wiki: https://github.com/NASA-PDS-Incubator/pds-deep-archive/wiki


Support
=======

If you are having issues, please let us know.  You can reach us at
https://pds.nasa.gov/?feedback=true


License
=======

The project is licensed under the Apache License, version 2. See the
LICENSE.txt file for details.


.. _2020: https://pythonclock.org/
.. _buildout: http://docs.buildout.org/en/latest/
.. _OAIS: https://www2.archivists.org/groups/standards-committee/open-archival-information-system-oais
.. _PDS: https://pds.nasa.gov/
.. _virtualenv: https://docs.python.org/3/library/venv.html
.. _lxml: https://lxml.de/


.. Copyright © 2019–2020 California Institute of Technology ("Caltech").
   ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
