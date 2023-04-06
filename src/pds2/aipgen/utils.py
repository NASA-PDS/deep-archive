# encoding: utf-8
#
# Copyright © 2020–2021 California Institute of Technology ("Caltech").
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
"""Utilities."""
import functools
import hashlib
import logging
import os.path
import re
import sqlite3
import urllib

from lxml import etree
from zope.interface import implementer

from .constants import PDS_NS_URI
from .constants import PRODUCT_COLLECTION_TAG
from .interfaces import IURLValidator


# Logging
# -------
_logger = logging.getLogger(__name__)


# Private Constants
# -----------------

_bufsiz = 512  # Byte buffer
_xmlcachesize = 2 ** 16  # XML files to cache in memory
_digestcachesize = 2 ** 16  # Message digests to cache in memory
_plinematcher = re.compile(r"^[Pp],\s*([^\s]+)::([^\s]+)")  # Match separate lids and vids in "P/p" lines in .tab files

# Help message for ``--include-latest-collection-only``:
_allcollectionshelp = """For bundles that reference collections by LID, this flag will only include the latest version of
collections in the bundle. By default, the software includes all versions of all collections located within the bundle
root directory.
"""


# Functions
# ---------


def createschema(con):
    """Make the database schema for handing AIPs and SIPs in the given ``con``nection."""
    cursor = con.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS labels (
        lid text NOT NULL,
        vid text NOT NULL
    )"""
    )
    cursor.execute("CREATE UNIQUE INDEX lidvidIndex ON labels (lid, vid)")
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS inter_label_references (
        lid text NOT NULL,
        vid text NOT NULL,
        to_lid text NOT NULL,
        to_vid text
    )"""
    )
    cursor.execute("CREATE UNIQUE INDEX lidvidlidMapping ON inter_label_references (lid, vid, to_lid, to_vid)")
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS label_file_references (
        lid text NOT NULL,
        vid text NOT NULL,
        filepath text NOT NULL
    )"""
    )
    cursor.execute("CREATE UNIQUE INDEX lidvidfileIndex on label_file_references (lid, vid, filepath)")


def getlogicalversionidentifier(tree):
    """Get a LID.

    In the XML document ``tree``, return the logical identifier and the version identifier as
    strings, or ``None, None`` if they're not found.
    """
    lid = vid = None
    root = tree.getroot()
    matches = root.findall(f"./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}logical_identifier")
    if matches:
        lid = matches[0].text.strip()
        matches = root.findall(f"./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}version_id")
        if matches:
            vid = matches[0].text.strip()
    return lid, vid


def _addinterlabelreferencesfromtabfile(lid, vid, tabfile, con):
    """Add inter-label references.

    Open the PDS tab file ``tabfile`` and find all "P lines" in it, adding them as destination
    references from the given logical version identifier ``lid`` and version identifier ``vid``
    to the ``inter_label_references`` table in the database ``con``nection.
    """
    with open(tabfile, "r") as f:
        for line in f:
            match = _plinematcher.match(line)
            if not match:
                continue
            try:
                con.execute(
                    "INSERT INTO inter_label_references (lid, vid, to_lid, to_vid) VALUES (?,?,?,?)",
                    (lid, vid, match.group(1), match.group(2)),
                )
            except sqlite3.IntegrityError:
                pass


def comprehenddirectory(dn, con):
    """Fathom a directory.

    In and under the given directory ``dn`` ,look for XML files and their various references to other
    files, populating tables in ``con``.
    """
    for dirpath, _dirnames, filenames in os.walk(dn):
        for fn in filenames:
            if fn.lower().endswith(".xml"):
                xmlfile = os.path.join(dirpath, fn)
                _logger.debug("📄 Deconstructing %s", xmlfile)
                tree = parsexml(xmlfile)
                if tree is None:
                    continue
                isproductcollection = tree.getroot().tag == PRODUCT_COLLECTION_TAG
                lid, vid = getlogicalversionidentifier(tree)
                if lid and vid:
                    # OK, got an XML file we can work with
                    con.execute("INSERT OR IGNORE INTO labels (lid, vid) VALUES (?, ?)", (lid, vid))
                    con.execute(
                        "INSERT OR IGNORE INTO label_file_references (lid, vid, filepath) VALUES (?,?,?)",
                        (lid, vid, xmlfile.replace("\\", "/")),
                    )

                    # Now see if it refers to other XML files
                    matches = tree.getroot().findall(f"./{{{PDS_NS_URI}}}Bundle_Member_Entry")
                    for match in matches:
                        # Do "primary" references only (https://github.com/NASA-PDS/pds-deep-archive/issues/92)
                        lidref = vidref = ordinality = None
                        for child in match:
                            if child.tag == f"{{{PDS_NS_URI}}}lid_reference":
                                lidref = child.text.strip()
                            elif child.tag == f"{{{PDS_NS_URI}}}lidvid_reference":
                                lidref, vidref = child.text.strip().split("::")
                            elif child.tag == f"{{{PDS_NS_URI}}}member_status":
                                ordinality = child.text.strip()
                        if ordinality is None:
                            raise ValueError(
                                f"Bundle {xmlfile} contains a <Bundle_Member_Entry> with no <member_status>"
                            )
                        if lidref and ordinality == "Primary":
                            if vidref:
                                con.execute(
                                    "INSERT OR IGNORE INTO inter_label_references (lid, vid, to_lid, to_vid) VALUES (?,?,?,?)",
                                    (lid, vid, lidref, vidref),
                                )
                            else:
                                con.execute(
                                    "INSERT OR IGNORE INTO inter_label_references (lid, vid, to_lid) VALUES (?,?,?)",
                                    (lid, vid, lidref),
                                )

                    # And see if it refers to other files
                    matches = tree.getroot().findall(f".//{{{PDS_NS_URI}}}file_name")
                    for match in matches:
                        # Reject relative paths (#145)
                        if ".." in match.text:
                            message = (
                                f'Bundle {xmlfile} contains a <file_name> ``{match.text}`` which contains a'
                                ' relative path ``..``, which is invalid'
                            )
                            raise ValueError(message)
                        # any sibling directory_path_name?
                        dpnnode = match.getparent().find(f"./{{{PDS_NS_URI}}}directory_path_name")
                        fn = match.text.strip()
                        dn = None if dpnnode is None else dpnnode.text.strip()
                        filepath = os.path.join(dirpath, dn, fn) if dn else os.path.join(dirpath, fn)
                        if os.path.isfile(filepath):
                            con.execute(
                                "INSERT OR IGNORE INTO label_file_references (lid, vid, filepath) VALUES (?,?,?)",
                                (lid, vid, filepath.replace("\\", "/")),
                            )
                            # Weird (to a certain degree of weird) case: <file_name> may refer to a file
                            # that contains even more inter_label_references, but only if this label is
                            # product collections.
                            if isproductcollection:
                                _addinterlabelreferencesfromtabfile(lid, vid, filepath, con)
                        else:
                            _logger.warning("⚠️ File %s referenced by %s does not exist; ignoring", fn, xmlfile)


@functools.lru_cache(maxsize=_xmlcachesize)
def parsexml(f):
    """Parse the XML in object ``f``."""
    try:
        return etree.parse(f)
    except etree.XMLSyntaxError:
        _logger.warning("👀 Cannot parse XML document at «%s»; ignoring it", f)
        return None


@functools.lru_cache(maxsize=_digestcachesize)
def getdigest(url, hashname):
    """Compute a digest of the object at url and return it as a hex string."""
    hashish = hashlib.new(hashname)
    _logger.debug("Getting «%s» for hashing with %s", url, hashname)
    with urllib.request.urlopen(url) as i:
        while True:
            buf = i.read(_bufsiz)
            if len(buf) == 0:
                break
            hashish.update(buf)
    return hashish.hexdigest()  # XXX We do not support hashes with varialbe-length digests


def getmd5(i):
    """Compute an MD5 digest of the input stream ``i`` and return it as a hex string."""
    md5 = hashlib.new("md5")
    while True:
        buf = i.read(_bufsiz)
        if len(buf) == 0:
            break
        md5.update(buf)
    return md5.hexdigest()


def addloggingarguments(parser):
    """Add command-line arguments to the given argument ``parser`` to support logging."""
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d",
        "--debug",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
        help="Log debugging messages for developers",
    )
    group.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        dest="loglevel",
        const=logging.WARNING,
        help="Don't log informational messages",
    )


def addbundlearguments(parser):
    """Bundle handling command-line arguments.

    Add command-line parsing to the given argument ``parser`` to support handling of bundles
    with ambiguous ``lid_reference`` without specific versions (#24).
    """
    parser.add_argument("--include-latest-collection-only", action="store_true", help=_allcollectionshelp)


# Classes
# -------

# https://github.com/NASA-PDS/pds-deep-archive/issues/102
@implementer(IURLValidator)
class URLValidator(object):
    """This serves to check the first URL generated by this system and abort early on failure.

    It's usually installed as a singleton utility (using zope.component).
    """

    _checked = False

    def validate(self, url):
        """See the interface being implemented."""
        if self._checked:
            return
        try:
            # Normally I'd make a ``urllib.request.Request`` with the method set to HEAD to both
            # test if the URL is well-formed (handled by Request construtor) and if the resource
            # exists (handled by the HEAD transaction). But this won't work with ``file:`` URLs
            # that don't even support the notion of a HEAD request. So, instead we see if we can
            # read 1 byte. Any other error we let propagate.
            with urllib.request.urlopen(url) as response:
                data = response.read(1)
                assert len(data) == 1
        except (ValueError, urllib.error.URLError) as ex:
            _logger.info("💥 I encountered an error while attempting to validate a URL!")
            _logger.info("🗺 The URL that did't work: «%s»", url)
            if getattr(ex, "reason", None) is not None:
                _logger.info("📖 The reason it didn't work is: «%s»", ex.reason)
            _logger.info(
                "💁‍♀️ This probably means that the bundle base URL is incorrect. You might want to check that!"
            )
            _logger.info("🤓 If you'd like the full stack trace, re-run with the ``--debug`` option.")
            raise
        finally:
            self._checked = True
