🏃‍♀️ Usage
===========

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

Running ``pds-deep-archive --help`` will give a summary of the
command-line invocation, its required arguments, and any options that refine
the behavior.  For example, to create an AIP from the LADEE 1101 bundle in
``test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml`` run::

    aipgen test/data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml

The program will print::

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

For reference, the full "usage" message from ``pds-deep-archive`` is::

    $ pds-deep-archive --help
    usage: pds-deep-archive [-h] [--version] -s
                            {PDS_ATM,PDS_ENG,PDS_GEO,PDS_IMG,PDS_JPL,PDS_NAI,PDS_PPI,PDS_PSI,PDS_RNG,PDS_SBN}
                            [-n] -b BUNDLE_BASE_URL [-d] [-q]
                            IN-BUNDLE.XML

    Generate an Archive Information Package (AIP) and a Submission Information
    Package (SIP). This creates three files for the AIP in the current directory
    (overwriting them if they already exist):
    ➀ a "checksum manifest" which contains MD5 hashes of *all* files in a product
    ➁ a "transfer manifest" which lists the "lidvids" for files within each XML
      label mentioned in a product
    ➂ an XML label for these two files.

    It also creates two files for the SIP (also overwriting them if they exist):
    ① A "SIP manifest" file; and an XML label of that file too. The names of
      the generated files are based on the logical identifier found in the
      bundle file, and any existing files are overwritten. The names of the
      generated files are printed upon successful completion.
    ② A PDS XML label of that file.

    The files are created in the current working directory when this program is
    run. The names of the files are based on the logical identifier found in the
    bundle file, and any existing files are overwritten. The names of the
    generated files are printed upon successful completion.

    positional arguments:
      IN-BUNDLE.XML         Bundle XML file to read

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -s {PDS_ATM,PDS_ENG,PDS_GEO,PDS_IMG,PDS_JPL,PDS_NAI,PDS_PPI,PDS_PSI,PDS_RNG,PDS_SBN}, --site {PDS_ATM,PDS_ENG,PDS_GEO,PDS_IMG,PDS_JPL,PDS_NAI,PDS_PPI,PDS_PSI,PDS_RNG,PDS_SBN}
                            Provider site ID for the manifest's label
      -n, --offline         Run offline, scanning bundle directory for matching
                            files instead of querying registry service. NOTE: By
                            default, set to True until online mode is available.
      -b BUNDLE_BASE_URL, --bundle-base-url BUNDLE_BASE_URL
                            Base URL for Node data archive. This URL will be
                            prepended to the bundle directory to form URLs to the
                            products. For example, if we are generating a SIP for
                            mission_bundle/LADEE_Bundle_1101.xml, and bundle-base-
                            url is https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/,
                            the URL in the SIP will be https://atmos.nmsu.edu/PDS/
                            data/PDS4/LADEE/mission_bundle/LADEE_Bundle_1101.xml.
      -d, --debug           Log debugging messages for developers
      -q, --quiet           Don't log informational messages