# encoding: utf-8
#
# Copyright © 2019–2020 California Institute of Technology ("Caltech").
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

'''Submission Information Package'''


from .constants import (
    INFORMATION_MODEL_VERSION, PDS_NS_URI, XML_SCHEMA_INSTANCE_NS_URI, XML_MODEL_PI,
    PDS_SCHEMA_URL, AIP_PRODUCT_URI_PREFIX, PDS_LABEL_FILENAME_EXTENSION
)
from .utils import getPrimariesAndOtherInfo, getMD5, getLogicalIdentifierAndFileInventory
from datetime import datetime
from lxml import etree
from urllib.parse import urlparse
import argparse, logging, hashlib, pysolr, urllib.request, os.path, re, sys


# Defaults & Constants
# --------------------

# Program related info:
_version = '0.0.0'
_description = '''Generate Submission Information Packages (SIPs) from bundles.
This program takes a bundle XML file as input and produces two output files:

① A Submission Information Package (SIP) manifest file; and
② A PDS XML label of that file.

The files are created in the current working directory when this program is
run. The names of the files are based on the logical identifier found in the
bundle file, and any existing files are overwritten. The names of the
generated files are printed upon successful completion.
'''

# Other constants and defaults:
_registryServiceURL = 'https://pds-dev-el7.jpl.nasa.gov/services/registry/pds'  # Default registry service
_bufsiz             = 512                                                       # Buffer size for reading from URL con
_pLineMatcher       = re.compile(r'^P,\s*(.+)')                                 # Match P-lines in a tab file

# TODO: Auto-generate from PDS4 IM
_providerSiteIDs = ['PDS_' + i for i in ('ATM', 'ENG', 'GEO', 'IMG', 'JPL', 'NAI', 'PPI', 'PSI', 'RNG', 'SBN')]

# URI prefix for logical identifiers of Submission Information Package bundles
_sipDeepURIPrefix = 'urn:nasa:pds:system_bundle:product_sip_deep_archive:'

# Boilerplate
_stdManifestDescription = 'Tab-separated manifest table for delivering one bundle to the Deep Archive'

# Record boilerplate; first is column name, second is its description (all records are ASCII_String in PDS parlance)
_recordBoilerplate = (
    ('checksum', 'Checksum Value'),
    ('checksum_type', 'Checksum Type'),
    ('file_specification_url', 'URL to file associated with checksum in field #1 and product lidvid in field #3'),
    ('LIDVID', 'Unique product lidvid that contains this file')
)

# Internal reference boilerplate
_intRefBoilerplate = 'Links this SIP to the specific version of the bundle product in the PDS registry system'

# Command-line names for various hash algorithms, mapped to Python implementation name—OK,
# not really! The Python implementation names are lowercase, but thankfully ``hashlib`` doesn't
# care. (Still not sure why these were up-cased.)
_algorithms = {
    'MD5':     'MD5',
    'SHA-1':   'SHA1',
    'SHA-256': 'SHA256',
}


# Logging
# -------
_logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(message)s', level=logging.WARNING)


# Functions
# ---------

def _getFileInfo(primaries, registryServiceURL, insecureConnectionFlag):
    '''For the ``primaries``, contact the ``registryServiceURL`` (and verifiying  the connection based on
    the negative state of the ``insecureConnectionFlag``) and find the lidvid and set of matching files
    for that lidvid, returning a mapping of the same (lidvid to set of file URLs).
    '''
    _logger.debug('Connecting to Solr at %s, verify=%s', registryServiceURL, not insecureConnectionFlag)
    lidvidsToFiles = {}
    solr = pysolr.Solr(registryServiceURL, verify=not insecureConnectionFlag)
    for primary in primaries:
        # XXX for testing, try: query = 'lid:*'
        query = f'lid:"{primary}"'
        results = solr.search(query)
        _logger.debug('For solr query «%s», got %d results', query, len(results))
        for result in results:
            lidvid = result.get('lidvid')
            if not lidvid:
                _logger.info('The ``lidvid`` is missing for a resulting match for «%s»', primary)
                continue
            files = lidvidsToFiles.get(lidvid, set())
            # XXX for testing, try: files |= set(['https://mars.jpl.nasa.gov/robots.txt'])
            files |= set(result.get('file_ref_url', []))
            lidvidsToFiles[lidvid] = files
    _logger.debug('Returning %d matching lidvids', len(lidvidsToFiles))
    return lidvidsToFiles


def _getPLines(tabFilePath):
    '''In the file named by ``tabFile``, get all tokens after any line that starts with ``P,``,
    iggnoring any space after the comma. Also strip any thing after ``::`` at the end of the line.
    '''
    lidvids = set()
    with open(tabFilePath, 'r') as tabFile:
        for line in tabFile:
            match = _pLineMatcher.match(line)
            if not match: continue

            # All values in collection manifest table must be a lidvid, if not throw an error
            if '::' not in match.group(1):
                msg = ('Invalid collection manifest. All records must contain '
                       'lidvids but found "' + match.group(1))
                raise Exception(msg)

            lidvids.add(match.group(1))

    return lidvids


def _findLidVidsInXMLFiles(lidvid, xmlFiles):
    '''Look in each of the ``xmlFiles`` for an XPath from root to ``Identification_Area`` to
    ``logical_identifier`` and ``version_id`` and see if they form a matching ``lidvid``.
    If it does, add that XML file to a set as a ``file:`` style URL and return the set.
    '''
    matchingFiles = set()
    for xmlFile in xmlFiles:
        _logger.debug('Parsing XML in %s', xmlFile)
        tree = etree.parse(xmlFile)
        root = tree.getroot()
        matches = root.findall(f'./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}logical_identifier')
        if not matches: continue
        lid = matches[0].text.strip()

        matches = root.findall(f'./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}version_id')
        if not matches: continue
        vid = matches[0].text.strip()

        if lidvid.strip() == lid + '::' + vid:
            matchingFiles.add('file:' + xmlFile)
            matchingFiles |= _getAssociatedProducts(tree, os.path.dirname(xmlFile))
            break

    return matchingFiles


def _getAssociatedProducts(root, filepath):
    '''Parse the XML for all the files associated with it that make up the product'''
    products = set()
    matches = root.findall(f'//{{{PDS_NS_URI}}}File/{{{PDS_NS_URI}}}file_name')
    matches.extend(root.findall(f'//{{{PDS_NS_URI}}}Document_File/{{{PDS_NS_URI}}}file_name'))
    if not matches: return products
    for m in matches:
        products.add('file:' + os.path.join(filepath, m.text))

    return products


def _getLocalFileInfo(bundle, primaries, bundleLidvid):
    '''Search all XML files (except for the ``bundle`` file) in the same directory as ``bundle``
    and look for all XPath ``Product_Collection/Identification_Area/logical_identifier`` values
    that match any of the primary names in ``primaries``. If we get a match, note all XPath
    ``File_Area_Inventory/File/file_name`` entries for later inclusion.

    What does later inclusion mean? We open each of those files (usually ending in ``.tab`` or
    ``.TAB``) and look for any lines with ``P,\\s*`` at the front: the next token is a magical
    "lidvid". We then have to find in the directory tree where ``bundle`` is all files that
    have that "lidvid" and return then a mapping of lidvids to set of matching files, as ``file:``
    URLs.
    '''
    # First get a set of all XML files under the same directory as ``bundle``

    # I'll take a six-pack of tabs
    lidvids = set()

    # Match up lidsvids with xmlFiles
    lidvidsToFiles = {}

    # Add bundle to manifest
    lidvidsToFiles[bundleLidvid] = {'file:' + bundle}

    root = os.path.dirname(bundle)
    xmlFiles = set()

    for dirpath, dirnames, filenames in os.walk(root):
        xmlFiles |= set([os.path.join(dirpath, i) for i in filenames if i.endswith(PDS_LABEL_FILENAME_EXTENSION) or i.endswith(PDS_LABEL_FILENAME_EXTENSION.upper())])

    for xmlFile in xmlFiles:
        # Need to check for lid or lidvid depending on what is specified in the bundle
        lid, lidvid, tabs = getLogicalIdentifierAndFileInventory(xmlFile)
        if not lid or not tabs: continue
        if lid in primaries or lidvid in primaries:
            # This will probably always be the case working with an offline directory tree
            lidvidsToFiles[lidvid] = {'file:' + xmlFile}
            for tab in tabs:
                lidvids |= _getPLines(tab)
                lidvidsToFiles[lidvid].add('file:' + tab)

    for lidvid in lidvids:
        # Look in all XML files for the lidvids
        products = _findLidVidsInXMLFiles(lidvid, xmlFiles)
        matching = lidvidsToFiles.get(lidvid, set())
        matching |= products
        lidvidsToFiles[lidvid] = matching

    return lidvidsToFiles


def _getDigests(lidvidsToFiles, hashName):
    '''``lidvidsToFiles`` is a mapping of lidvid (string) to a set of matching file URLs.
    Using a digest algorithm identified by ``hashName``, retrieve each URL's content and cmpute
    its digest. Return a sequence of triples of (url, digest (hex string), and lidvid)
    '''
    withDigests = []
    # TODO: potential optimization is that if the same file appears for multiple lidvids we retrieve it
    # multiple times; we could cache previous hash computations
    for lidvid, files in lidvidsToFiles.items():
        for url in files:
            try:
                hashish = hashlib.new(hashName)
                _logger.debug('Getting «%s» for hashing with %s', url, hashName)
                with urllib.request.urlopen(url) as i:
                    while True:
                        buf = i.read(_bufsiz)
                        if len(buf) == 0: break
                        hashish.update(buf)
                # FIXME: some hash algorithms take variable length digests; we should filter those out
                withDigests.append((url, hashish.hexdigest(), lidvid))
            except urllib.error.URLError as error:
                _logger.info('Problem retrieving «%s» for digest: %r; ignoring', url, error)
    return withDigests


def _writeTable(hashedFiles, hashName, manifest, offline, baseURL, basePathToReplace):
    '''For each file in ``hashedFiles`` (a triple of file URL, digest, and lidvid), write a tab
    separated sequence of lines onto ``manifest`` with the columns containing the digest,
    the name of the hasing algorithm that produced the digest, the URL to the file, and the
    lidvid. Return a hex conversion of the MD5 digest of the manifest plus the total bytes
    written.

    If ``offline`` mode, we transform all URLs written to the table by stripping off
    everything except the last component (the file) and prepending the given ``baseURL``.
    '''
    hashish, size = hashlib.new('md5'), 0
    for url, digest, lidvid in sorted(hashedFiles):
        if offline:
            if baseURL.endswith('/'):
                baseURL = baseURL[:-1]

            url = baseURL + urlparse(url).path.replace(basePathToReplace, '')

        entry = f'{digest}\t{hashName}\t{url}\t{lidvid.strip()}\r\n'.encode('utf-8')
        hashish.update(entry)
        manifest.write(entry)
        size += len(entry)
    return hashish.hexdigest(), size


def _writeLabel(logicalID, versionID, title, digest, size, numEntries, hashName, manifestFile, site, labelOutputFile, aipFile):
    '''Write an XML label to the file ``labelOutputFile``. Note that ``digest`` is a hex version
    of the *MD5* digest of the generated manifest, but ``hashName`` is the name of the hash algorithm
    used to produce the *contents* of the manifest, which may be MD5 or something else.

    The ``aipFile`` is a read-stream to the Archive Infomration Package (AIP) which we use
    to write an MD5 hash into this label. If it's not given, we default to writing an
    MD5 of zeros.
    '''

    # Get the current time, but drop the microsecond resolution
    ts = datetime.utcnow()
    ts = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, microsecond=0, tzinfo=None)

    # Set up convenient prefixes for XML namespaces
    nsmap = {
        None: PDS_NS_URI,
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    prefix = f'{{{PDS_NS_URI}}}'

    # Root of the XML document: Product_SIP_Deep_Archive
    root = etree.Element(
        prefix + 'Product_SIP_Deep_Archive',
        attrib={f'{{{XML_SCHEMA_INSTANCE_NS_URI}}}' + 'schemaLocation': PDS_SCHEMA_URL},
        nsmap=nsmap
    )

    identificationArea = etree.Element(prefix + 'Identification_Area')
    root.append(identificationArea)
    logicalIdentifier = _sipDeepURIPrefix + logicalID.split(':')[-1] + ':' + versionID
    etree.SubElement(identificationArea, prefix + 'logical_identifier').text = logicalIdentifier
    etree.SubElement(identificationArea, prefix + 'version_id').text = '1.0'
    etree.SubElement(identificationArea, prefix + 'title').text = 'Submission Information Package for the ' + title
    etree.SubElement(identificationArea, prefix + 'information_model_version').text = INFORMATION_MODEL_VERSION
    etree.SubElement(identificationArea, prefix + 'product_class').text = 'Product_SIP_Deep_Archive'

    modificationHistory = etree.Element(prefix + 'Modification_History')
    identificationArea.append(modificationHistory)
    modificationDetail = etree.Element(prefix + 'Modification_Detail')
    modificationHistory.append(modificationDetail)
    etree.SubElement(modificationDetail, prefix + 'modification_date').text = ts.date().isoformat()
    etree.SubElement(modificationDetail, prefix + 'version_id').text = '1.0'
    etree.SubElement(modificationDetail, prefix + 'description').text = 'SIP was verisoned and created'

    deep = etree.Element(prefix + 'Information_Package_Component_Deep_Archive')
    root.append(deep)
    deep.append(etree.Comment('MD5 digest checksum for the manifest file'))
    etree.SubElement(deep, prefix + 'manifest_checksum').text = digest
    etree.SubElement(deep, prefix + 'checksum_type').text = 'MD5'
    etree.SubElement(deep, prefix + 'manifest_url').text = 'file:' + os.path.abspath(manifestFile)
    etree.SubElement(deep, prefix + 'aip_lidvid').text = AIP_PRODUCT_URI_PREFIX + logicalID.split(':')[-1]

    aipMD5 = getMD5(aipFile) if aipFile else '00000000000000000000000000000000'
    etree.SubElement(deep, prefix + 'aip_label_checksum').text = aipMD5

    deepFileArea = etree.Element(prefix + 'File_Area_SIP_Deep_Archive')
    deep.append(deepFileArea)
    f = etree.Element(prefix + 'File')
    deepFileArea.append(f)
    etree.SubElement(f, prefix + 'file_name').text = os.path.basename(manifestFile)
    f.append(etree.Comment('Creation date time in formation YYYY-MM-DDTHH:mm:ss'))
    etree.SubElement(f, prefix + 'creation_date_time').text = ts.isoformat()
    etree.SubElement(f, prefix + 'file_size', unit='byte').text = str(size)
    etree.SubElement(f, prefix + 'records').text = str(numEntries)

    deeper = etree.Element(prefix + 'Manifest_SIP_Deep_Archive')
    deepFileArea.append(deeper)
    etree.SubElement(deeper, prefix + 'name').text = 'Delivery Manifest Table'
    etree.SubElement(deeper, prefix + 'local_identifier').text = 'Table'
    etree.SubElement(deeper, prefix + 'offset', unit='byte').text = '0'
    deeper.append(etree.Comment('Size the of the SIP manifest in bytes'))
    etree.SubElement(deeper, prefix + 'object_length', unit='byte').text = str(size)
    etree.SubElement(deeper, prefix + 'parsing_standard_id').text = 'PDS DSV 1'
    etree.SubElement(deeper, prefix + 'description').text = _stdManifestDescription
    deeper.append(etree.Comment('Number of rows in the manifest'))
    etree.SubElement(deeper, prefix + 'records').text = str(numEntries)
    etree.SubElement(deeper, prefix + 'record_delimiter').text = 'Carriage-Return Line-Feed'
    etree.SubElement(deeper, prefix + 'field_delimiter').text = 'Horizontal Tab'

    columns = etree.Element(prefix + 'Record_Delimited')
    deeper.append(columns)
    etree.SubElement(columns, prefix + 'fields').text = '4'
    etree.SubElement(columns, prefix + 'groups').text = '0'
    for colNum, (name, desc) in enumerate(_recordBoilerplate, 1):
        column = etree.Element(prefix + 'Field_Delimited')
        columns.append(column)
        etree.SubElement(column, prefix + 'name').text = name
        etree.SubElement(column, prefix + 'field_number').text = str(colNum)
        etree.SubElement(column, prefix + 'data_type').text = 'ASCII_String'
        etree.SubElement(column, prefix + 'description').text = desc

    deep.append(etree.Comment('Include reference to the Bundle being described'))
    internal = etree.Element(prefix + 'Internal_Reference')
    deep.append(internal)
    internal.append(etree.Comment('The LIDVID from the bundle label (combination of logical_identifier and version_id)'))
    etree.SubElement(internal, prefix + 'lidvid_reference').text = logicalID + '::' + versionID
    etree.SubElement(internal, prefix + 'reference_type').text = 'package_has_bundle'
    etree.SubElement(internal, prefix + 'comment').text = _intRefBoilerplate

    sipDeep = etree.Element(prefix + 'SIP_Deep_Archive')
    root.append(sipDeep)
    etree.SubElement(sipDeep, prefix + 'description').text = 'Submission Information Package for the' + title
    sipDeep.append(etree.Comment('Provider Site ID input by user'))
    etree.SubElement(sipDeep, prefix + 'provider_site_id').text = site

    # Add the xml-model PI, write out the tree
    model = etree.ProcessingInstruction('xml-model', XML_MODEL_PI)
    root.addprevious(model)
    tree = etree.ElementTree(root)
    tree.write(labelOutputFile, encoding='utf-8', xml_declaration=True, pretty_print=True)


def _produce(bundle, hashName, registryServiceURL, insecureConnectionFlag, site, offline, baseURL, aipFile):
    '''Produce a SIP from the given bundle'''
    # Get the bundle path
    bundle = os.path.abspath(bundle.name)

    # Get the bundle's primary collections and other useful info
    primaries, bundleLID, title, bundleVID = getPrimariesAndOtherInfo(bundle)
    strippedLogicalID = bundleLID.split(':')[-1]

    filename = strippedLogicalID + '_sip_v' + bundleVID
    manifestFileName, labelFileName = filename + '.tab', filename + PDS_LABEL_FILENAME_EXTENSION
    if offline:
        lidvidsToFiles = _getLocalFileInfo(bundle, primaries, bundleLID + '::' + bundleVID)
    else:
        _logger.warning('The remote functionality with registry in the loop is still in development.')
        lidvidsToFiles = _getFileInfo(primaries, registryServiceURL, insecureConnectionFlag)

    hashedFiles = _getDigests(lidvidsToFiles, hashName)
    with open(manifestFileName, 'wb') as manifest:
        md5, size = _writeTable(hashedFiles, hashName, manifest, offline, baseURL, os.path.dirname(os.path.dirname(bundle)))
        with open(labelFileName, 'wb') as label:
            _writeLabel(bundleLID, bundleVID, title, md5, size, len(hashedFiles), hashName, manifestFileName, site, label, aipFile)
    return manifestFileName, labelFileName


def main():
    '''Check the command-line for options and create a SIP from the given bundle XML'''
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument(
        'bundle', type=argparse.FileType('rb'), metavar='IN-BUNDLE.XML', help='Bundle XML file to read'
    )
    parser.add_argument(
        '-a', '--algorithm', default='MD5', choices=sorted(_algorithms.keys()),
        help='File hash (checksum) algorithm; default %(default)s'
    )
    parser.add_argument(
        '-s', '--site', required=True, choices=_providerSiteIDs,
        help="Provider site ID for the manifest's label; default %(default)s"
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        '-u', '--url', default=_registryServiceURL,
        help='URL to the registry service; default %(default)s'
    )
    group.add_argument(
        '-n', '--offline', default=False, action='store_true',
        help='Run offline, scanning bundle directory for matching files instead of querying registry service'
    )
    parser.add_argument(
        '-k', '--insecure', default=False, action='store_true',
        help='Ignore SSL/TLS security issues; default %(default)s'
    )
    parser.add_argument(
        '-c', '--aip', type=argparse.FileType('rb'), metavar='AIP-CHECKSUM-MANIFEST.TAB',
        help='Archive Information Product checksum manifest file'
    )
    parser.add_argument(
        '-b', '--bundle-base-url', required=False, default='file:/',
        help='Base URL prepended to URLs in the generated manifest for local files in "offline" mode'
    )
    parser.add_argument(
        '-v', '--verbose', default=False, action='store_true',
        help='Verbose logging; defaults %(default)s'
    )
    # TODO: ``pds4_information_model_version`` is parsed into the arg namespace but is otherwise ignored
    parser.add_argument(
        '-i', '--pds4-information-model-version', default=INFORMATION_MODEL_VERSION,
        help='Specify PDS4 Information Model version to generate SIP. Must be 1.13.0.0+; default %(default)s'
    )
    args = parser.parse_args()
    if args.verbose:
        _logger.setLevel(logging.DEBUG)
    _logger.debug('command line args = %r', args)
    manifest, label = _produce(
        args.bundle,
        _algorithms[args.algorithm],
        args.url,
        args.insecure,
        args.site,
        args.offline,
        args.bundle_base_url,
        args.aip
    )
    print(f'⚙︎ ``sipgen`` — Submission Information Package (SIP) Generator, version {_version}', file=sys.stderr)
    print(f'🎉 Success! From {args.bundle.name}, generated these output files:', file=sys.stderr)
    print(f'• Manifest: {manifest}', file=sys.stderr)
    print(f'• Label: {label}', file=sys.stderr)
    sys.exit(0)


if __name__ == '__main__':
    main()
