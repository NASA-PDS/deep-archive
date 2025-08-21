# 🪐 PDS Deep Archive Utilities


[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5750540.svg)](https://doi.org/10.5281/zenodo.5750540) [![Unstable Build](https://github.com/NASA-PDS/deep-archive/workflows/%F0%9F%A4%AA%20Unstable%20integration%20&%20delivery/badge.svg "Latest unstable integration log")](https://github.com/NASA-PDS/deep-archive/actions?query=workflow%3A%22%F0%9F%A4%AA+Unstable+integration+%26+delivery%22) [![Stable Build](https://github.com/NASA-PDS/deep-archive/workflows/%F0%9F%98%8C%20Stable%20integration%20&%20delivery/badge.svg "Latest stable integration log")](https://github.com/NASA-PDS/deep-archive/actions?query=workflow%3A%22%F0%9F%98%8C+Stable+integration+%26+delivery%2)


Software for the [Planetary Data System](https://pds.nasa.gov/) to generate Archive Information Package (AIP) and Submission Information Package (SIP) products, based upon [Open Archival Information System](https://www2.archivists.org/groups/standards-committee/open-archival-information-system-oais) standards.


## ✨ Features

Installing this package will give you two different executable Python programs:

-   `pds-deep-archive` for making Deep Archives of local, on-disk PDS products.
-   `pds-deep-registry-archive` for making Deep Archives of proucts in a PDS Registry server.


## ⎆ Installation

See the online documentation for [Installation](https://nasa-pds.github.io/deep-archive/installation/) instructions.

You should then be able to run the deep archive utilities:

    (pds-deep-archive) bash> pds-deep-archive --help
    (pds-deep-archive) bash> pds-deep-registry-archive --help

👉 _Note:_ The above commands demonstrate typical usage with a command-line prompt, such as that provided by the popular `bash` shell; your own prompt may appear differently and may vary depending on operating system, shell choice, and so forth.


## 👷‍♂️ Build

See the [Development Guide](https://nasa-pds.github.io/deep-archive/development/index.html) for more information.


## 📄 Documentation

Installation and Usage information can be found in the documentation online at https://nasa-pds.github.io/deep-archive/ or the latest version is maintained under the `docs` directory.


### 🐈 Build Sphinx Docs

To build the Sphinx HTML documentation:

```console
$ python3.13 -m venv venv
$ source venv/bin/pip activate
$ pip install --editable '.[dev]
$ sphinx-build --builder html docs/source docs/build
…
The HTML pages are in build/sphinx/html.
```


## 🥖 Translations

This product has not been translated into any other languages than US English.


## 👏 Contribute

All users and developers of the NASA-PDS software are expected to abide by our [Code of Conduct](https://github.com/NASA-PDS/.github/blob/main/CODE_OF_CONDUCT.md). Please read this to ensure you understand the expectations of our community. For information on how to contribute to NASA-PDS codebases please take a look at our [Contributing guidelines](https://github.com/NASA-PDS/.github/blob/main/CONTRIBUTING.md).

- Issue Tracker: https://github.com/NASA-PDS/deep-archive/issues
- Source Code: https://github.com/NASA-PDS/deep-archive
- Wiki: https://github.com/NASA-PDS/deep-archive/wiki


### 💽 Getting Test Data

If you need to mirror a part of a website to add to the test data, try this handy invocation of `wget`:
```console
$ wget \
    --quiet \
    --execute robots=off \
    --cut-dirs=2 \
    --reject='index.html*' \
    --no-host-directories \
    --mirror \
    --no-parent \
    --relative \
    --timestamping \
    --no-check-certificate \
    --recursive \
    "https://whatever/some/path"
```
Note ⑴: Although the author typically reaches for `curl`, it lacks a direct mirroring option—hence `wget` here.

Note ⑵: This is mostly a "note-to-self" for the author of this subsection 😉.


## 💁‍♀️ Support

If you are having issues file a bug report in Github: https://github.com/NASA-PDS/deep-archive/issues

Or you can reach us at https://pds.nasa.gov/?feedback=true


## 💳 License

The project is licensed under the Apache License, version 2. See the `LICENSE.txt` file for details.
