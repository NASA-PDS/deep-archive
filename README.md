# 🪐 PDS Deep Archive Utilities


[![Stable Build](https://github.com/NASA-PDS/pds-deep-archive/workflows/%F0%9F%98%8C%20Stable%20integration%20&%20delivery/badge.svg "Latest stable integration log")](https://github.com/NASA-PDS/pds-deep-archive/actions?query=workflow%3A%22%F0%9F%98%8C+Stable+integration+%26+delivery%2) [![Unstable Build](https://github.com/NASA-PDS/pds-deep-archive/workflows/%F0%9F%A4%AA%20Unstable%20integration%20&%20delivery/badge.svg "Latest unstable integration log")](https://github.com/NASA-PDS/pds-deep-archive/actions?query=workflow%3A%22%F0%9F%A4%AA+Unstable+integration+%26+delivery%22) 


Software for the [Planetary Data System](https://pds.nasa.gov/) to generate Archive Information Package (AIP) and Submission Information Package (SIP) products, based upon [Open Archival Information System](https://www2.archivists.org/groups/standards-committee/open-archival-information-system-oais) standards.


## ✨ Features

- Provides an exectuble Python script `pds-deep-archive`. Run `pds-deep-archive --help` for more details.
- Provides an exectuble Python script `aipgen`. Run `aipgen --help` for more details.
- Provides an exectuble Python script `sipgen`. Run `sipgen --help` for more details.


## ⎆ Installation

See the online documentation for [Installation](https://nasa-pds.github.io/pds-deep-archive/installation/) instructions.
    
You should then be able to run the deep archive utilities:

    (pds-deep-archive) bash> pds-deep-archive --help
    (pds-deep-archive) bash> aipgen --help
    (pds-deep-archive) bash> sipgen --help

👉 _Note:_ The above commands demonstrate typical usage with a command-line prompt, such as that provided by the popular `bash` shell; your own prompt may appear differently and may vary depending on operating system, shell choice, and so forth.


## 👷‍♂️ Build

See the [Development Guide](https://nasa-pds.github.io/pds-deep-archive/development/) for more information.


## 📄 Documentation

Installation and Usage information can be found in the documentation online at https://nasa-pds.github.io/pds-deep-archive/ or the latest version is maintained under the `docs` directory.


### 🐈 Build Sphinx Docs

To build the Sphinx HTML documentation:

    $ python3 -m venv venv
    $ venv/bin/python setup.py develop
    $ venv/bin/python setup.py build_sphinx
    running build_sphinx
    …
    The HTML pages are in build/sphinx/html.


## 🥖 Translations

This product has not been translated into any other languages than US English.


## 👏 Contribute

- Issue Tracker: https://github.com/NASA-PDS/pds-deep-archive/issues
- Source Code: https://github.com/NASA-PDS/pds-deep-archive
- Wiki: https://github.com/NASA-PDS/pds-deep-archive/wiki


## 💁‍♀️ Support

If you are having issues file a bug report in Github: https://github.com/NASA-PDS/pds-deep-archive/issues

Or you can reach us at https://pds.nasa.gov/?feedback=true


## 💳 License

The project is licensed under the Apache License, version 2. See the `LICENSE.txt` file for details.
