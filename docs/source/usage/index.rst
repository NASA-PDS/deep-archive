🏃‍♀️ Usage
===========

.. toctree::


Overview
--------

This package provides one primary executable, ``pds-deep-archive`` that generates both
and Archive Information Package (AIP) and a Submission Information Package (SIP). The 
SIP is what is delivered by the PDS to the NASA Space Science Data Coordinated Archive (NSSDCA).
For more information about the products produced, see the following references:

•   OAIS Information - http://www.oais.info/
•   AIP Information - https://www.iasa-web.org/tc04/archival-information-package-aip
•   SIP Information - https://www.iasa-web.org/tc04/submission-information-package-sip

This package also comes with the two sub-components of ``pds-deep-archive`` that can be ran
individually:

•  ``aipgen`` that generates Archive Information Packages from a PDS4 bundle
•  ``sipgen`` that generates Submission Information from a PDS4 bundle

Usage Information
-----------------

Running ``pds-deep-archive --help`` will give a summary of the
command-line invocation, its required arguments, and any options that refine
the behavior. 


Example
-------

For example, to create a SIP and AIP from the LADEE 1101 Bundle located at
``test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml`` run the following (NOTE: assumes you followed the default Installation into a Virtual Environment)::

    # Prep your environment by sourcing your Python virtual environment
    $ source $HOME/.virtualenvs/pds-deep-archive/bin/activate

    # The (pds-deep-archive) prefix indicates your virtual environment is active
    (pds-deep-archive) $

    # Now let's run pds-deep-archive
    # NOTE: This software must be run against data on your local filesystem
    (pds-deep-archive) $ pds-deep-archive -s PDS_ATM  \ 
                            -b https://atmos.nmsu.edu/PDS/data/PDS4/LADEE  \
                            test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml

From this command-line execution, we are inputting the following information:

* ``-s PDS_ATM`` - uses ``-s`` flag to specify Atmospheres Node as the provider site for the manifest's label
* ``-b https://atmos.nmsu.edu/PDS/data/PDS4/LADEE`` - uses ``-b`` flag Base URL for Node data archive. This URL will be prepended to the bundle directory to form URLs to the products. For this case, this will allow us to form proper URLs in the output manifests based upon the valid online products, e.g. https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/mission_bundle/LADEE_Bundle_1101.xml
* ``test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml`` - this is the final positional argument input to the software that specifies the bundle product file on the local filesystem.

Once you complete this execution, the program will print::

    INFO 👟 PDS Deep Archive, version 0.0.0
    INFO 🏃‍♀️ Starting AIP generation for test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml

    INFO 🎉  Success! AIP done, files generated:
    INFO • Checksum manifest: ladee_mission_bundle_v1.0_checksum_manifest_v1.0.tab
    INFO • Transfer manifest: ladee_mission_bundle_v1.0_transfer_manifest_v1.0.tab
    INFO • XML label for them both: ladee_mission_bundle_v1.0_aip_v1.0.xml

    INFO 🏃‍♀️ Starting SIP generation for test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml

    INFO 🎉 Success! From /Users/jpadams/Documents/proj/pds/pdsen/workspace/pds-deep-archive/test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml, generated these output files:
    INFO • SIP Manifest: ladee_mission_bundle_v1.0_sip_v1.0.tab
    INFO • XML label for the SIP: ladee_mission_bundle_v1.0_sip_v1.0.xml

    INFO 👋 That's it! Thanks for making an AIP and SIP with us today. Bye!

This creates 5 output files in the current directory as part of the AIP and SIP Generation:

•  ``ladee_mission_bundle_v1.0_checksum_manifest_v1.0.tab``, the checksum manifest
•  ``ladee_mission_bundle_v1.0_transfer_manifest_v1.0.tab``, the transfer manifest
•  ``ladee_mission_bundle_v1.0_aip_v1.0.xml``, the label for these two files

•  ``ladee_mission_bundle_v1.0_sip_v1.0.tab``, the created SIP manifest as a
   tab-separated values file.
•  ``ladee_mission_bundle_v1.0_sip_v1.0.xml``, an PDS label for the SIP file.

Be sure to check out the SIP Manifest, ``ladee_mission_bundle_v1.0_sip_v1.0.tab``, to ensure the URLs included are valid URLs.

If everything looks good to go, package them up into a PDS Deep Archive data package (e.g. ``ladee_mission_bundle_v1.0_pds_deep_archive.zip``).

Email the data package to the `PDS Operator <mailto:pds-operator@jpl.nasa.gov>`_ .


PDS Delivery Checklist
------------------------
The following is a checklist and procedure Discipline Node personnel should follow when delivering a PDS Deep Archive data package to the PDS Engineering Node upon a new release of data:

*  ▶ START: New Bundle is ready for Delivery.
*  Bundle has completed successful validation with PDS4 Validate Tool.
*  Execute PDS Deep Archive software per usage instructions and example above.
*  Check the SIP Manifest (``*._sip_v1.0.tab``) file to verify URLs indicated are valid.
*  Package up the five ``*.tab` and ``*.xml`` files into a ``.ZIP`` or ``.TAR.GZ`` PDS Deep Archive Delivery package.
*  Email PDS Deep Archive Delivery package to the `PDS Operator <mailto:pds-operator@jpl.nasa.gov>`_ for delivery to NSSDCA.
*  Receive confirmation from PDS Operator once delivery has completed.
*  🎉 DONE


