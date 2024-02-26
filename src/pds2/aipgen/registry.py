# encoding: utf-8
#
# Copyright © 2021–2024 California Institute of Technology ("Caltech").
# ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# • Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# • Redistributions must reproduce the above copyright notice, this list of
#   conditions and the following disclaimer in the documentation and/or other
#   materials provided with the distribution.
# • Neither the name of Caltech nor its operating division, the Jet Propulsion
#   Laboratory, nor the names of its contributors may be used to endorse or
#   promote products derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Registry based AIP and SIP."""
# Imports
# =======
import argparse
import dataclasses
import hashlib
import logging
import sys
from datetime import datetime
from http import HTTPStatus
from typing import Any
from typing import Iterator
from typing import Union

import requests

from . import VERSION
from .aip import writelabel as writeaiplabel
from .constants import AIP_SIP_DEFAULT_VERSION
from .constants import PDS_LABEL_FILENAME_EXTENSION
from .constants import PDS_TABLE_FILENAME_EXTENSION
from .constants import PROVIDER_SITE_IDS
from .sip import writelabel as writesiplabel
from .utils import addbundlearguments
from .utils import addloggingarguments


# Constants
# =========
#
# Logging
# -------

_logger = logging.getLogger(__name__)  # The one true logger for PDS
_progresslogging = 100  # How frequently to report PDS progress; every N items


# PDS API Access
# --------------

_apiquerylimit = 50  # Pagination in the PDS API
_defaultserver = "https://pds.nasa.gov/api/search/1.0/"  # Where to find the PDS API
_searchkey = "ops:Harvest_Info.ops:harvest_date_time"  # How to sort products


# PDS API property keys we're interested in
# -----------------------------------------

_propdataurl = "ops:Data_File_Info.ops:file_ref"
_propdatamd5 = "ops:Data_File_Info.ops:md5_checksum"
_proplabelurl = "ops:Label_File_Info.ops:file_ref"
_proplabelmd5 = "ops:Label_File_Info.ops:md5_checksum"
_fields = [_propdataurl, _propdatamd5, _proplabelurl, _proplabelmd5]


# Program/Module Metadata
# -----------------------

_description = """Generate "PDS deep archives" of PDS data bundles from the PDS Registry Service, which
includes PDS Archive Information Packages (AIPs) and PDS Submission Information Packages (SIPs). If you
have a PDS bundle locally in your filesystem, use ``pds-deep-archive`` instead. This program is intended
for when the PDS bundle is remotely available via the HTTP PDS application programmer interface (API)."""
__version__ = VERSION


# Classes
# =======


@dataclasses.dataclass(order=True, frozen=True)
class _File:
    """A "PDS file" of some kind in the PDS Registry Service whose details we get via the PDS API."""

    url: str
    md5: str


def _deurnlidvid(lidvid: str) -> tuple[str, str]:
    """De-URN a LID VID.

    Given a PDS ``lidvid`` as a Uniform Resource Name such as ``urn:nasa:pds:whatever::1.0``,
    transform it to a double of ``whatever`` and ``1.0``.
    """
    lid, vid = lidvid.split("::")
    return lid.split(":")[-1], vid


def _splitlidvid(lidvid: str) -> tuple[str, str]:
    """Split a LIDVID into a LID and VID.

    Given a PDS ``lidvid`` as a Uniform Resource Name such as ``urn:nasa:pds:whatever::1.0``,
    transform it to a double of ``urn:nasa:pds:whatever`` and ``1.0``.
    """
    lid, vid = lidvid.split("::")
    return lid, vid


def _makefilename(lidvid: str, ts: datetime, kind: str, ext: str) -> str:
    """Make a filename.

    Make a PDS filename for the given ``lidvid`` by dropping its URN prefix, splitting it into
    LID and VID, adding the date part of the ``ts`` timestamp, slapping on the ``kind`` of file it
    is, and the given ``ext``ension, which should already include the ``.``.
    """
    lid, vid = _deurnlidvid(lidvid)
    slate = ts.date().strftime("%Y%m%d")
    return f"{lid}_v{vid}_{slate}_{kind}_v{AIP_SIP_DEFAULT_VERSION}{ext}"


def _getbundle(server_url: str, lidvid: str) -> Union[dict[str, Any], None]:
    """Get a bundle.

    Using the PDS API server at ``server_url`` ask for the bundle with the
    identifier ``lidvid`` and return a ``dict`` with its attributes.
    If it can't be found, return ``None``.
    """
    r = requests.get(f"{server_url}/products/{lidvid}")
    if r.status_code == HTTPStatus.NOT_FOUND:
        return None
    return r.json()


def _getproducts(server_url: str, lidvid: str, allcollections=True) -> Iterator[dict[str, Any]]:
    """Get products (which could be collections of a dataset or products of a collection).

    Using the PDS API server at ``server_url`` generate products that belong to ``lidvid``.

    If ``allcollections`` is True, then return all collections for LID-only references; otherwise
    return just the latest collection for LID-only references (has no effect on full LIDVID-references).
    """
    url = f"{server_url}/products/{lidvid}/members/{'all' if allcollections else 'latest'}"
    params = {"sort": _searchkey, "limit": _apiquerylimit}
    while True:
        _logger.debug('Making request to %s with params %r', url, params)
        r = requests.get(url, params=params)
        matches = r.json()["data"]
        num_matches = len(matches)
        for i in matches:
            yield i
        if num_matches < _apiquerylimit:
            break
        params["search-after"] = matches[-1]["properties"][_searchkey]


def _addfiles(product: dict, bac: dict):
    """Add the PDS files described in the PDS ``product`` to the ``bac``."""
    lidvid, props = product["id"], product["properties"]
    files = bac.get(lidvid, set())  # Get the current set (or a new empty set)

    if _propdataurl in props:  # Are there data files in the product?
        urls, md5s = props[_propdataurl], props[_propdatamd5]  # Get the URLs and MD5s of them
        for url, md5 in zip(urls, md5s):  # For each URL and matching MD5
            files.add(_File(url, md5))  # Add it to the set
    if _proplabelurl in props:  # How about the label itself?
        files.add(_File(props[_proplabelurl][0], props[_proplabelmd5][0]))  # Add it too
    bac[lidvid] = files  # Stash for future use


def _comprehendregistry(url: str, bundlelidvid: str, allcollections=True) -> tuple[int, dict, str]:
    """Fathom the registry.

    Query the PDS API at ``url`` for all information about the PDS ``bundlelidvid`` and return a
    comprehension of it. If ``allcollections`` is True, we include every reference from a collection
    that's LID-only; if it's False, then we only include the latest reference form a LID-only reference.
    A "comprehension of it" means a triple of the common prefix length of all PDS paths referenced
    within it, the "B.A.C." (a dict mapping PDS lidvids to sets of ``_File``s), and the title of
    the PDS bundle.

    If ``allcollections`` is True, we include all collections, meaning that if a bundle references
    a collection with LID only (no VID), we include all version IDs of that collection. When this
    flag ``allcollections`` is False, then we include only the *latest* collection for a LID-only
    reference.
    """
    _logger.debug("🤔 Comprehending the registry at %s for %s", url, bundlelidvid)

    # Set up our client connection

    # This is the "B.A.C." 😏
    bac: dict[str, set[_File]]
    bac = {}

    bundle = _getbundle(url, bundlelidvid)
    if bundle is None:
        raise ValueError(f"🤷‍♀️ The bundle {bundlelidvid} cannot be found in the registry at {url}")
    title = bundle.get("title", "«unknown»")
    _addfiles(bundle, bac)
    bundleurl = bundle["metadata"]["label_url"]
    prefixlen = bundleurl.rfind("/") + 1

    # It turns out the PDS registry makes this *trivial* compared to the PDS filesystem version;
    # Just understanding it all was there was the hard part! 😊 THANK YOU! 🙏
    for collection in _getproducts(url, bundlelidvid, allcollections):
        _addfiles(collection, bac)
        for product in _getproducts(url, collection["id"]):
            _addfiles(product, bac)

    # C'est tout 🌊
    return prefixlen, bac, title


def _writechecksummanifest(fn: str, prefixlen: int, bac: dict) -> tuple[str, int, int]:
    """Write an AIP "checksum manifest".

    This writes an AIP "checksum manifest" to the given ``fn`` PDS filename, stripping ``prefixlen``
    characters off paths, and using information from the ``bac``.  Return a triple of the MD5
    of the manifest, its size in bytes, and a count of the number of entries in it.
    """
    hashish, size, count = hashlib.new("md5"), 0, 0
    with open(fn, "wb") as o:
        for files in bac.values():
            for f in files:
                entry = f"{f.md5}\t{f.url[prefixlen:]}\r\n".encode("utf-8")
                o.write(entry)
                hashish.update(entry)
                size += len(entry)
                count += 1
                if count % _progresslogging == 0:
                    _logger.debug("⏲ Wrote %d entries into the checksum manifest %s", count, fn)
    _logger.info("📄 Wrote AIP checksum manifest %s with %d entries", fn, count)
    return hashish.hexdigest(), size, count


def _writetransfermanifest(fn: str, prefixlen: int, bac: dict) -> tuple[str, int, int]:
    """Write an AIP "transfer manifest".

    This writes an AIP "transfer manifest" to the named ``fn`` PDS file, stripping ``prefixlen``
    characters off the beginnings of PDS paths, and using info in the ``bac``. Return a triple of
    the MD5 of the created manifest, its size in bytes, and a count of its entries.
    """
    _logger.debug("⚙️ Writing AIP transfer manifest to %s", fn)
    hashish, size, count = hashlib.new("md5"), 0, 0
    with open(fn, "wb") as o:
        for lidvid, files in bac.items():
            for f in files:
                entry = f"{lidvid:255}/{f.url[prefixlen:]:254}\r\n".encode("utf-8")  # 254 because we hard-code the /
                o.write(entry)
                hashish.update(entry)
                size += len(entry)
                count += 1
                if count % _progresslogging == 0:
                    _logger.debug("⏲ Wrote %d entries into the transfer manifest %s", count, fn)
    _logger.info("📄 Wrote AIP transfer manifest %s with %d entries", fn, count)
    return hashish.hexdigest(), size, count


def _writeaip(bundlelidvid: str, prefixlen: int, bac: dict, ts: datetime) -> str:
    """Create the PDS Archive Information Package.

    This creates the PDS Archive Information Package for the given ``bundlelidvid``, stripping
    ``prefixlen`` characters off file paths and using information in the ``bac``.  The ``ts``
    timestamp tells what metadata to put in the PDS label and the date for generated PDS
    filenames. Return a stringified version of the MD5 hash of the *checksum manifest* of the AIP.
    """
    _logger.debug("⚙️ Creating AIP for %s", bundlelidvid)
    cmfn = _makefilename(bundlelidvid, ts, "checksum_manifest", PDS_TABLE_FILENAME_EXTENSION)
    tmfn = _makefilename(bundlelidvid, ts, "transfer_manifest", PDS_TABLE_FILENAME_EXTENSION)
    cmmd5, cmsize, cmnum = _writechecksummanifest(cmfn, prefixlen, bac)
    tmmd5, tmsize, tmnum = _writetransfermanifest(tmfn, prefixlen, bac)
    labelfn = _makefilename(bundlelidvid, ts, "aip", PDS_LABEL_FILENAME_EXTENSION)
    lid, vid = _splitlidvid(bundlelidvid)
    writeaiplabel(labelfn, f"{lid}_v{vid}", lid, vid, cmfn, cmmd5, cmsize, cmnum, tmfn, tmmd5, tmsize, tmnum, ts)
    _logger.info("📄 Wrote label for them both: %s", labelfn)
    return cmmd5


def _writesip(bundlelidvid: str, bac: dict, title: str, site: str, ts: datetime, cmmd5: str):
    """Write a Submission Information Package.

    This writes a Submission Information Package based on the ``bac`` to the current directory
    generating PDS filenames and other label metadata from the timestamp ``ts`` and ``bundlelidvid``.
    The ``cmmd5`` is the MD5 digest of the PDS Archive Information Package's transfer manifest and
    also goes into the PDS label. The PDS ``site`` is a string like ``PDS_ATM`` indicating the
    PDS site. You'd think we could get that from the PDS API but 🤷‍♀️.
    """
    _logger.debug("⚙️ Creating SIP for %s (title %s) for site %s", bundlelidvid, title, site)
    sipfn = _makefilename(bundlelidvid, ts, "sip", PDS_TABLE_FILENAME_EXTENSION)
    hashish, size, count = hashlib.new("md5"), 0, 0
    with open(sipfn, "wb") as o:
        for lidvid, files in bac.items():
            for f in files:
                entry = f"{f.md5}\tMD5\t{f.url}\t{lidvid}\r\n".encode("utf-8")
                o.write(entry)
                hashish.update(entry)
                size += len(entry)
                count += 1
                if count % _progresslogging == 0:
                    _logger.debug("⏲ Wrote %d entries into the submission info file %s", count, sipfn)
    _logger.info("📄 Wrote SIP %s with %d entries", sipfn, count)
    labelfn = _makefilename(bundlelidvid, ts, "sip", PDS_LABEL_FILENAME_EXTENSION)
    _logger.info("📄 Wrote label for SIP: %s", labelfn)
    with open(labelfn, "wb") as o:
        lid, vid = _splitlidvid(bundlelidvid)
        writesiplabel(lid, vid, title, hashish.hexdigest(), size, count, "MD5", sipfn, site, o, cmmd5, ts)


def generatedeeparchive(url: str, bundlelidvid: str, site: str, allcollections=True):
    """Make a PDS "deep archive" 🧘 in the current directory.

    A PDS "deep archive" 🧘‍♀️ (consisting of the Archive Information Package's transfer manifest and
    checksum manifest, and the Submission Information Package's table file—plus their corresponding
    labels) for the named PDS bundle identified by ``bundlelidvid``, for the PDS ``site``, using knowledge
    in the PDS Registry at ``url``, including ``allcollections`` if True else just the latest collection
    for PDS bundles that reference collections by logical identifier only.
    """
    # When is happening? Make a timestamp and remove the timezone info
    ts = datetime.utcnow()
    ts = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, microsecond=0, tzinfo=None)

    # Figure out what we're dealing with
    prefixlen, bac, title = _comprehendregistry(url, bundlelidvid, allcollections)

    # Make it rain ☔️
    cmmd5 = _writeaip(bundlelidvid, prefixlen, bac, ts)
    _writesip(bundlelidvid, bac, title, site, ts, cmmd5)


def main():
    """Check the command line and make a PDS Deep Archive for the named PDS bundle LIDVID."""
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    addloggingarguments(parser)
    addbundlearguments(parser)
    parser.add_argument(
        "-u", "--url", default=_defaultserver, help="URL to the PDS API of the PDS Registry to use [%(default)s]"
    )
    parser.add_argument(
        "-s", "--site", required=True, choices=PROVIDER_SITE_IDS, help="Provider site ID for the manifest's label"
    )
    parser.add_argument("bundle", help="LIDVID of the PDS bundle for which to create a PDS Deep Archive")
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, format="%(levelname)s %(message)s")
    _logger.info("👟 PDS Deep Registry-based Archive, version %s", __version__)
    _logger.debug("💢 command line args = %r", args)
    try:
        generatedeeparchive(args.url, args.bundle, args.site, not args.include_latest_collection_only)
    except Exception:
        _logger.exception("💥 We got an unexpected error; sorry it didn't work out")
        sys.exit(-1)
    finally:
        _logger.info("👋 Thanks for using this program! Bye!")
    sys.exit(0)


if __name__ == "__main__":
    main()


# Notes
# =====
#
# The following are stream-of-consciousness notes I made while developing this and may be ignored:
#
# matches = bundles.get_bundles(q='livi eq urn:nasa:pds:insight_documents:document_hp3rad::5.0')
# matches = collections.get_collection(q='lidvid eq urn:nasa:pds:insight_documents:document_hp3rad::5.0')
# matches = products.products(q='lidvid eq urn:nasa:pds:insight_documents:document_hp3rad::5.0', start=0, limit=9999)
# matches = otherAPI.products_of_a_collection('urn:nasa:pds:insight_documents:document_hp3rad::8.0', start=0, limit=999)
# print(matches)

# We can do this way:
# matches = bundles.get_bundles(q='lidvid eq {lidvid}"')

# Or we can do it this way:
# bundle = bundles.bundle_by_lidvid('urn:nasa:pds:insight_documents::2.0')
# At this point we have:
# - bundle.id - the lidvid
# - Possible filepath entry:
#   - bundle.metadata.label_url ???
#   - ops:Label_File_Info.ops:file_ref ???
# - ops:Label_File_Info.ops:md5_checksum
# - bundle.type - if this is "Product_Collection" then we can say "isProductCollection" is True
#   - May not have to worry about this? API might actually collate this for us
# - bundle.properties
#   - pds:Bundle_Member_Entry.pds:lid_reference (perhaps there is pds:Bundle_Member_Entry.pds:lidvd_reference)?
#   - pds:Bundle_Member_Entry.pds:member_status (Primary or Secondary)
#
# - ops:Data_File_Info.ops:md5_checksum
# - ops:Data_File_Info.ops:file_ref - maybe we can make the filepath out of this?
# pprint(bundle)
#
# if aip: _writeaip(bundlelidvid, prefixlen, bac, ts)
# if sip: _writesip(bundlelidvid, bac, ts)
#
# # xxx = bcapi.collections_of_a_bundle(bundlelidvid)  # type of each = ``Product_Collection``
# # xxx = bcapi.collections_of_a_bundle(bundlelidvid,
#     fields=['ops:Label_File_Info.ops:md5_checksum'])  # type of each = ``Product_Collection``
#
# # The lidvid below comes from one of the responses iterating over xxx.data:
# print('before')
# for product in cpapi.products_of_a_collection('urn:nasa:pds:insight_documents:document_hp3rad::8.0').data:
#     print(product.id)
# print('after')
# for product in _getproducts(apiclient, 'urn:nasa:pds:insight_documents:document_hp3rad::8.0'):
#     print(product.id)
# return

# Approach then:
# Get the bundle (to see if it's valid mostly but also get its fileref + md5)
# Add the bundle + md5 to the b-a-collection
# For each collection of the bundle:
#       add the collection + md5 to the b-a-collection
#       add any ops:Data_File_Info.ops:file_ref + md5 to the b-a-collection
#       for each product of a collection:
#           add the product + md5 to the b-a-collection
#           add the file_ref + md5 to the b-a-collection
# Then write out the sip and aip of the b-a-collection
#
# Tables
# - labels (lid, vid)
# - inter_table_references (lid, vid, to_lid, to_vid (may be null))
# - label_file_references (lid, vid, filepath)
#
# We may have to dump all that because the registry API seems to give a lot of data immediately
# blobs? blobs???
#
# Using the https://pds.nasa.gov/api/search/1.0/ directly (without the Python pds.api_client):
#
# We are normally passed a bundle.xml file; we can get its info directly with:
#
#     curl -X GET --header 'Accept: application/vnd.nasa.pds.pds4+xml' \
#         'https://pds.nasa.gov/api/search/1.0/bundles/urn%3Anasa%3Apds%3Ainsight_documents%3A%3A2.0'
#
# This gives:
#
#     <?xml version="1.0" encoding="UTF-8"?>
#     <?xml-model href="https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1B00.sch" schematypens="http://purl.oclc.org/dsdl/schematron"?>
#     <Product_Bundle
#         xmlns="http://pds.nasa.gov/pds4/pds/v1"
#         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#         xsi:schemaLocation="http://pds.nasa.gov/pds4/pds/v1 https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1B00.xsd">
#         <Identification_Area> …
#         …
#         <File_Area_Text>
#               <File>
#                     <file_name>readme.txt</file_name>
#                     <comment>Introduction to the bundle</comment>
#               </File>
#
#         …
#         <Bundle_Member_Entry>
#               <lid_reference>urn:nasa:pds:insight_documents:document_mission</lid_reference>
#               <member_status>Primary</member_status>
#               <reference_type>bundle_has_document_collection</reference_type>
#         </Bundle_Member_Entry>
#         …
#         <Bundle_Member_Entry>
#               <lid_reference>urn:nasa:pds:insight_documents:document_hp3rad</lid_reference>
#               <member_status>Primary</member_status>
#               <reference_type>bundle_has_document_collection</reference_type>
#         </Bundle_Member_Entry>
#         …
