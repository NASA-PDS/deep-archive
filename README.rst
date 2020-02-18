****************************
 PDS Deep Archive Utilities
****************************

Software for the Planetary Data System (PDS_) to generate Archive Information
Package (AIP) and Submission Information Package (SIP) products, based upon Open
Archival Information System (OAIS_) standards.


Features
========

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


Usage
=====

1. If not already activated, activate your virtualenv::

    bash> $HOME/.virtualenvs/pds-deep-archive/bin/activate
    (pds-deep-archive) bash>

2. Then you can run sipgen. Here is a basic usage example using data in the test directory::

    (pds-deep-archive) bash> sipgen -s PDS_ATM -n -b https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/ test/data/ladee_test/ladee_mission_bundle/LADEE_Bundle_1101.xml
    ⚙︎ ``sipgen`` — Submission Information Package (SIP) Generator, version 0.0.0
    🎉 Success! From test/data/ladee_test/ladee_mission_bundle/LADEE_Bundle_1101.xml, generated these output files:
    • Manifest: ladee_mission_bundle_sip_v1.0.tab
    • Label: ladee_mission_bundle_sip_v1.0.xml


Full usage from the ``--help`` flag::

    usage: sipgen [-h] [-a {MD5,SHA-1,SHA-256}] -s
                  {PDS_ATM,PDS_ENG,PDS_GEO,PDS_IMG,PDS_JPL,PDS_NAI,PDS_PPI,PDS_PSI,PDS_RNG,PDS_SBN}
                  [-u URL] [-k] [-n] [-b BUNDLE_BASE_URL] [-v]
                  [-i PDS4_INFORMATION_MODEL_VERSION]
                  IN-BUNDLE.XML

    Generate Submission Information Packages (SIPs) from bundles. This program
    takes a bundle XML file as input and produces two output files: ① A Submission
    Information Package (SIP) manifest file; and ② A PDS XML label of that file.
    The files are created in the current working directory when this program is
    run. The names of the files are based on the logical identifier found in the
    bundle file, and any existing files are overwritten. The names of the
    generated files are printed upon successful completion.

    positional arguments:
      IN-BUNDLE.XML         Bundle XML file to read

    optional arguments:
      -h, --help            show this help message and exit
      -a {MD5,SHA-1,SHA-256}, --algorithm {MD5,SHA-1,SHA-256}
                            File hash (checksum) algorithm; default MD5
      -s {PDS_ATM,PDS_ENG,PDS_GEO,PDS_IMG,PDS_JPL,PDS_NAI,PDS_PPI,PDS_PSI,PDS_RNG,PDS_SBN}, --site {PDS_ATM,PDS_ENG,PDS_GEO,PDS_IMG,PDS_JPL,PDS_NAI,PDS_PPI,PDS_PSI,PDS_RNG,PDS_SBN}
                            Provider site ID for the manifest's label; default
                            None
      -u URL, --url URL     URL to the registry service; default https://pds-dev-
                            el7.jpl.nasa.gov/services/registry/pds
      -k, --insecure        Ignore SSL/TLS security issues; default False
      -n, --offline         Run offline, scanning bundle directory for matching
                            files instead of querying registry service
      -b BUNDLE_BASE_URL, --bundle-base-url BUNDLE_BASE_URL
                            Base URL prepended to URLs in the generated manifest
                            for local files in "offline" mode
      -v, --verbose         Verbose logging; defaults False
      -i PDS4_INFORMATION_MODEL_VERSION, --pds4-information-model-version PDS4_INFORMATION_MODEL_VERSION
                            Specify PDS4 Information Model version to generate
                            SIP. Must be 1.13.0.0+; default 1.13.0.0


Documentation
=============

Additional documentation is available in the ``docs`` directory and also TBD.



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
