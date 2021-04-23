🏃‍♀️ Usage
===========

.. toctree::


Overview
--------

This package provides two primary executables, ``pds-deep-archive`` and
``pds-deep-registry-archive``, that generate both an Archive Information
Package (AIP) and a Submission Information Package (SIP). The SIP is what is
delivered by the PDS to the NASA Space Science Data Coordinated Archive
(NSSDCA). For more information about the products produced, see the following
references:

•   OAIS Information - http://www.oais.info/
•   AIP Information - https://www.iasa-web.org/tc04/archival-information-package-aip
•   SIP Information - https://www.iasa-web.org/tc04/submission-information-package-sip

You use ``pds-deep-archive`` for PDS data on your hard drive, network
filesystem, etc.; you use ``pds-deep-registry-archive`` for PDS data in a
PDS Registry.

This package also comes with the two sub-components of ``pds-deep-archive``
that can be ran individually:

•  ``aipgen`` that generates Archive Information Packages from a PDS4 bundle
•  ``sipgen`` that generates Submission Information from a PDS4 bundle

These work just with local files, not the PDS Registry.


Usage Information
-----------------

Running ``pds-deep-archive --help`` or ``pds-deep-registry-archive --help`` to
get summaries of the command-line invocations, required arguments, and any
options that refine the behavior.


Example 1: Basic Usage on Local Files
-------------------------------------

For example, to create a SIP and AIP from the LADEE 1101 Bundle located at
``test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml`` run the
following (NOTE: assumes you followed the default Installation into a Virtual
Environment); note that lines starting with the octothorp ``#`` are comments
to help explain what follows and need not be typed in::

    # Prep your environment by sourcing your Python virtual environment
    $ source $HOME/.virtualenvs/pds-deep-archive/bin/activate

.. note:: The ``source`` command and the location of your Python virtual
    environment may vary depending on the command-line interpreter (terminal)
    you're using and the installation of Python. You may wish to consult a
    system administrator for clarification. In some cases, it may involve
    simply replacing ``source`` with a single period ``.``; in others, it
    may be more involved, especially the location of your Python virtual
    environment.

::

    # The (pds-deep-archive) prefix indicates your virtual environment is active
    (pds-deep-archive) $

.. note:: The changes the the prompt may not necessarily appear depending on
    the local machine environment, command interpreter, etc.

::

    # Now let's run pds-deep-archive
    # NOTE: This software must be run against data on your local filesystem
    (pds-deep-archive) $ pds-deep-archive -s PDS_ATM  \ 
        -b https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/  \
        test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml

.. note:: The trailing backslashes above are "continuation characters" to
    indicate to the command shell that the entire command line spans multiple
    physical lines. You may choose to enter the command on a single long
    physical line without the backslashes. Regardless, please consult your
    documentation regarding what the proper continuation character is for
    your shell; in the most common cases, it is a backslash.


From this command-line execution, we are inputting the following information:

•  ``-s PDS_ATM`` - uses ``-s`` flag to specify Atmospheres Node as the
   provider site for the manifest's label
•  ``-b https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/`` - uses ``-b`` flag Base
   URL for Node data archive. This URL will be prepended to the bundle
   directory to form URLs to the products. For this case, this will allow us
   to form proper URLs in the output manifests based upon the valid online
   products, e.g.
   https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/mission_bundle/LADEE_Bundle_1101.xml
•  ``test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml`` - this is the
   final positional argument input to the software that specifies the bundle
   product file on the local filesystem.

Once you complete this execution, the program will print::

    INFO 👟 PDS Deep Archive, version VERSION-NUMBER
    INFO 🏃‍♀️ Starting AIP generation for test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml
    INFO 🎉 Success! AIP done, files generated:
    INFO 📄 Checksum manifest: ladee_mission_bundle_v1.0_checksum_manifest_v1.0_DATE.tab
    INFO 📄 Transfer manifest: ladee_mission_bundle_v1.0_transfer_manifest_v1.0_DATE.tab
    INFO 📄 XML label for them both: ladee_mission_bundle_v1.0_aip_v1.0_DATE.xml
    INFO 🏃‍♀️ Starting SIP generation for test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml
    INFO 🎉 Success! From /SOME/DIR/test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml, generated these output files:
    INFO 📄 SIP Manifest: ladee_mission_bundle_v1.0_sip_v1.0_DATE.tab
            allCollections=args.include_latest_collection_only,
    INFO 📄 XML label for the SIP: ladee_mission_bundle_v1.0_sip_v1.0_DATE.xml
    INFO 👋 That's it! Thanks for making an AIP and SIP with us today. Bye!

This creates 5 output files in the current directory as part of the AIP and
SIP Generation (with DATE replaced by the current date):

•  ``ladee_mission_bundle_v1.0_checksum_manifest_v1.0_DATE.tab``, the checksum manifest
•  ``ladee_mission_bundle_v1.0_transfer_manifest_v1.0_DATE.tab``, the transfer manifest
•  ``ladee_mission_bundle_v1.0_aip_v1.0_DATE.xml``, the label for these two files
•  ``ladee_mission_bundle_v1.0_sip_v1.0_DATE.tab``, the created SIP manifest as a
   tab-separated values file.
•  ``ladee_mission_bundle_v1.0_sip_v1.0_DATE.xml``, an PDS label for the SIP file.

Be sure to check out the SIP Manifest,
``ladee_mission_bundle_v1.0_sip_v1.0_DATE.tab``, to ensure the URLs included are
valid URLs.

If everything looks good to go, package them up into a PDS Deep Archive data
package (e.g. ``ladee_mission_bundle_v1.0_pds_deep_archive.zip``).

Create a new `PDS4 NSSDCA Delivery Github Issue <https://github.com/NASA-PDS/pdsen-operations/issues/new/choose>`_ for the PDS Engineering Node to submit the package to NSSDCA


Example 2: Bundle Referencing Collections by LID
------------------------------------------------

For running the software on an accumulating bundle, you have two options:

**Option 1: (preferred) Run ``pds-deep-archive`` against the entire bundle and all versions of all collections present beneath the bundle root directory.**

This is the default functionality of ``pds-deep-archive``. See `Example 1: Basic Usage on Local Files`_ to execute using this option.

**Option 2: Run ``pds-deep-archive`` against the bundle with only the current versions of the collections present beneath the bundle root directory.**

Execute the software with the ``--include-latest-collection-only`` flag enabled, for example::

    (pds-deep-archive) $ pds-deep-archive -s PDS_ATM  \ 
        -b https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/  \
        test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml
        --include-latest-collection-only

.. note:: The same admonitions about the command prompt and continuation
    characters mentioned earlier applies to the above example.


Example 3: Generating Deep Archives of Remote Data in a PDS Registry
--------------------------------------------------------------------

Assuming the software is installed properly and the virtual Python environment
is still set up as above, then the following invocation will generate the AIP
checksum and transfer manifests and the SIP manifest for the bundle
``urn:nasa:pds:insight_documents::2.0`` using the PDS Registry API at
``https://pds-gamma.jpl.nasa.gov/api/`` for the site ``PDS_ATM``::

    (pds-deep-archive) $ bin/pds-deep-registry-archive \
        --site PDS_ATM \
        urn:nasa:pds:insight_documents::2.0

.. note:: The same admonitions about the command prompt and continuation
    characters mentioned earlier applies to the above examples.

This writes 5 output files in the current directory as part of the AIP and
SIP Generation, but without needing to read any local files; these files
include:

•  ``insight_documents_v2.0_checksum_manifest_v1.0_DATE.tab``, the checksum manifest
•  ``insight_documents_v2.0_transfer_manifest_v1.0_DATE.tab``, the transfer manifest
•  ``insight_documents_v2.0_aip_v1.0_DATE.xml``, the label for these two files
•  ``insight_documents_v2.0_sip_v1.0_DATE.tab``, the created SIP manifest as a
   tab-separated values file.
•  ``insight_documents_v2.0_sip_v1.0_DATE.xml``, an PDS label for the SIP file.

As of this writing, there may be a couple of issues with PDS Registry APIs
that may affect ``pds-deep-registry-archive``:

•  A `pagination bug`_ may cause some performance issues when making deep
   archives of large bundles. By default, ``pds-deep-registry-archive``
   works around the bug—but if you know the PDS Registry you're using is
   free of the bug, you can add ``--disable-pagination-workaround`` to the
   command. It doesn't hurt if you use it regardless.
•  An `internal server error`_ may appear when certain data is loaded into a
   PDS Registry. By default, though, ``pds-deep-registry-archive`` will treat
   such errors as "not found" instead of as serious errors. However, if you
   prefer to treat the problem as the serious error it really is, add the
   ``--disable-bad-documents-workaround`` option to the command.


PDS Delivery Checklist
----------------------

The following is a checklist and procedure Discipline Node personnel should
follow when delivering a PDS Deep Archive data package to the PDS Engineering
Node upon a new release of data.

For more formalized details on the NSSDCA Delivery Process, see the following `process document <https://github.com/NASA-PDS/pds-deep-archive/tree/master/docs/PDS4_Submission_Process_v1.0.docx>`_.

1.  ▶  START: New Bundle is ready for Delivery.

2.     Verify the Bundle has completed successful validation with PDS4 Validate Tool (no ERRORS).

3.     Execute PDS Deep Archive software per usage instructions and example above.

4.     Check the SIP Manifest (e.g. ``ladee_mission_bundle_v1.0_sip_v1.0_20200618.tab``) file to verify URLs indicated are valid. For example::
    
        # Example of a bad URL
        https://this.url.does.not.exist.com/LADEE_Bundle_1101.xml

        # Example of GOOD URL (file exists online)
        https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/mission_bundle/LADEE_Bundle_1101.xml

5.     Package up the five ``*.tab` and ``*.xml`` files into a ``.ZIP`` or ``.TAR.GZ`` PDS Deep Archive Delivery package. For example::

        tar -cvzf ladee_mission_bundle_v1.0_NSSDCA_20200702.tar.gz ladee_mission_bundle_v1.0_*.tab ladee_mission_bundle_v1.0_*.xml

6.     Create a new `PDS4 NSSDCA Delivery Github Issue <https://github.com/NASA-PDS/pdsen-operations/issues/new/choose>`_ for the PDS Engineering Node to submit the package to NSSDCA.

7.     EN will then complete `validation and submission to NSSDCA <https://pds-engineering.jpl.nasa.gov/content/nssdca_interface_process>`_.

7.     You can then follow along with status in the Github Issue.

8.     The PDS Engineering Node Operations Team will notify you once delivery has been completed.

8.  🎉 DONE


.. _`pagination bug`: https://github.com/NASA-PDS/pds-api/issues/73
.. _`internal server error`: https://github.com/NASA-PDS/registry-api-service/issues/17

