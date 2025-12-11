# encoding: utf-8
#
# Copyright © 2019–2021 California Institute of Technology ("Caltech").
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
"""Submission Information Package."""
import argparse
import hashlib
import logging
import os.path
import shutil
import sqlite3
import sys
import tempfile
import urllib.request
from datetime import datetime
from urllib.parse import urlparse

from lxml import etree
from zope.component import provideUtility  # type: ignore
from zope.component import queryUtility  # type: ignore

from . import VERSION
from .constants import AIP_PRODUCT_URI_PREFIX
from .constants import AIP_SIP_DEFAULT_VERSION
from .constants import HASH_ALGORITHMS
from .constants import INFORMATION_MODEL_VERSION
from .constants import PDS_LABEL_FILENAME_EXTENSION
from .constants import PDS_NS_URI
from .constants import PDS_SCHEMA_URL
from .constants import PDS_TABLE_FILENAME_EXTENSION
from .constants import PROVIDER_SITE_IDS
from .constants import SIP_MANIFEST_URL
from .constants import XML_MODEL_PI
from .constants import XML_SCHEMA_INSTANCE_NS_URI
from .interfaces import IURLValidator
from .utils import addbundlearguments
from .utils import addloggingarguments
from .utils import comprehenddirectory
from .utils import createschema
from .utils import getdigest
from .utils import getlogicalversionidentifier
from .utils import getmd5
from .utils import parsexml
from .utils import URLValidator


# Defaults & Constants
# --------------------

# Module metadata:
__version__ = VERSION

# Program related info, for --help; note this is hand-wrapped at 80 columns:
_description = """Generate Submission Information Packages (SIPs) from bundles.
This program takes a bundle XML file as input and produces two output files:

① A Submission Information Package (SIP) manifest file; and
② A PDS XML label of that file.

The files are created in the current working directory when this program is
run. The names of the files are based on the logical identifier found in the
bundle file, and any existing files are overwritten. The names of the
generated files are printed upon successful completion.
"""

# Other constants and defaults:
_registryserviceurl = "https://pds.nasa.gov/services/registry/pds"  # Default registry service; for future use?

# URI prefix for logical identifiers of Submission Information Package bundles
_sipdeepuriprefix = "urn:nasa:pds:system_bundle:product_sip_deep_archive:"

# Boilerplate
_stdmanifestdescription = "Tab-separated manifest table for delivering one bundle to the Deep Archive"

# Record boilerplate; first is column name, second is its description (all records are ASCII_String in PDS parlance)
_recordboilerplate = (
    ("checksum", "Checksum Value"),
    ("checksum_type", "Checksum Type"),
    ("file_specification_url", "URL to file associated with checksum in field #1 and product lidvid in field #3"),
    ("LIDVID", "Unique product lidvid that contains this file"),
)

# Internal reference boilerplate
_intrefboilerplate = "Links this SIP to the specific version of the bundle product in the PDS registry system"


# Logging
# -------

_logger = logging.getLogger(__name__)


# Functions
# ---------


def _getdigests(lidvidstofiles, hashname):
    """Get digests.

    ``lidvidstofiles`` is a mapping of lidvid (string) to a set of matching file URLs.
    Using a digest algorithm identified by ``hashname``, retrieve each URL's content and cmpute
    its digest. Return a sequence of triples of (url, digest (hex string), and lidvid)
    """
    _logger.debug("∛ Computing digests for %d files using %s", sum([len(i) for i in lidvidstofiles.values()]), hashname)

    withdigests = []
    # TODO: potential optimization is that if the same file appears for multiple lidvids we retrieve it
    # multiple times; we could cache previous hash computations.
    # 🩹 BANDAID: ``getdigests`` has an LRU cache.
    for lidvid, files in lidvidstofiles.items():
        for url in files:
            try:
                d = getdigest(url, hashname)
                withdigests.append((url, d, lidvid))
            except urllib.error.URLError as error:
                _logger.info("Problem retrieving «%s» for digest: %r; ignoring", url, error)
    return withdigests


def _writetable(hashedfiles, hashname, manifest, baseurl, bp):
    """Write a table.

    For each file in ``hashedfiles`` (a triple of file URL, digest, and lidvid), write a tab
    separated sequence of lines onto ``manifest`` with the columns containing the digest,
    the name of the hasing algorithm that produced the digest, the URL to the file, and the
    lidvid. Return a hex conversion of the MD5 digest of the manifest plus the total bytes
    written.  ``bp`` is the base path that'll get stripped from URLs before writing.
    """
    _logger.debug("⎍ Writing SIP table with hash %s", hashname)
    hashish, size, hashname, count, bp = hashlib.new("md5", usedforsecurity=False), 0, hashname.upper(), 0, bp.replace("\\", "/")
    for url, digest, lidvid in sorted(hashedfiles):
        if baseurl.endswith("/"):
            baseurl = baseurl[:-1]
        url = baseurl + urlparse(url).path.replace(bp, "")

        # https://github.com/NASA-PDS/pds-deep-archive/issues/102:
        #
        # Normally I wouldn't have the guard for ``None`` in here, but many, many tests in the
        # functional test suite use bad URLs. Rather than try to modify every last test to use
        # always-available URLs, we simply don't install a URL validator.
        #
        # Oh and I added a command-line flag to disable validation, ``--disable-url-validation`` 😉
        validator = queryUtility(IURLValidator)
        if validator is not None:
            validator.validate(url)

        entry = f"{digest}\t{hashname}\t{url}\t{lidvid.strip()}\r\n".encode("utf-8")
        hashish.update(entry)
        manifest.write(entry)
        size += len(entry)
        count += 1
        if count % 100 == 0:
            _logger.info("⏰ Wrote %d entries into the SIP", count)
    return hashish.hexdigest(), size


def writelabel(
    logicalid,
    versionid,
    title,
    digest,
    size,
    numentries,
    hashname,
    manifestfile,
    site,
    labeloutputfile,
    aipfile,
    timestamp,
):
    """Write a label.

    Write an XML label to the file ``labeloutputfile``. Note that ``digest`` is a hex version
    of the *MD5* digest of the generated manifest, but ``hashname`` is the name of the hash algorithm
    used to produce the *contents* of the manifest, which may be MD5 or something else.

    The ``aipfile`` is a read-stream to the Archive Infomration Package (AIP) which we use
    to write an MD5 hash into this label. Or it's a hex string of the MD5. But if it's not given
    at all (i.e., is ``None``, we default to writing an MD5 of zeros.

    The ``timestamp`` is a ``datetime`` object that tells what creation date to use in the label.
    """
    _logger.debug("🏷  Writing SIP label to %s", labeloutputfile)

    # Set up convenient prefixes for XML namespaces
    nsmap = {None: PDS_NS_URI, "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    prefix = f"{{{PDS_NS_URI}}}"

    # Root of the XML document: Product_SIP_Deep_Archive
    root = etree.Element(
        prefix + "Product_SIP_Deep_Archive",
        attrib={f"{{{XML_SCHEMA_INSTANCE_NS_URI}}}" + "schemaLocation": PDS_SCHEMA_URL},
        nsmap=nsmap,
    )

    identificationarea = etree.Element(prefix + "Identification_Area")
    root.append(identificationarea)
    logicalidentifier = (
        _sipdeepuriprefix + logicalid.split(":")[-1] + "_v" + versionid + "_" + timestamp.date().strftime("%Y%m%d")
    )
    etree.SubElement(identificationarea, prefix + "logical_identifier").text = logicalidentifier
    etree.SubElement(identificationarea, prefix + "version_id").text = AIP_SIP_DEFAULT_VERSION
    etree.SubElement(identificationarea, prefix + "title").text = "Submission Information Package for the " + title
    etree.SubElement(identificationarea, prefix + "information_model_version").text = INFORMATION_MODEL_VERSION
    etree.SubElement(identificationarea, prefix + "product_class").text = "Product_SIP_Deep_Archive"

    modificationhistory = etree.Element(prefix + "Modification_History")
    identificationarea.append(modificationhistory)
    modificationdetail = etree.Element(prefix + "Modification_Detail")
    modificationhistory.append(modificationdetail)
    etree.SubElement(modificationdetail, prefix + "modification_date").text = timestamp.date().isoformat()
    etree.SubElement(modificationdetail, prefix + "version_id").text = AIP_SIP_DEFAULT_VERSION
    etree.SubElement(modificationdetail, prefix + "description").text = "SIP was versioned and created"

    deep = etree.Element(prefix + "Information_Package_Component_Deep_Archive")
    root.append(deep)
    deep.append(etree.Comment("MD5 digest checksum for the manifest file"))
    etree.SubElement(deep, prefix + "manifest_checksum").text = digest
    etree.SubElement(deep, prefix + "checksum_type").text = "MD5"
    etree.SubElement(deep, prefix + "manifest_url").text = SIP_MANIFEST_URL + str(timestamp.year) + "/" + manifestfile
    etree.SubElement(deep, prefix + "aip_lidvid").text = (
        AIP_PRODUCT_URI_PREFIX
        + logicalid.split(":")[-1]
        + "_v"
        + versionid
        + "_"
        + timestamp.date().strftime("%Y%m%d")
        + "::1.0"
    )

    if isinstance(aipfile, str):
        aipmd5 = aipfile
    elif aipfile is not None:
        aipmd5 = getmd5(aipfile)
    else:
        aipmd5 = "00000000000000000000000000000000"
    etree.SubElement(deep, prefix + "aip_label_checksum").text = aipmd5

    deepfilearea = etree.Element(prefix + "File_Area_SIP_Deep_Archive")
    deep.append(deepfilearea)
    f = etree.Element(prefix + "File")
    deepfilearea.append(f)
    etree.SubElement(f, prefix + "file_name").text = os.path.basename(manifestfile)
    f.append(etree.Comment("Creation date time in formation YYYY-MM-DDTHH:mm:ss"))
    etree.SubElement(f, prefix + "creation_date_time").text = timestamp.isoformat()
    etree.SubElement(f, prefix + "file_size", unit="byte").text = str(size)
    etree.SubElement(f, prefix + "records").text = str(numentries)

    deeper = etree.Element(prefix + "Manifest_SIP_Deep_Archive")
    deepfilearea.append(deeper)
    etree.SubElement(deeper, prefix + "name").text = "Delivery Manifest Table"
    etree.SubElement(deeper, prefix + "local_identifier").text = "Table"
    etree.SubElement(deeper, prefix + "offset", unit="byte").text = "0"
    deeper.append(etree.Comment("Size the of the SIP manifest in bytes"))
    etree.SubElement(deeper, prefix + "object_length", unit="byte").text = str(size)
    etree.SubElement(deeper, prefix + "parsing_standard_id").text = "PDS DSV 1"
    etree.SubElement(deeper, prefix + "description").text = _stdmanifestdescription
    deeper.append(etree.Comment("Number of rows in the manifest"))
    etree.SubElement(deeper, prefix + "records").text = str(numentries)
    etree.SubElement(deeper, prefix + "record_delimiter").text = "Carriage-Return Line-Feed"
    etree.SubElement(deeper, prefix + "field_delimiter").text = "Horizontal Tab"

    columns = etree.Element(prefix + "Record_Delimited")
    deeper.append(columns)
    etree.SubElement(columns, prefix + "fields").text = "4"
    etree.SubElement(columns, prefix + "groups").text = "0"
    for colnum, (name, desc) in enumerate(_recordboilerplate, 1):
        column = etree.Element(prefix + "Field_Delimited")
        columns.append(column)
        etree.SubElement(column, prefix + "name").text = name
        etree.SubElement(column, prefix + "field_number").text = str(colnum)
        etree.SubElement(column, prefix + "data_type").text = "ASCII_String"
        etree.SubElement(column, prefix + "description").text = desc

    deep.append(etree.Comment("Include reference to the Bundle being described"))
    internal = etree.Element(prefix + "Internal_Reference")
    deep.append(internal)
    internal.append(
        etree.Comment("The LIDVID from the bundle label (combination of logical_identifier and version_id)")
    )
    etree.SubElement(internal, prefix + "lidvid_reference").text = logicalid + "::" + versionid
    etree.SubElement(internal, prefix + "reference_type").text = "package_has_bundle"
    etree.SubElement(internal, prefix + "comment").text = _intrefboilerplate

    sipdeep = etree.Element(prefix + "SIP_Deep_Archive")
    root.append(sipdeep)
    etree.SubElement(sipdeep, prefix + "description").text = "Submission Information Package for the" + title
    sipdeep.append(etree.Comment("Provider Site ID input by user"))
    etree.SubElement(sipdeep, prefix + "provider_site_id").text = site

    # Add the xml-model PI, write out the tree
    model = etree.ProcessingInstruction("xml-model", XML_MODEL_PI)
    root.addprevious(model)
    tree = etree.ElementTree(root)
    tree.write(labeloutputfile, encoding="utf-8", xml_declaration=True, pretty_print=True)


def addsiparguments(parser):
    """Add submission information package argument handling to the given argument ``parser``."""
    # TODO: Temporarily commenting out this argument until an input manifest is available
    # parser.add_argument(
    #     '-a', '--algorithm', default='MD5', choices=sorted(HASH_ALGORITHMS.keys()),
    #     help='File hash (checksum) algorithm; default %(default)s'
    # )
    parser.add_argument(
        "-s", "--site", required=True, choices=PROVIDER_SITE_IDS, help="Provider site ID for the manifest's label"
    )

    # TODO: Temporarily setting to be required by default until online mode is available
    parser.add_argument(
        "-b",
        "--bundle-base-url",
        required=True,
        help="Base URL for Node data archive. This URL will be prepended to"
        " the bundle directory to form URLs to the products. For example,"
        " if we are generating a SIP for mission_bundle/LADEE_Bundle_1101.xml,"
        " and bundle-base-url is https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/,"
        " the URL in the SIP will be https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/mission_bundle/LADEE_Bundle_1101.xml.",
    )

    # https://github.com/NASA-PDS/pds-deep-archive/issues/102
    parser.add_argument(
        "-D",
        "--disable-url-validation",
        required=False,
        action="store_true",
        help="SIP generation will check if URLs generated from the ``bundle-base-url`` are valid"
        " by attempting to retrieve the first such URL and failing (early) if it cannot; this"
        " flag disables such validation.",
    )


def _populate(lid, vid, lidvidstofiles, allcollections, con):
    """Populate the LIDVIDs-to-files.

    Populate the ``lidvidstofiles`` dict (which maps ``lid::vid`` → set of ``file:`` URLs) with
    data from ``con`` by recursively looking for file referenced by the label ``lid``::``vid``,
    following bundle member entires to other XML labels. When those references are full lidvid
    references, it's easy. But when they're just logical ID references, then we take just the
    latest version ID except if ``allcollections`` is True, then we take *all* version IDs.
    """
    _logger.debug("📥 Organizing files by %s::%s", lid, vid)
    lidvid = f"{lid}::{vid}"
    cursor = con.cursor()
    cursor.execute("SELECT filepath FROM label_file_references WHERE lid = ? AND vid = ?", ((lid, vid)))
    matchingfiles = set(["file:" + i[0] for i in cursor.fetchall()])
    filessofar = lidvidstofiles.get(lidvid, set())
    filessofar |= matchingfiles
    lidvidstofiles[lidvid] = filessofar
    _logger.debug("⧟ Following inter-label references from %s::%s with allcollections=%r", lid, vid, allcollections)
    cursor.execute("SELECT to_lid, to_vid FROM inter_label_references WHERE lid = ? AND vid = ?", ((lid, vid)))
    for to_lid, to_vid in cursor.fetchall():
        # lid-only reference: capture ``allcollections`` or just the latest
        if to_vid is None:
            if allcollections:
                cursor.execute("SELECT vid FROM labels WHERE lid = ?", (to_lid,))
                for to_vid in [i[0] for i in cursor.fetchall()]:
                    _populate(to_lid, to_vid, lidvidstofiles, allcollections, con)
            else:
                # Note that ``max(vid)`` isn't sufficient since it's text and therefore 2.0 > 10.0; however
                # to do this right we'd have to make (major, minor) ver cols out of version IDs or provide a
                # sqlite3 C extension with a custom collator. Close 'nuff for gov't work 😁
                cursor.execute("SELECT max(vid) FROM labels WHERE lid = ?", (to_lid,))
                to_vid = cursor.fetchone()[0]
                _populate(to_lid, to_vid, lidvidstofiles, allcollections, con)
        else:
            # It's a specific lid+vid
            _populate(to_lid, to_vid, lidvidstofiles, allcollections, con)


def _gettitle(tree):
    """Get the title.

    Get the title of the XML label in the given ``tree`` by following from the root of
    the tree to the Identification Area and thence the title, returning a sentinel string
    if it's not found.
    """
    root = tree.getroot()
    matches = root.findall(f"./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}title")
    if matches:
        return matches[0].text.strip()
    else:
        _logger.warning("❓ Bundle missing <title>")
        return "«unknown»"


def produce(
    bundle, hashname, registryserviceurl, insecureconnectionflag, site, baseurl, aipfile, allcollections, con, timestamp
):
    """Produce the submission information package.

    Produce the submission information package for the given ``bundle``, using the message digest
    algorithm identified by ``hashname``. Label this for the given ``site`` and prefix items in the
    submission information package with the given ``baseurl`` and referencing the optional
    ``aipfile``.  For XML labels that have just a lid reference to other labels, include just the
    latest version of such referenced labels unless ``allcollections`` is True.  Return the names
    of the manifest file and the label file generated. ``con`` is a sqlite3 database connection
    we can use as lookup and storage. The ``timestamp`` is used for the creation date in the
    label for the SIP and also in filenames or the label and SIP.
    """
    _logger.info("🏃‍♀️ Starting SIP generation for %s", bundle.name)

    tree = parsexml(bundle)
    lid, vid = getlogicalversionidentifier(tree)
    title = _gettitle(tree)
    strippedlogicalid = lid.split(":")[-1] + "_v" + vid
    filename = strippedlogicalid + "_" + timestamp.date().strftime("%Y%m%d") + "_sip_v" + AIP_SIP_DEFAULT_VERSION
    manifestfilename = filename + PDS_TABLE_FILENAME_EXTENSION
    labelfilename = filename + PDS_LABEL_FILENAME_EXTENSION
    bundle = os.path.abspath(bundle.name)
    lidvidstofiles = {}

    _populate(lid, vid, lidvidstofiles, allcollections, con)
    hashedfiles = _getdigests(lidvidstofiles, hashname)
    with open(manifestfilename, "wb") as manifest:
        md5, size = _writetable(hashedfiles, hashname, manifest, baseurl, os.path.dirname(os.path.dirname(bundle)))
        with open(labelfilename, "wb") as label:
            writelabel(
                lid,
                vid,
                title,
                md5,
                size,
                len(hashedfiles),
                hashname,
                manifestfilename,
                site,
                label,
                aipfile,
                timestamp,
            )
    _logger.info("🎉 Success! From %s, generated these output files:", bundle)
    _logger.info("📄 SIP Manifest: %s", manifestfilename)
    _logger.info("📄 XML label for the SIP: %s", labelfilename)
    return manifestfilename, labelfilename


def main():
    """Check the command-line for options and create a SIP from the given bundle XML."""
    parser = argparse.ArgumentParser(description=_description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    addbundlearguments(parser)
    addsiparguments(parser)
    addloggingarguments(parser)
    parser.add_argument(
        "bundle",
        type=argparse.FileType("rb"),
        metavar="INPUT-BUNDLE.XML",
        help="Bundle XML file to read from local filesystem.",
    )
    parser.add_argument(
        "-c",
        "--aip",
        type=argparse.FileType("rb"),
        metavar="AIP-CHECKSUM-MANIFEST.TAB",
        help="Archive Information Product checksum manifest file",
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, format="%(levelname)s %(message)s")
    _logger.debug("⚙️ command line args = %r", args)

    # https://github.com/NASA-PDS/pds-deep-archive/issues/102
    if not args.disable_url_validation:
        provideUtility(URLValidator())

    tempdir = tempfile.mkdtemp(suffix=".dir", prefix="sip")
    try:
        # Survey the surgical field
        dbfile = os.path.join(tempdir, "pds-deep-archive.sqlite3")
        con = sqlite3.connect(dbfile)
        _logger.debug("⚙️ Creating potentially future-mulitprocessing–capable DB in %s", dbfile)
        with con:
            createschema(con)
            comprehenddirectory(os.path.dirname(os.path.abspath(args.bundle.name)), con)

        # Make a timestamp but drop the microsecond resolution
        ts = datetime.utcnow()
        ts = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, microsecond=0, tzinfo=None)

        # Let's get the show on the road
        manifest, label = produce(
            bundle=args.bundle,
            # TODO: Temporarily hardcoding these values until other modes are available
            # hashname=HASH_ALGORITHMS[args.algorithm],
            # registryserviceurl=args.url,
            # insecureconnectionflag=args.insecure,
            hashname=HASH_ALGORITHMS["MD5"],
            registryserviceurl=None,
            insecureconnectionflag=False,
            site=args.site,
            baseurl=args.bundle_base_url,
            aipfile=args.aip,
            allcollections=not args.include_latest_collection_only,
            con=con,
            timestamp=ts,
        )
    except Exception as ex:
        _logger.critical("🛑 Cannot proceed as a critical problem has occurred; re-run with --debug for more info.")
        _logger.debug("🖥 Here is the exception: %r", ex, exc_info=ex)
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)
    _logger.info("👋 All done for now.")
    sys.exit(0)


if __name__ == "__main__":
    main()
