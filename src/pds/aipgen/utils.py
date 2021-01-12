# encoding: utf-8
#
# Copyright © 2020 California Institute of Technology ("Caltech").
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

'''Utilities'''

from .constants import PDS_NS_URI, PRODUCT_COLLECTION_TAG
from lxml import etree
import logging, hashlib, os.path, functools, urllib, re


# Logging
# -------
_logger = logging.getLogger(__name__)


# Private Constants
# -----------------

_bufsiz = 512                                            # Byte buffer
_xmlCacheSize = 2**16                                    # XML files to cache in memory
_digestCacheSize = 2**16                                 # Message digests to cache in memory
_pLineMatcher = re.compile(r'^P,\s*([^\s]+)::([^\s]+)')  # Match separate lids and vids in "P" lines in ``.tab`` files

# Help message for ``--include-latest-collection-only``:
_allCollectionsHelp = '''For bundles that reference collections by LID, this flag will only include the latest version of
collections in the bundle. By default, the software includes all versions of all collections located within the bundle 
root directory.
'''


# Functions
# ---------


def createSchema(con):
    '''Make the database schema for handing AIPs and SIPs in the given ``con``nection
    '''
    cursor = con.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS labels (
        lid text NOT NULL,
        vid text NOT NULL
    )''')
    cursor.execute('CREATE UNIQUE INDEX lidvidIndex ON labels (lid, vid)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inter_label_references (
        lid text NOT NULL,
        vid text NOT NULL,
        to_lid text NOT NULL,
        to_vid text
    )''')
    cursor.execute('CREATE UNIQUE INDEX lidvidlidMapping ON inter_label_references (lid, vid, to_lid, to_vid)')
    cursor.execute('''CREATE TABLE IF NOT EXISTS label_file_references (
        lid text NOT NULL,
        vid text NOT NULL,
        filepath text NOT NULL
    )''')
    cursor.execute('CREATE UNIQUE INDEX lidvidfileIndex on label_file_references (lid, vid, filepath)')


def getLogicalVersionIdentifier(tree):
    '''In the XML document ``tree``, return the logical identifier and the version identifier as
    strings, or ``None, None`` if they're not found.
    '''
    lid = vid = None
    root = tree.getroot()
    matches = root.findall(f'./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}logical_identifier')
    if matches:
        lid = matches[0].text.strip()
        matches = root.findall(f'./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}version_id')
        if matches:
            vid = matches[0].text.strip()
    return lid, vid


def _addInterLabelReferencesFromTabFile(lid, vid, tabFile, con):
    '''Open the PDS tab file ``tabFile`` and find all "P lines" in it, adding them as destination
    references from the given logical version identifier ``lid`` and version identifier ``vid``
    to the ``inter_label_references`` table in the database ``con``nection.
    '''
    with open(tabFile, 'r') as f:
        for line in f:
            match = _pLineMatcher.match(line)
            if not match: continue
            con.execute(
                'INSERT INTO inter_label_references (lid, vid, to_lid, to_vid) VALUES (?,?,?,?)',
                (lid, vid, match.group(1), match.group(2))
            )


def comprehendDirectory(dn, con):
    '''In and under the given directory ``dn`` ,look for XML files and their various references to other
    files, populating tables in ``con``'''
    for dirpath, dirnames, filenames in os.walk(dn):
        for fn in filenames:
            if fn.lower().endswith('.xml'):
                xmlFile = os.path.join(dirpath, fn)
                _logger.debug('📄 Deconstructing %s', xmlFile)
                tree = parseXML(xmlFile)
                if tree is None: continue
                isProductCollection = tree.getroot().tag == PRODUCT_COLLECTION_TAG
                lid, vid = getLogicalVersionIdentifier(tree)
                if lid and vid:
                    # OK, got an XML file we can work with
                    con.execute('INSERT OR IGNORE INTO labels (lid, vid) VALUES (?, ?)', (lid, vid))
                    con.execute(
                        'INSERT OR IGNORE INTO label_file_references (lid, vid, filepath) VALUES (?,?,?)',
                        (lid, vid, xmlFile.replace('\\', '/'))
                    )

                    # Now see if it refers to other XML files
                    matches = tree.getroot().findall(f'./{{{PDS_NS_URI}}}Bundle_Member_Entry')
                    for match in matches:
                        # Do "primary" references only (https://github.com/NASA-PDS/pds-deep-archive/issues/92)
                        lidRef = vidRef = ordinality = None
                        for child in match:
                            if child.tag == f'{{{PDS_NS_URI}}}lid_reference':
                                lidRef = child.text.strip()
                            elif child.tag == f'{{{PDS_NS_URI}}}lidvid_reference':
                                lidRef, vidRef = child.text.strip().split('::')
                            elif child.tag == f'{{{PDS_NS_URI}}}member_status':
                                ordinality = child.text.strip()
                        if ordinality is None:
                            raise ValueError(f'Bundle {xmlFile} contains a <Bundle_Member_Entry> with no <member_status>')
                        if lidRef and ordinality == 'Primary':
                            if vidRef:
                                con.execute(
                                    'INSERT OR IGNORE INTO inter_label_references (lid, vid, to_lid, to_vid) VALUES (?,?,?,?)',
                                    (lid, vid, lidRef, vidRef)
                                )
                            else:
                                con.execute(
                                    'INSERT OR IGNORE INTO inter_label_references (lid, vid, to_lid) VALUES (?,?,?)',
                                    (lid, vid, lidRef)
                                )

                    # And see if it refers to other files
                    matches = tree.getroot().findall(f'.//{{{PDS_NS_URI}}}file_name')
                    for match in matches:
                        # any sibling directory_path_name?
                        dpnNode = match.getparent().find(f'./{{{PDS_NS_URI}}}directory_path_name')
                        fn = match.text.strip()
                        dn = None if dpnNode is None else dpnNode.text.strip()
                        filepath = os.path.join(dirpath, dn, fn) if dn else os.path.join(dirpath, fn)
                        if os.path.isfile(filepath):
                            con.execute(
                                'INSERT OR IGNORE INTO label_file_references (lid, vid, filepath) VALUES (?,?,?)',
                                (lid, vid, filepath.replace('\\', '/'))
                            )
                            # Weird (to a certain degree of weird) case: <file_name> may refer to a file
                            # that contains even more inter_label_references, but only if this label is
                            # product collections.
                            if isProductCollection:
                                _addInterLabelReferencesFromTabFile(lid, vid, filepath, con)
                        else:
                            _logger.warning('⚠️ File %s referenced by %s does not exist; ignoring', fn, xmlFile)


@functools.lru_cache(maxsize=_xmlCacheSize)
def parseXML(f):
    '''Parse the XML in object ``f``'''
    try:
        return etree.parse(f)
    except etree.XMLSyntaxError:
        _logger.warning('👀 Cannot parse XML document at «%s»; ignoring it', f)
        return None


@functools.lru_cache(maxsize=_digestCacheSize)
def getDigest(url, hashName):
    '''Compute a digest of the object at url and return it as a hex string'''
    hashish = hashlib.new(hashName)
    _logger.debug('Getting «%s» for hashing with %s', url, hashName)
    with urllib.request.urlopen(url) as i:
        while True:
            buf = i.read(_bufsiz)
            if len(buf) == 0: break
            hashish.update(buf)
    return hashish.hexdigest()  # XXX We do not support hashes with varialbe-length digests


def getMD5(i):
    '''Compute an MD5 digest of the input stream ``i`` and return it as a hex string'''
    md5 = hashlib.new('md5')
    while True:
        buf = i.read(_bufsiz)
        if len(buf) == 0: break
        md5.update(buf)
    return md5.hexdigest()


def addLoggingArguments(parser):
    '''Add command-line arguments to the given argument ``parser`` to support logging.'''
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO,
        help='Log debugging messages for developers'
    )
    group.add_argument(
        '-q', '--quiet', action='store_const', dest='loglevel', const=logging.WARNING,
        help="Don't log informational messages"
    )


def addBundleArguments(parser):
    '''Add command-line parsing to the given argument ``parser`` to support handling of bundles
    with ambiguous ``lid_reference`` without specific versions (#24)
    '''
    parser.add_argument('--include-latest-collection-only', action='store_false', default=True, help=_allCollectionsHelp)
