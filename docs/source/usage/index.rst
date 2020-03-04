🏃‍♀️ Usage
===========

This package provides two executables, ``aipgen`` that generats Archive
Information Packages; and ``sipgen``, that generates Submission Information
Package (SIP)—both from PDS bundles.

Running ``aipgen --help`` or ``sipgen --help`` will give a summary of the
command-line invocation, its required arguments, and any options that refine
the behavior.  For example, to create an AIP from the LADEE 1101 bundle in
``test/data/ladee_test/ladee_mission_bundle/LADEE_Bundle_1101.xml`` run::

    aipgen test/data/ladee_test/ladee_mission_bundle/LADEE_Bundle_1101.xml

The program will print::

    INFO 🏃‍♀️ Starting AIP generation for test/data/ladee_test/ladee_mission_bundle/LADEE_Bundle_1101.xml
    INFO 🧾 Writing checksum manifest for /Users/kelly/Documents/Clients/JPL/PDS/Development/pds-deep-archive/test/data/ladee_test/ladee_mission_bundle to ladee_mission_bundle_checksum_manifest_v1.0.tab
    INFO 🚢 Writing transfer manifest for /Users/kelly/Documents/Clients/JPL/PDS/Development/pds-deep-archive/test/data/ladee_test/ladee_mission_bundle to ladee_mission_bundle_transfer_manifest_v1.0.tab
    INFO 🏷  Writing AIP label to ladee_mission_bundle_aip_v1.0.xml
    INFO 🎉  Success! All done, files generated:
    INFO • Checksum manifest: ladee_mission_bundle_checksum_manifest_v1.0.tab
    INFO • Transfer manifest: ladee_mission_bundle_transfer_manifest_v1.0.tab
    INFO • XML label: ladee_mission_bundle_aip_v1.0.xml
    INFO 👋 Thanks for using this program! Bye!

This creates three output files in the current directory as part of the AIP:

•  ``ladee_mission_bundle_checksum_manifest_v1.0.tab``, the checksum manifest
•  ``ladee_mission_bundle_transfer_manifest_v1.0.tab``, the transfer manifest
•  ``ladee_mission_bundle_aip_v1.0.xml``, the label for these two files

The checkum manifest may then be fed into ``sipgen`` to create the SIP::

    sipgen --aip ladee_mission_bundle_checksum_manifest_v1.0.tab ladee_mission_bundle_checksum_manifest_v1.0.tab --s PDS_ATM --offline --bundle-base-url https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/ test/data/ladee_test/ladee_mission_bundle/LADEE_Bundle_1101.xml

This program will print::

    ⚙︎ ``sipgen`` — Submission Information Package (SIP) Generator, version 0.0.0
    🎉 Success! From test/data/ladee_test/ladee_mission_bundle/LADEE_Bundle_1101.xml, generated these output files:
    • Manifest: ladee_mission_bundle_sip_v1.0.tab
    • Label: ladee_mission_bundle_sip_v1.0.xml

And two new files will appear in the current directory:

•  ``ladee_mission_bundle_sip_v1.0.tab``, the created SIP manifest as a
   tab-separated values file.
•  ``ladee_mission_bundle_sip_v1.0.xml``, an PDS label for the SIP file.

For reference, the full "usage" message from ``aipgen`` is::

    usage: aipgen [-h] [-v] IN-BUNDLE.XML

    Generate an Archive Information Package or AIP. An AIP consists of three
    files: ➀ a "checksum manifest" which contains MD5 hashes of *all* files in a
    product; ➁ a "transfer manifest" which lists the "lidvids" for files within
    each XML label mentioned in a product; and ➂ an XML label for these two files.
    You can use the checksum manifest file ➀ as input to ``sipgen`` in order to
    create a Submission Information Package.

    positional arguments:
      IN-BUNDLE.XML  Root bundle XML file to read

    optional arguments:
      -h, --help     show this help message and exit
      -v, --verbose  Verbose logging; defaults False

For reference, the full "usage" message from ``sipgen`` follows::

    usage: sipgen [-h] [-a {MD5,SHA-1,SHA-256}] -s
                  {PDS_ATM,PDS_ENG,PDS_GEO,PDS_IMG,PDS_JPL,PDS_NAI,PDS_PPI,PDS_PSI,PDS_RNG,PDS_SBN}
                  [-u URL | -n] [-k] [-c AIP-CHECKSUM-MANIFEST.TAB]
                  [-b BUNDLE_BASE_URL] [-v] [-i PDS4_INFORMATION_MODEL_VERSION]
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
      -n, --offline         Run offline, scanning bundle directory for matching
                            files instead of querying registry service
      -k, --insecure        Ignore SSL/TLS security issues; default False
      -c AIP-CHECKSUM-MANIFEST.TAB, --aip AIP-CHECKSUM-MANIFEST.TAB
                            Archive Information Product checksum manifest file
      -b BUNDLE_BASE_URL, --bundle-base-url BUNDLE_BASE_URL
                            Base URL prepended to URLs in the generated manifest
                            for local files in "offline" mode
      -v, --verbose         Verbose logging; defaults False
      -i PDS4_INFORMATION_MODEL_VERSION, --pds4-information-model-version PDS4_INFORMATION_MODEL_VERSION
                            Specify PDS4 Information Model version to generate
                            SIP. Must be 1.13.0.0+; default 1.13.0.0
