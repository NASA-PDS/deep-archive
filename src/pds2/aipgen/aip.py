# encoding: utf-8
#
# Copyright © 2020 California Institute of Technology ("Caltech").
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
"""Archive Information Package."""
import argparse
import hashlib
import logging
import os.path
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime

from lxml import etree

from . import VERSION
from .constants import AIP_SIP_DEFAULT_VERSION
from .constants import INFORMATION_MODEL_VERSION
from .constants import PDS_LABEL_FILENAME_EXTENSION
from .constants import PDS_NS_URI
from .constants import PDS_SCHEMA_URL
from .constants import PDS_TABLE_FILENAME_EXTENSION
from .constants import XML_MODEL_PI
from .constants import XML_SCHEMA_INSTANCE_NS_URI
from .utils import addbundlearguments
from .utils import addloggingarguments
from .utils import comprehenddirectory
from .utils import createschema
from .utils import getlogicalversionidentifier
from .utils import getmd5
from .utils import parsexml


# Constants
# ---------

# Module metadata

__version__ = VERSION

# For ``--help``; note this is hand-wrapped at 80 columns:
_description = """Generate an Archive Information Package or AIP. An AIP consists of three
files:
➀ a "checksum manifest" which contains MD5 hashes of *all* files in a
  product;
➁ a "transfer manifest" which lists the "lidvids" for files within each
  XML label mentioned in a product; and
➂ an XML label for these two files.
You can use the checksum manifest file ➀ as input to ``sipgen`` in order
to create a Submission Information Package."""

# Prefix to use for logical IDs for labels for AIPs
_aipproductprefix = "urn:nasa:pds:system_bundle:product_aip:"

# Comment to insert near the top of an AIP XML label
_iacomment = (
    "Parse name from bundle logical_identifier, e.g. urn:nasa:pds:ladee_mission_bundle would be ladee_mission_bundle"
)

# Logging:
_logger = logging.getLogger(__name__)


# Functions
# ---------


def writelabel(
    labeloutputfile,
    logicalidfragment,
    bundlelid,
    bundlevid,
    chksumfn,
    chksummd5,
    chksumsize,
    chksumnum,
    xferfn,
    xfermd5,
    xfersize,
    xfernum,
    timestamp,
):
    """Create an XML label in ``labeloutputfile`` which will be overwritten.

    It will use the following information:

    • ``logicalidfragment`` — the last colon-separated component of the "lidvid"
    • ``bundlelid``— the full "lid" without the vid
    • ``bundlevid`` — the "vid" without the lid
    • ``chksumfn`` — the name of the AIP checksum file we generated
    • ``chksummd5`` — MD5 hash of the AIP checksum file
    • ``chksumsize`` — size in bytes of the AIP checksum file
    • ``chksumnum`` — count of records in the AIP checksum file
    • ``xferfn`` — the name of the AIP transfer manifest file we generated
    • ``xfermd5`` — the MD5 hash of the transfer manifest file
    • ``xfersize`` — size in bytes of the transfer manifest file
    • ``xfernum`` — count of records in the transfer manifest file
    • ``timestamp`` — what to use for creation date + modification date, in the label
    """
    _logger.debug("🏷  Writing AIP label to %s", labeloutputfile)

    # Contrive the logical identifer of the label
    labellid = _aipproductprefix + logicalidfragment.split(":")[-1] + "_" + timestamp.date().strftime("%Y%m%d")

    # Set up convenient prefixes for XML namespaces
    nsmap = {None: PDS_NS_URI, "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    prefix = f"{{{PDS_NS_URI}}}"

    # Root of the XML document: Product_AIP
    root = etree.Element(
        prefix + "Product_AIP",
        attrib={f"{{{XML_SCHEMA_INSTANCE_NS_URI}}}" + "schemaLocation": PDS_SCHEMA_URL},
        nsmap=nsmap,
    )

    identificationarea = etree.Element(prefix + "Identification_Area")
    root.append(identificationarea)
    identificationarea.append(etree.Comment(_iacomment))
    etree.SubElement(identificationarea, prefix + "logical_identifier").text = labellid
    etree.SubElement(identificationarea, prefix + "version_id").text = AIP_SIP_DEFAULT_VERSION
    identificationarea.append(etree.Comment("Use the title from the bundle label"))
    title = "Archive Information Package for " + logicalidfragment + "::" + bundlevid
    etree.SubElement(identificationarea, prefix + "title").text = title
    etree.SubElement(identificationarea, prefix + "information_model_version").text = INFORMATION_MODEL_VERSION
    etree.SubElement(identificationarea, prefix + "product_class").text = "Product_AIP"

    modificationhistory = etree.Element(prefix + "Modification_History")
    identificationarea.append(modificationhistory)
    modificationdetail = etree.Element(prefix + "Modification_Detail")
    modificationhistory.append(modificationdetail)
    modificationdetail.append(etree.Comment("Creation date in format YYYY-MM-DD"))
    etree.SubElement(modificationdetail, prefix + "modification_date").text = timestamp.date().isoformat()
    etree.SubElement(modificationdetail, prefix + "version_id").text = AIP_SIP_DEFAULT_VERSION
    etree.SubElement(
        modificationdetail, prefix + "description"
    ).text = "Archive Information Package was versioned and created"

    ipc = etree.Element(prefix + "Information_Package_Component")
    root.append(ipc)
    etree.SubElement(ipc, prefix + "checksum_manifest_checksum").text = chksummd5
    etree.SubElement(ipc, prefix + "checksum_type").text = "MD5"
    etree.SubElement(ipc, prefix + "transfer_manifest_checksum").text = xfermd5
    ipc.append(etree.Comment("Include reference to the Bundle being described"))
    internalref = etree.Element(prefix + "Internal_Reference")
    ipc.append(internalref)
    internalref.append(
        etree.Comment("The LIDVID from the bundle label (combination of logical_identifier and version_id)")
    )
    etree.SubElement(internalref, prefix + "lidvid_reference").text = bundlelid + "::" + bundlevid
    etree.SubElement(internalref, prefix + "reference_type").text = "package_has_bundle"
    etree.SubElement(
        internalref, prefix + "comment"
    ).text = "Links this AIP to the specific version of the bundle product in the PDS registry system"

    chksum = etree.Element(prefix + "File_Area_Checksum_Manifest")
    ipc.append(chksum)
    f = etree.Element(prefix + "File")
    chksum.append(f)
    etree.SubElement(f, prefix + "file_name").text = chksumfn
    f.append(etree.Comment("Creation date time in formation YYYY-MM-DDTHH:mm:ss"))
    etree.SubElement(f, prefix + "creation_date_time").text = timestamp.isoformat()
    etree.SubElement(f, prefix + "file_size", unit="byte").text = str(chksumsize)
    etree.SubElement(f, prefix + "records").text = str(chksumnum)
    cm = etree.Element(prefix + "Checksum_Manifest")
    chksum.append(cm)
    etree.SubElement(cm, prefix + "name").text = "checksum manifest"
    etree.SubElement(cm, prefix + "offset", unit="byte").text = "0"
    etree.SubElement(cm, prefix + "object_length", unit="byte").text = str(chksumsize)
    etree.SubElement(cm, prefix + "parsing_standard_id").text = "MD5Deep 4.n"
    etree.SubElement(cm, prefix + "record_delimiter").text = "Carriage-Return Line-Feed"

    manifest = etree.Element(prefix + "File_Area_Transfer_Manifest")
    ipc.append(manifest)
    f = etree.Element(prefix + "File")
    manifest.append(f)
    etree.SubElement(f, prefix + "file_name").text = xferfn
    etree.SubElement(f, prefix + "creation_date_time").text = timestamp.isoformat()
    etree.SubElement(f, prefix + "file_size", unit="byte").text = str(xfersize)
    etree.SubElement(f, prefix + "records").text = str(xfernum)  # Do it once here
    tm = etree.Element(prefix + "Transfer_Manifest")
    manifest.append(tm)
    etree.SubElement(tm, prefix + "name").text = "transfer manifest"
    etree.SubElement(tm, prefix + "offset", unit="byte").text = "0"
    etree.SubElement(tm, prefix + "records").text = str(xfernum)  # And again here! 🤷‍♀️
    etree.SubElement(tm, prefix + "record_delimiter").text = "Carriage-Return Line-Feed"
    rc = etree.Element(prefix + "Record_Character")
    tm.append(rc)
    etree.SubElement(rc, prefix + "fields").text = "2"
    etree.SubElement(rc, prefix + "groups").text = "0"
    etree.SubElement(rc, prefix + "record_length", unit="byte").text = "512"
    fc = etree.Element(prefix + "Field_Character")
    rc.append(fc)
    etree.SubElement(fc, prefix + "name").text = "LIDVID"
    etree.SubElement(fc, prefix + "field_location", unit="byte").text = "1"
    etree.SubElement(fc, prefix + "data_type").text = "ASCII_String"
    etree.SubElement(fc, prefix + "field_length", unit="byte").text = "255"
    fc = etree.Element(prefix + "Field_Character")
    rc.append(fc)
    etree.SubElement(fc, prefix + "name").text = "File Specification Name"
    etree.SubElement(fc, prefix + "field_location", unit="byte").text = "256"
    etree.SubElement(fc, prefix + "data_type").text = "ASCII_File_Specification_Name"
    etree.SubElement(fc, prefix + "field_length", unit="byte").text = "255"

    aip = etree.Element(prefix + "Archival_Information_Package")
    root.append(aip)
    descr = "Archival Information Package for " + bundlelid + "::" + bundlevid
    etree.SubElement(aip, prefix + "description").text = descr

    # Add the xml-model PI, write out the tree
    model = etree.ProcessingInstruction("xml-model", XML_MODEL_PI)
    root.addprevious(model)
    tree = etree.ElementTree(root)
    tree.write(labeloutputfile, encoding="utf-8", xml_declaration=True, pretty_print=True)


def _getfiles(con, lid, vid, allcollections):
    """Get the files.

    Get the files specified in the database at ``con`` referenced by the label ``lid``::``vid``.
    Recursively find files specified by the labels references as bundle member entries in the label
    for ``lid``::``vid``. Note that some references might be by ``lid`` only; when this is the case,
    we choose only the latest version found in ``con`` except if ``allcollections`` is True, then
    we put in *every* referenced version.

    Returns a sequence of triples (lid, vid, filepath) where filepath is the full path of a
    referenced file.
    """
    _logger.debug("🕵️‍♀️ Finding files for %s::%s", lid, vid)
    cursor = con.cursor()
    cursor.execute("SELECT filepath FROM label_file_references WHERE lid = ? AND vid = ?", ((lid, vid)))
    files = set([(lid, vid, i[0]) for i in cursor.fetchall()])

    _logger.debug("🕵️‍♂️ Finding inter-label references from %s::%s with allcollections=%r", lid, vid, allcollections)
    cursor.execute("SELECT to_lid, to_vid FROM inter_label_references WHERE lid = ? AND vid = ?", ((lid, vid)))
    for to_lid, to_vid in cursor.fetchall():
        # For a lid-only reference, we can include all of the potential vids or just the latest
        if to_vid is None:
            # lid-only, so what's it gonna be, all or latest 🤷‍♀️
            if allcollections:
                cursor.execute("SELECT vid FROM labels WHERE lid = ?", (to_lid,))
                for to_vid in [i[0] for i in cursor.fetchall()]:
                    files |= _getfiles(con, to_lid, to_vid, allcollections)
            else:
                # Note that ``max(vid)`` doesn't cut it since it would make 2.0 > 10.0; however  to fix this
                # we'd either have to make (major, minor) columns out of version IDs or provide a sqlite3 C
                # extension with a version collator. But this is close enough for now. 🧐
                cursor.execute("SELECT max(vid) FROM labels WHERE lid = ?", (to_lid,))
                to_vid = cursor.fetchone()[0]
                files |= _getfiles(con, to_lid, to_vid, allcollections)
        else:
            # full lid-vid reference
            files |= _getfiles(con, to_lid, to_vid, allcollections)
    return files


def _writechecksummanifest(chksumfn, lid, vid, con, prefixlen, allcollections):
    """Write the checksum manifest.

    Write the checksum manifest for the label ``lid``::``vid`` found in database ``con`` to the
    file ``chksumfn``, stripping the prefixes of local filenames up to ``prefixlen`` characters,
    and optionally including ``allcollections`` for labels that reference bundle member entries
    by lid-only if True, otherwise the latest version only if False.
    """
    _logger.debug("🧾 Writing checksum manifest for %s::%s to %s", lid, vid, chksumfn)
    md5, size, count = hashlib.new("md5"), 0, 0
    files = _getfiles(con, lid, vid, allcollections)
    with open(chksumfn, "wb") as o:
        # The tuples are (lid, vid, filepath)—we care just about filepath
        for f in [i[2] for i in files]:
            with open(f, "rb") as i:
                digest = getmd5(i)
                strippedfn = f[prefixlen:]
                entry = f"{digest}\t{strippedfn}\r\n".encode("utf-8")
                o.write(entry)
                md5.update(entry)
                size += len(entry)
                count += 1
                if count % 100 == 0:
                    _logger.debug("⏲ Wrote %d entries into the checksum manifest", count)
    return md5.hexdigest(), size, count, files


def _writetransfermanifest(xferfn, prefixlen, files):
    """Write the transfer manifest.

    Write the transfer manifest to the file ``xferfn`` for the given ``files``, stripping the prefix
    of local file paths up to ``prefixlen`` characters away.  ``files`` is a sequence of triples of
    (lid, vid, filepath).
    """
    _logger.debug("🚢 Writing transfer manifest to %s", xferfn)
    md5, size, count = hashlib.new("md5"), 0, 0

    # First, organize by lid::vids → sequences of files
    lidvidstofiles = {}
    for lid, vid, f in files:
        lidvid, transformedfn = f"{lid}::{vid}", "/" + f[prefixlen:]
        perlidvid = lidvidstofiles.get(lidvid, [])
        perlidvid.append(transformedfn)
        lidvidstofiles[lidvid] = perlidvid

    # Now write those organized into groups of lidvids
    with open(xferfn, "wb") as o:
        for lidvid, filenames in lidvidstofiles.items():
            for fn in filenames:
                entry = f"{lidvid:255}{fn:255}\r\n".encode("utf-8")
                o.write(entry)
                md5.update(entry)
                size += len(entry)
                count += 1
                if count % 100 == 0:
                    _logger.debug("⌚️ Wrote %d entries into the transfer manifest", count)
    return md5.hexdigest(), size, count


def process(bundle, allcollections, con, timestamp):
    """Process towards an AIP.

    Generate a "checksum manifest", a "transfer manifest", and a PDS label from the given
    ``bundle``, which is an open file stream (with a ``name`` atribute) on the local
    filesystem. Return the name of the generated checksum manifest file. ``con`` is a sqlite3
    database connection containing information about the bundle. The ``timestamp`` tells us
    what to put into the label for thie AIP files about creation date and also to create
    filenames of our generated files.
    """
    _logger.info("🏃‍♀️ Starting AIP generation for %s", bundle.name)

    prefixlen = len(os.path.dirname(os.path.abspath(bundle.name))) + 1
    lid, vid = getlogicalversionidentifier(parsexml(bundle))
    strippedlogicalid, slate = lid.split(":")[-1] + "_v" + vid, timestamp.date().strftime("%Y%m%d")

    # Easy one: the checksum† manifest
    # †It's actually an MD5 *hash*, not a checksum 😅
    chksumfn = (
        strippedlogicalid
        + "_"
        + slate
        + "_checksum_manifest_v"
        + AIP_SIP_DEFAULT_VERSION
        + PDS_TABLE_FILENAME_EXTENSION
    )
    chksummd5, chksumsize, chksumnum, files = _writechecksummanifest(chksumfn, lid, vid, con, prefixlen, allcollections)

    # Next: the transfer manifest
    xferfn = (
        strippedlogicalid
        + "_"
        + slate
        + "_transfer_manifest_v"
        + AIP_SIP_DEFAULT_VERSION
        + PDS_TABLE_FILENAME_EXTENSION
    )
    xfermd5, xfersize, xfernum = _writetransfermanifest(xferfn, prefixlen, files)

    # Finally, the XML label
    labelfn = strippedlogicalid + "_" + slate + "_aip_v" + AIP_SIP_DEFAULT_VERSION + PDS_LABEL_FILENAME_EXTENSION
    writelabel(
        labelfn,
        strippedlogicalid,
        lid,
        vid,
        chksumfn,
        chksummd5,
        chksumsize,
        chksumnum,
        xferfn,
        xfermd5,
        xfersize,
        xfernum,
        timestamp,
    )
    _logger.info("🎉 Success! AIP done, files generated:")
    _logger.info("📄 Checksum manifest: %s", chksumfn)
    _logger.info("📄 Transfer manifest: %s", xferfn)
    _logger.info("📄 XML label for them both: %s", labelfn)
    return chksumfn, xferfn, labelfn


def main():
    """Check the command-line for options and create an AIP from the given bundle XML."""
    parser = argparse.ArgumentParser(description=_description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    addloggingarguments(parser)
    addbundlearguments(parser)
    parser.add_argument(
        "bundle", type=argparse.FileType("rb"), metavar="IN-BUNDLE.XML", help="Root bundle XML file to read"
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, format="%(levelname)s %(message)s")
    _logger.debug("⚙️ command line args = %r", args)
    tempdir = tempfile.mkdtemp(suffix=".dir", prefix="aip")
    try:
        # Scout the enemy line
        dbfile = os.path.join(tempdir, "pds-deep-archive.sqlite3")
        con = sqlite3.connect(dbfile)
        _logger.debug("⚙️ Creating potentially future-mulitprocessing–capable DB in %s", dbfile)
        with con:
            createschema(con)
            comprehenddirectory(os.path.dirname(os.path.abspath(args.bundle.name)), con)

        # Make a timestamp but drop the microsecond resolution
        ts = datetime.utcnow()
        ts = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, microsecond=0, tzinfo=None)

        # Here we go, daddy
        process(args.bundle, not args.include_latest_collection_only, con, ts)
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)

    _logger.info("👋 Thanks for using this program! Bye!")
    sys.exit(0)


if __name__ == "__main__":
    main()
