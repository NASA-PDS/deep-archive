🏃‍♀️ Usage
=========

This package provides one executable, ``sipgen``, that generates Submission
Information Package (SIP) from PDS bundles.

Running ``sipgen --help`` will give a summary of the command-line invocation,
its required arguments, and any options that refine the behavior.  For
example, to create a SIP from the LADEE 1101 bundle in
``test/data/ladee_test/ladee_mission_bundle/LADEE_Bundle_1101.xml``, run::

    sipgen --s PDS_ATM --offline --bundle-base-url https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/ test/data/ladee_test/ladee_mission_bundle/LADEE_Bundle_1101.xml

The program will print::

    ⚙︎ ``sipgen`` — Submission Information Package (SIP) Generator, version 0.0.0
    🎉 Success! From test/data/ladee_test/ladee_mission_bundle/LADEE_Bundle_1101.xml, generated these output files:
    • Manifest: ladee_mission_bundle_sip_v1.0.tab
    • Label: ladee_mission_bundle_sip_v1.0.xml

And two new files will appear in the current directory:

•  ``ladee_mission_bundle_sip_v1.0.tab``, the created SIP manifest as a
   tab-separated values file.
•  ``ladee_mission_bundle_sip_v1.0.xml``, an PDS label for the SIP file.

For reference, the full "usage" message from ``sipgen`` follows::

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