****************************
 PDS Deep Archive Utilities
****************************

|Stable Build| |Unstable Build|

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

See the online documentation for Installation_ instructions
    
You should then be able to run the deep archive utilities::

    (pds-deep-archive) bash> pds-deep-archive --help
    (pds-deep-archive) bash> aipgen --help
    (pds-deep-archive) bash> sipgen --help

.. note:: The above commands demonstrate typical usage with a command-line
    prompt, such as that provided by the popular ``bash`` shell; your own
    prompt may appear differently and may vary depending on operating system,
    shell choice, and so forth.


Build
=====

See the `Development Guide`_ for more information.


Documentation
=============

Installation and Usage information can be found in the documentation online at https://nasa-pds.github.io/pds-deep-archive/ or the latest version is maintained under the ``docs`` directory.



Translations
============

This product has not been translated into any other languages than US English.


Contribute
==========

• Issue Tracker: https://github.com/NASA-PDS/pds-deep-archive/issues
• Source Code: https://github.com/NASA-PDS/pds-deep-archive
• Wiki: https://github.com/NASA-PDS/pds-deep-archive/wiki


Support
=======

If you are having issues file a bug report in Github: https://github.com/NASA-PDS/pds-deep-archive/issues

Or you can reach us at https://pds.nasa.gov/?feedback=true


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
.. _Installation: https://nasa-pds.github.io/pds-deep-archive/installation/
.. _`Development Guide`: https://nasa-pds.github.io/pds-deep-archive/development/

.. |Unstable Build| image:: https://github.com/NASA-PDS/pds-deep-archive/workflows/%F0%9F%A4%AA%20Unstable%20integration%20&%20delivery/badge.svg
   :target: https://github.com/NASA-PDS/pds-deep-archive/actions?query=workflow%3A%22%F0%9F%A4%AA+Unstable+integration+%26+delivery%22

.. |Stable Build| image:: https://github.com/NASA-PDS/pds-deep-archive/workflows/%F0%9F%98%8C%20Stable%20integration%20&%20delivery/badge.svg
   :target: https://github.com/NASA-PDS/pds-deep-archive/actions?query=workflow%3A%22%F0%9F%98%8C+Stable+integration+%26+delivery%22


.. Copyright © 2019–2020 California Institute of Technology ("Caltech").
   ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
