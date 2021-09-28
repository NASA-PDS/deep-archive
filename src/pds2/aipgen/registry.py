# encoding: utf-8
#
# Copyright © 2021 California Institute of Technology ("Caltech").
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
"""Registry based AIP and SIP"""
# Imports
# =======
import argparse
import dataclasses
import hashlib
import http.client
import logging
import sys
from datetime import datetime

import pds.api_client  # type: ignore

from . import VERSION
from .aip import writeLabel as writeAIPLabel
from .constants import AIP_SIP_DEFAULT_VERSION
from .constants import PDS_LABEL_FILENAME_EXTENSION
from .constants import PDS_TABLE_FILENAME_EXTENSION
from .constants import PROVIDER_SITE_IDS
from .sip import writeLabel as writeSIPLabel
from .utils import addBundleArguments
from .utils import addLoggingArguments


# Constants
# =========
#
# Logging
# -------

_logger = logging.getLogger(__name__)  # The one true logger for PDS
_progressLogging = 100  # How frequently to report PDS progress; every N items


# PDS API Access
# --------------

_apiQueryLimit = 50  # Pagination in the PDS API
_defaultServer = "https://pds-gamma.jpl.nasa.gov/api/"  # Not just the default, the only one I know of 😮


# PDS API property keys we're interested in
# -----------------------------------------

_propDataURL = "ops:Data_File_Info.ops:file_ref"
_propDataMD5 = "ops:Data_File_Info.ops:md5_checksum"
_propLabelURL = "ops:Label_File_Info.ops:file_ref"
_propLabelMD5 = "ops:Label_File_Info.ops:md5_checksum"
_fields = [_propDataURL, _propDataMD5, _propLabelURL, _propLabelMD5]


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
    """A "PDS file" of some kind in the PDS Registry Service whose details we get via the PDS API"""

    url: str
    md5: str


def _deURNLIDVID(lidvid: str) -> tuple[str, str]:
    """Given a PDS ``lidvid`` as a Uniform Resource Name such as ``urn:nasa:pds:whatever::1.0``,
    transform it to a double of ``whatever`` and ``1.0``.
    """
    lid, vid = lidvid.split("::")
    return lid.split(":")[-1], vid


def _makeFilename(lidvid: str, ts: datetime, kind: str, ext: str) -> str:
    """Make a PDS filename for the given ``lidvid`` by dropping its URN prefix, splitting it into
    LID and VID, adding the date part of the ``ts`` timestamp, slapping on the ``kind`` of file it
    is, and the given ``ext``ension, which should already include the ``.``.
    """
    lid, vid = _deURNLIDVID(lidvid)
    slate = ts.date().strftime("%Y%m%d")
    return f"{lid}_v{vid}_{slate}_{kind}_v{AIP_SIP_DEFAULT_VERSION}{ext}"


def _getBundle(apiClient: pds.api_client.ApiClient, lidvid: str) -> pds.api_client.models.product.Product:
    """Using the PDS ``apiClient`` find the PDS bundle with the named ``lidvid`` and return it not as
    an ``pds.api_client.models.product.Bundle`` (which doesn't exist) but as a ``Product``.  If it
    can't be found, return ``None``.
    """
    try:
        _logger.debug("⚙️ Asking ``bundle_by_lidvid`` for %s", lidvid)
        bundles = pds.api_client.BundlesApi(apiClient)
        return bundles.bundle_by_lidvid(lidvid)  # type = ``Product_Bundle``
    except pds.api_client.exceptions.ApiException as ex:
        if ex.status == http.client.NOT_FOUND:
            return None
        else:
            raise


def _getCollections(apiClient: pds.api_client.ApiClient, lidvid: str, workaroundPaginationBug=True):
    """Using the PDS ``apiClient`` generate collections that belong to the PDS bundle ``lidvid``.
    If ``workaroundPaginationBug`` is True, avoid the bug in the count of items returned from the
    ``/bundles/{lidvid}/collections`` endpoint; see NASA-PDS/pds-api#73.
    """
    bcAPI, start = pds.api_client.BundlesCollectionsApi(apiClient), 0
    while True:
        limit = _apiQueryLimit - 1 if workaroundPaginationBug else _apiQueryLimit
        _logger.debug("⚙️ Asking ``collections_of_a_bundle`` for %s at %d limit %d", lidvid, start, limit)
        results = bcAPI.collections_of_a_bundle(lidvid, start=start, limit=limit, fields=_fields)
        if results.data is None:
            return
        start += len(results.data)
        for i in results.data:
            yield i


def _getProducts(apiClient: pds.api_client.ApiClient, lidvid: str):
    """Using the PDS ``apiClient`` generate PDS products that belong to the collection ``lidvid``."""
    cpAPI, start = pds.api_client.CollectionsProductsApi(apiClient), 0
    while True:
        try:
            _logger.debug("⚙️ Asking ``products_of_a_collection`` for %s at %d limit %d", lidvid, start, _apiQueryLimit)
            results = cpAPI.products_of_a_collection(lidvid, start=start, limit=_apiQueryLimit, fields=_fields)
        except pds.api_client.exceptions.ApiException as ex:
            if ex.status == http.client.NOT_FOUND:
                return
            else:
                raise
        if results.data is None:
            return
        start += len(results.data)
        for i in results.data:
            yield i


def _addFiles(product: pds.api_client.models.Product, bac: dict):
    """Add the PDS files described in the PDS ``product`` to the ``bac``."""
    lidvid, props = product.id, product.properties  # Shorthand
    files = bac.get(lidvid, set())  # Get the current set (or a new empty set)
    if _propDataURL in props:  # Are there data files in the product?
        urls, md5s = props[_propDataURL], props[_propDataMD5]  # Get the URLs and MD5s of them
        for url, md5 in zip(urls, md5s):  # For each URL and matching MD5
            files.add(_File(url, md5))  # Add it to the set
    if _propLabelURL in props:  # How about the label itself?
        files.add(_File(props[_propLabelURL][0], props[_propLabelMD5][0]))  # Add it too
    bac[lidvid] = files  # Stash for future use


def _comprehendRegistry(
    url: str, bundleLIDVID: str, allCollections=True, workaroundPaginationBug=True
) -> tuple[int, dict, str]:
    """Query the PDS API at ``url`` for all information about the PDS ``bundleLIDVID`` and return a
    comprehension of it. If ``allCollections`` is True, we include every reference from a collection
    that's LID-only; if it's False, then we only include the latest reference form a LID-only reference.
    A "comprehension of it" means a triple of the common prefix length of all PDS paths referenced
    within it, the "B.A.C." (a dict mapping PDS lidvids to sets of ``_File``s), and the title of
    the PDS bundle.

    Note: currently ``allCollections`` is ignored; see NASA-PDS/pds-api#74.
    """
    _logger.debug("🤔 Comprehending the registry at %s for %s", url, bundleLIDVID)

    # Set up our client connection
    config = pds.api_client.Configuration()
    config.host = url
    apiClient = pds.api_client.ApiClient(config)

    # This is the "B.A.C." 😏
    bac: dict[str, set[_File]]
    bac = {}

    bundle = _getBundle(apiClient, bundleLIDVID)  # There's no class "Bundle" but class Product 🤷‍♀️
    if bundle is None:
        raise ValueError(f"🤷‍♀️ The bundle {bundleLIDVID} cannot be found in the registry at {url}")
    title = bundle.title if bundle.title else "«unknown»"
    _addFiles(bundle, bac)

    bundleURL = bundle.metadata.label_url
    prefixLen = bundleURL.rfind("/") + 1

    # It turns out the PDS registry makes this *trivial* compared to the PDS filesystem version;
    # Just understanding it all was there was the hard part! 😊 THANK YOU! 🙏
    for collection in _getCollections(apiClient, bundleLIDVID, workaroundPaginationBug):
        _addFiles(collection, bac)
        for product in _getProducts(apiClient, collection.id):
            _addFiles(product, bac)

    # C'est tout 🌊
    return prefixLen, bac, title


def _writeChecksumManifest(fn: str, prefixLen: int, bac: dict) -> tuple[str, int, int]:
    """Write an AIP "checksum manifest" to the given ``fn`` PDS filename, stripping ``prefixLen``
    characters off paths, and using information from the ``bac``.  Return a triple of the MD5
    of the manifest, its size in bytes, and a count of the number of entries in it.
    """
    hashish, size, count = hashlib.new("md5"), 0, 0
    with open(fn, "wb") as o:
        for files in bac.values():
            for f in files:
                entry = f"{f.md5}\t{f.url[prefixLen:]}\r\n".encode("utf-8")
                o.write(entry)
                hashish.update(entry)
                size += len(entry)
                count += 1
                if count % _progressLogging == 0:
                    _logger.debug("⏲ Wrote %d entries into the checksum manifest %s", count, fn)
    _logger.info("📄 Wrote AIP checksum manifest %s with %d entries", fn, count)
    return hashish.hexdigest(), size, count


def _writeTransferManifest(fn: str, prefixLen: int, bac: dict) -> tuple[str, int, int]:
    """Write an AIP "transfer manifest" to the named ``fn`` PDS file, stripping ``prefixLen``
    characters off the beginnings of PDS paths, and using info in the ``bac``. Return a triple of
    the MD5 of the created manifest, its size in bytes, and a count of its entries.
    """
    _logger.debug("⚙️ Writing AIP transfer manifest to %s", fn)
    hashish, size, count = hashlib.new("md5"), 0, 0
    with open(fn, "wb") as o:
        for lidvid, files in bac.items():
            for f in files:
                entry = f"{lidvid:255}/{f.url[prefixLen:]:255}\r\n".encode("utf-8")
                o.write(entry)
                hashish.update(entry)
                size += len(entry)
                count += 1
                if count % _progressLogging == 0:
                    _logger.debug("⏲ Wrote %d entries into the transfer manifest %s", count, fn)
    _logger.info("📄 Wrote AIP transfer manifest %s with %d entries", fn, count)
    return hashish.hexdigest(), size, count


def _writeAIP(bundleLIDVID: str, prefixLen: int, bac: dict, ts: datetime) -> str:
    """Create the PDS Archive Information Package for the given ``bundleLIDVID``, stripping
    ``prefixLen`` characters off file paths and using information in the ``bac``.  The ``ts``
    timestamp tells what metadata to put in the PDS label and the date for generated PDS
    filenames. Return a stringified version of the MD5 hash of the *checksum manifest* of the AIP.
    """
    _logger.debug("⚙️ Creating AIP for %s", bundleLIDVID)
    cmFN = _makeFilename(bundleLIDVID, ts, "checksum_manifest", PDS_TABLE_FILENAME_EXTENSION)
    tmFN = _makeFilename(bundleLIDVID, ts, "transfer_manifest", PDS_TABLE_FILENAME_EXTENSION)
    cmMD5, cmSize, cmNum = _writeChecksumManifest(cmFN, prefixLen, bac)
    tmMD5, tmSize, tmNum = _writeTransferManifest(tmFN, prefixLen, bac)
    lid, vid = _deURNLIDVID(bundleLIDVID)
    labelFN = _makeFilename(bundleLIDVID, ts, "aip", PDS_LABEL_FILENAME_EXTENSION)
    writeAIPLabel(labelFN, f"{lid}_v{vid}", lid, vid, cmFN, cmMD5, cmSize, cmNum, tmFN, tmMD5, tmSize, tmNum, ts)
    _logger.info("📄 Wrote label for them both: %s", labelFN)
    return cmMD5


def _writeSIP(bundleLIDVID: str, bac: dict, title: str, site: str, ts: datetime, cmMD5: str):
    """Write a Submission Information Package based on the ``bac`` to the current directory
    generating PDS filenames and other label metadata from the timestamp ``ts`` and ``bundleLIDVID``.
    The ``cmMD5`` is the MD5 digest of the PDS Archive Information Package's transfer manifest and
    also goes into the PDS label. The PDS ``site`` is a string like ``PDS_ATM`` indicating the
    PDS site. You'd think we could get that from the PDS API but 🤷‍♀️.
    """
    _logger.debug("⚙️ Creating SIP for %s (title %s) for site %s", bundleLIDVID, title, site)
    sipFN = _makeFilename(bundleLIDVID, ts, "sip", PDS_TABLE_FILENAME_EXTENSION)
    hashish, size, count = hashlib.new("md5"), 0, 0
    with open(sipFN, "wb") as o:
        for lidvid, files in bac.items():
            for f in files:
                entry = f"{f.md5}\tMD5\t{f.url}\t{lidvid}\r\n".encode("utf-8")
                o.write(entry)
                hashish.update(entry)
                size += len(entry)
                count += 1
                if count % _progressLogging == 0:
                    _logger.debug("⏲ Wrote %d entries into the submission info file %s", count, sipFN)
    _logger.info("📄 Wrote SIP %s with %d entries", sipFN, count)
    labelFN = _makeFilename(bundleLIDVID, ts, "sip", PDS_LABEL_FILENAME_EXTENSION)
    _logger.info("📄 Wrote label for SIP: %s", labelFN)
    with open(labelFN, "wb") as o:
        lid, vid = _deURNLIDVID(bundleLIDVID)
        writeSIPLabel(lid, vid, title, hashish.hexdigest(), size, count, "MD5", sipFN, site, o, cmMD5, ts)


def generateDeepArchive(url: str, bundleLIDVID: str, site: str, allCollections=True, workaroundPaginationBug=True):
    """Make a PDS "deep archive" 🧘 in the current directory (consisting of the Archive Information
    Package's transfer manifest and checksum manifest, and the Submission Information Package's
    table file—plus their corresponding labels) for the named PDS bundle identified by
    ``bundleLIDVID``, for the PDS ``site``, using knowledge in the PDS Registry at ``url``,
    including ``allCollections`` if True else just the latest collection for PDS bundles that reference
    collections by logical identifier only, and neatly avoiding a PDS bug, namely
    the ``workaroundPaginationBug`` if True if a certain PDS registry endpoint doens't handle
    PDS pagination right.
    """

    # When is happening? Make a timestamp and remove the timezone info
    ts = datetime.utcnow()
    ts = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, microsecond=0, tzinfo=None)

    # Figure out what we're dealing with
    prefixLen, bac, title = _comprehendRegistry(url, bundleLIDVID, allCollections, workaroundPaginationBug)

    # Make it rain ☔️
    cmMD5 = _writeAIP(bundleLIDVID, prefixLen, bac, ts)
    _writeSIP(bundleLIDVID, bac, title, site, ts, cmMD5)


def main():
    """Check the command line and make a PDS Deep Archive for the named PDS bundle LIDVID."""
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    addLoggingArguments(parser)
    addBundleArguments(parser)
    parser.add_argument(
        "-u", "--url", default=_defaultServer, help="URL to the PDS API of the PDS Registry to use [%(default)s]"
    )
    parser.add_argument(
        "-s", "--site", required=True, choices=PROVIDER_SITE_IDS, help="Provider site ID for the manifest's label"
    )
    parser.add_argument(
        "--disable-pagination-workaround",
        action="store_true",
        help="By default, this program will sidestep an issue in the PDS Registry that treats pagination "
        'of results from the "collections of a bundle query" as being off by one item; specifiy this option '
        "disables this workaround—see https://github.com/NASA-PDS/pds-api/issues/73 for more information",
    )
    parser.add_argument("bundle", help="LIDVID of the PDS bundle for which to create a PDS Deep Archive")
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, format="%(levelname)s %(message)s")
    _logger.info("👟 PDS Deep Registry-based Archive, version %s", __version__)
    _logger.debug("💢 command line args = %r", args)
    if args.include_latest_collection_only:
        _logger.critical(
            "🙇 SORRY! Including only the latest collection is not yet supported! Please see "
            "https://github.com/NASA-PDS/pds-api/issues/74 and for now re-run without --include-latest-collection-only"
        )
        sys.exit(1)

    _logger.debug("%r", args)
    try:
        generateDeepArchive(
            args.url,
            args.bundle,
            args.site,
            not args.include_latest_collection_only,
            not args.disable_pagination_workaround,
        )
    except pds.api_client.exceptions.ApiException as ex:
        if ex.status == http.client.INTERNAL_SERVER_ERROR:
            _logger.critical(
                "🚨 The server at %s gave an INTERNAL SERVER ERROR; you should contact its administrator if you "
                "can figure out who that is. The following information may be helpful to them in figuring out "
                "the issue: «%r»",
                args.url,
                ex.body,
            )
            sys.exit(-2)
        _logger.exception("💥 We got an unexpected error; sorry it didn't work out")
        sys.exit(-3)
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
# if aip: _writeAIP(bundleLIDVID, prefixLen, bac, ts)
# if sip: _writeSIP(bundleLIDVID, bac, ts)
#
# # xxx = bcAPI.collections_of_a_bundle(bundleLIDVID)  # type of each = ``Product_Collection``
# # xxx = bcAPI.collections_of_a_bundle(bundleLIDVID, fields=['ops:Label_File_Info.ops:md5_checksum'])  # type of each = ``Product_Collection``
#
# # The lidvid below comes from one of the responses iterating over xxx.data:
# print('before')
# for product in cpAPI.products_of_a_collection('urn:nasa:pds:insight_documents:document_hp3rad::8.0').data:
#     print(product.id)
# print('after')
# for product in _getProducts(apiClient, 'urn:nasa:pds:insight_documents:document_hp3rad::8.0'):
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
# Using the https://pds-gamma.jpl.nasa.gov/api/ directly (without the Python pds.api_client):
#
# We are normally passed a bundle.xml file; we can get its info directly with:
#
#     curl -X GET --header 'Accept: application/pds4+xml' 'https://pds-gamma.jpl.nasa.gov/api/bundles/urn%3Anasa%3Apds%3Ainsight_documents%3A%3A2.0'
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
