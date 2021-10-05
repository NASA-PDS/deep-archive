PDS Deep Archive
================

The PDS Deep Archive is a Python_ based package providing utilities for
handling *deep* archives. It includes software for Archive Information Package
(AIP) and Submission Information Package (SIP) products, based on Open
Archival Information System (OAIS_) standards.

This software is used to generate the necessary packages for delivery of PDS4
archives to the NASA Space Science Data Coordinated Archive (NSSDCA).

For delivering PDS3 data, see `documentation at the Engineering Node`_.

Currently, this package provides two executable programs:

•  ``pds-deep-registry-archive``, primary executable for creating both Archive
   Information Packages (AIPs) and Submission Information Packages (SIPs) that
   uses the PDS Registry remote API over HTTP; and
•  ``pds-deep-archive``, primary executable for creating both Archive
   Information Packages (AIPs) and Submission Information Packages (SIPs) that
   uses a bundle laid out in the local filesystem; and

There are two additional programs:

•  ``aipgen``, a subcomponent of ``pds-deep-archive`` to create Archive
   Information Packages (AIPs); and
•  ``sipgen``, a subcomponent of ``pds-deep-archive`` to create Submission
   Information Packages (SIPs)

If you want to make Deep Archives of PDS data in a remote PDS Registry, use
``pds-deep-registry-archive``. For Deep Archives of PDS data on your hard
drive or other nearby filesystem, use ``pds-deep-archive``. (The other
two programs are there if you ever *just* want an AIP or a SIP out of
local files; you'll almost never need to use these.)

..  image:: _static/images/fs-vs-registry.png
    :target: _static/images/fs-vs-registry.png


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
.. _`documentation at the Engineering Node`: https://pds-engineering.jpl.nasa.gov/content/nssdca_interface_process#pds3
