PDS Deep Archive
===================

The PDS Deep Archive is a Python_ based package providing utilities for
handling *deep* archives. It includes software for Archive Information Package
(AIP) and Submission Information Package (SIP) products, based on Open
Archival Information System (OAIS_) standards.

This software is used to generate the necessary packages for delivery of PDS4
archives to the NASA Space Science Data Coordinated Archive (NSSDCA).

For delivering PDS3 data, see `documentation at the Engineering Node <https://pds-engineering.jpl.nasa.gov/content/nssdca_interface_process#pds3>`_.

Currently, this package provides three executable programs:

•  ``pds-deep-archive``, primary executable for creating both Archive
   Information Packages (AIPs) and Submission Information Packages (SIPs); and
•  ``aipgen``, a subcomponent of ``pds-deep-archive`` to create Archive
   Information Packages (AIPs); and
•  ``sipgen``, a subcomponent of ``pds-deep-archive`` to create Submission
   Information Packages (SIPs)

from PDS bundles. You'll mostly just use ``pds-deep-archive`` but the other
two are there if you ever *just* want an AIP or a SIP.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation/index
   usage/index
   development/index
   support/index


.. Perhaps we will use this in the future:
.. Indexes and Tables
.. ==================

.. • :ref:`genindex`
.. • :ref:`modindex`
.. • :ref:`search`

.. _OAIS: https://www2.archivists.org/groups/standards-committee/open-archival-information-system-oais
.. _Python: https://www.python.org/
