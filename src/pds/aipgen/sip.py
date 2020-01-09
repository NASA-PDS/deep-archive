# encoding: utf-8

'''Submission Information Package'''


from datetime import datetime
from lxml import etree
import argparse, logging, hashlib, pysolr, urllib.request, os.path, re


# Defaults & Constants
# --------------------

_providerSiteIds    = ['PDS_ATM', 'PDS_ENG', 'PDS_GEO', 'PDS_IMG', 'PDS_JPL', 'PDS_NAI', 'PDS_PPI', 'PDS_PSI', 'PDS_RNG', 'PDS_SBN'] # TODO: Auto-generate from PDS4 IM
_registryServiceURL = 'https://pds-dev-el7.jpl.nasa.gov/services/registry/pds'  # Default registry service
_bufsiz             = 512                                                       # Buffer size for reading from URL con
_pLineMatcher       = re.compile(r'^P,\s*(.+)')                                 # Match P-lines in a tab file
_pdsNS              = 'http://pds.nasa.gov/pds4/pds/v1'                         # Namespace URI for PDS XML
_xsiNS              = 'http://www.w3.org/2001/XMLSchema-instance'               # Namespace URI for XML Schema

# For the XML model processing instruction
_xmlModel = '''href="https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1D00.sch"
schematypens="http://purl.oclc.org/dsdl/schematron"'''
# Where to find the PDS schema
_schemaLocation = 'http://pds.nasa.gov/pds4/pds/v1 https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1D00.xsd'
# URI prefix for logical identifiers of Submission Information Package bundles
_sipDeepURIPrefix = 'urn:nasa:pds:system_bundle:product_sip_deep_archive:'
# URI prefix for logical identifiers of volume identifiers for products for Archive Information Packages
_aipProductURIPrefix = 'urn:nasa:pds:system_bundle:product_aip:'
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


# logging
# -------
_logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(message)s', level=logging.WARNING)


# Functions
# ---------

def _getPrimariesAndOtherInfo(bundle):
    '''Get the "primaries" from the given bundle XML plus the logical identifier,
    plus the title plus the version ID (this function does too much)'''
    _logger.debug('Parsing XML in %r', bundle)
    primaries = set()
    tree = etree.parse(bundle)
    root = tree.getroot()
    members = root.findall(f'.//{{{_pdsNS}}}Bundle_Member_Entry')
    for member in members:
        lid = kind = None
        for elem in member:
            if elem.tag == f'{{{_pdsNS}}}lid_reference':
                lid = elem.text.strip()
            elif elem.tag == f'{{{_pdsNS}}}member_status':
                kind = elem.text.strip().lower()
        if kind == 'primary' and lid:
            primaries.add(lid)
    _logger.debug('XML parse done, got %d primaries', len(primaries))
    matches = root.findall(f'./{{{_pdsNS}}}Identification_Area/{{{_pdsNS}}}logical_identifier')
    logicalID = matches[0].text.strip()
    matches = root.findall(f'./{{{_pdsNS}}}Identification_Area/{{{_pdsNS}}}title')
    title = matches[0].text.strip()
    matches = root.findall(f'./{{{_pdsNS}}}Identification_Area/{{{_pdsNS}}}version_id')
    versionID = matches[0].text.strip()
    return primaries, logicalID, title, versionID


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


def _getLogicalIdentifierAndFileInventory(xmlFile):
    '''In the named local ``xmlFile ``, return a pair of its logical identifier via the XPath
    expression ``Product_Collection/Identification_Area/logical_identifier`` and all ``file_name``
    in ``File`` in ``File_Area_Inventory`` entries. If there's no logical identifier, just return
    None and None
    '''
    _logger.debug('Parsing XML in %s', xmlFile)
    tree = etree.parse(xmlFile)
    root = tree.getroot()
    matches = root.findall(f'./{{{_pdsNS}}}Identification_Area/{{{_pdsNS}}}logical_identifier')
    if not matches: return None, None
    lid = matches[0].text.strip()
    if not lid: return None, None
    dirname = os.path.dirname(xmlFile)
    matches = root.findall(f'./{{{_pdsNS}}}File_Area_Inventory/{{{_pdsNS}}}File/{{{_pdsNS}}}file_name')
    return lid, [os.path.join(dirname, i.text.strip()) for i in matches]


def _getPLines(tabFilePath):
    '''In the file named by ``tabFile``, get all tokens after any line that starts with ``P,``,
    iggnoring any space after the comma. Also strip any thing after ``::`` at the end of the line.
    '''
    lidvids = set()
    with open(tabFilePath, 'r') as tabFile:
        for line in tabFile:
            match = _pLineMatcher.match(line)
            if not match: continue
            lidvids.add(match.group(1).split('::')[0])
    return lidvids


def _findLidVidsInXMLFiles(lidvid, xmlFiles):
    '''Look in each of the ``xmlFiles`` for an XPath from root to ``Identification_Area`` to
    ``logical_identifier`` and see if the text there matches the ``lidvid``.  If it does, add
    that XML file to a set as a ``file:`` style URL and return the set.
    '''
    matchingFiles = set()
    for xmlFile in xmlFiles:
        _logger.debug('Parsing XML in %s', xmlFile)
        tree = etree.parse(xmlFile)
        root = tree.getroot()
        matches = root.findall(f'./{{{_pdsNS}}}Identification_Area/{{{_pdsNS}}}logical_identifier')
        if not matches: continue
        if lidvid == matches[0].text.strip():
            matchingFiles.add('file:' + xmlFile)
    return matchingFiles


def _getLocalFileInfo(bundle, primaries):
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
    # First get a set of all XML fules under the same directory as ``bundle`` but not including ``bundle``.
    bundlePath = os.path.abspath(bundle.name)
    root = os.path.dirname(bundlePath)
    xmlFiles = set()
    root = os.path.dirname(os.path.abspath(bundle.name))
    for dirpath, dirnames, filenames in os.walk(root):
        xmlFiles |= set([os.path.join(dirpath, i) for i in filenames if i.endswith('.xml') or i.endswith('.XML')])
    xmlFiles.remove(bundlePath)

    # I'll take a six-pack of tabs
    lidvids = set()
    for xmlFile in xmlFiles:
        lid, tabs = _getLogicalIdentifierAndFileInventory(xmlFile)
        if not lid or not tabs: continue
        if lid in primaries:
            # This will probably always be the case working with an offline directory tree
            for tab in tabs:
                lidvids |= _getPLines(tab)

    # Match up lidsvids with xmlFiles
    lidvidsToFiles = {}
    for lidvid in lidvids:
        # We just look in the XML files; is that correct? Should we do "egrep -r" and match *any* file?
        files = _findLidVidsInXMLFiles(lidvid, xmlFiles)
        matching = lidvidsToFiles.get(lidvid, set())
        matching |= files
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


def _writeTable(hashedFiles, hashName, manifest):
    '''For each file in ``hashedFiles`` (a triple of file URL, digest, and lidvid), write a tab
    separated sequence of lines onto ``manifest`` with the columns containing the digest,
    the name of the hasing algorithm that produced the digest, the URL to the file, and the
    lidvid. Return a hex conversion of the MD5 digest of the manifest plus the total bytes
    written.
    '''
    hashish, size = hashlib.new('md5'), 0
    for url, digest, lidvid in sorted(hashedFiles):
        entry = f'{digest}\t{hashName}\t{url}\t{lidvid}\n'.encode('utf-8')
        hashish.update(entry)
        manifest.write(entry)
        size += len(entry)
    return hashish.hexdigest(), size


def _writeLabel(logicalID, versionID, title, digest, size, numEntries, hashName, manifestFile, site, labelOutputFile):
    '''Write an XML label to the file ``labelOutputFile``. Note that ``digest`` is a hex version
    of the *MD5* digest of the generated manifest, but ``hashName`` is the name of the hash algorithm
    used to produce the *contents* of the manifest, which may be MD5 or something else.
    '''

    # Get the current time, but drop the microsecond resolution
    ts = datetime.utcnow()
    ts = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, microsecond=0, tzinfo=None)

    # Set up convenient prefixes for XML namespaces
    nsmap = {
        None: _pdsNS,
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    prefix = f'{{{_pdsNS}}}'

    # Root of the XML document: Product_SIP_Deep_Archive
    root = etree.Element(
        prefix + 'Product_SIP_Deep_Archive',
        attrib={f'{{{_xsiNS}}}' + 'schemaLocation': _schemaLocation},
        nsmap=nsmap
    )

    identificationArea = etree.Element(prefix + 'Identification_Area')
    root.append(identificationArea)
    etree.SubElement(identificationArea, prefix + 'logical_identifier').text = _sipDeepURIPrefix + logicalID.split(':')[-1]
    etree.SubElement(identificationArea, prefix + 'version_id').text = '1.0'
    etree.SubElement(identificationArea, prefix + 'title').text = 'Submission Information Package for the ' + title
    etree.SubElement(identificationArea, prefix + 'information_model_version').text = '1.13.0.0'
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
    etree.SubElement(deep, prefix + 'aip_lidvid').text = _aipProductURIPrefix + logicalID.split(':')[-1]
    etree.SubElement(deep, prefix + 'aip_label_checksum').text = hashName

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
    model = etree.ProcessingInstruction('xml-model', _xmlModel)
    root.addprevious(model)
    tree = etree.ElementTree(root)
    tree.write(labelOutputFile, encoding='utf-8', xml_declaration=True, pretty_print=True)


def _produce(bundle, hashName, registryServiceURL, insecureConnectionFlag, manifest, label, site, offline):
    '''Produce a SIP from the given bundle'''
    primaries, logicalID, title, versionID = _getPrimariesAndOtherInfo(bundle)
    if offline:
        lidvidsToFiles = _getLocalFileInfo(bundle, primaries)
    else:
        lidvidsToFiles = _getFileInfo(primaries, registryServiceURL, insecureConnectionFlag)
    hashedFiles = _getDigests(lidvidsToFiles, hashName)
    md5, size = _writeTable(hashedFiles, hashName, manifest)
    _writeLabel(logicalID, versionID, title, md5, size, len(hashedFiles), hashName, manifest.name, site, label)


def main():
    '''Check the command-line for options and create a SIP from the given bundle XML'''
    parser = argparse.ArgumentParser(description='Generate Submission Information Packages (SIPs) from bundles')
    parser.add_argument(
        'bundle', type=argparse.FileType('rb'), metavar='IN-BUNDLE.XML',
        help='Bundle XML file to read; defaults to stdin if none given'
    )
    parser.add_argument(
        'manifest', type=argparse.FileType('wb'), metavar='OUT-MANIFEST.TAB',
        help='Tab separated manifest file to generate; defaults to stdout'
    )
    parser.add_argument(
        'label', type=argparse.FileType('wb'), metavar='OUT-LABEL.XML',
        help='XML label to create describing the generated manifest'
    )
    parser.add_argument(
        '-a', '--algorithm', default='md5', choices=sorted(list(hashlib.algorithms_available)),
        help='File hash (checksum, but not really); default %(default)s'
    )
    parser.add_argument(
        '-s', '--site', required=True, choices=_providerSiteIds,
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
        '-v', '--verbose', default=False, action='store_true',
        help='Verbose _logger; defaults %(default)s'
    )
    args = parser.parse_args()
    if args.verbose:
        _logger.setLevel(logging.DEBUG)
    _logger.debug('command line args = %r', args)
    _produce(args.bundle, args.algorithm, args.url, args.insecure, args.manifest, args.label, args.site, args.offline)


if __name__ == '__main__':
    main()
