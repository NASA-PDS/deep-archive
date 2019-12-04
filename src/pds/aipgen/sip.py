# encoding: utf-8

'''Submission Information Package'''


from xml.etree import ElementTree
import argparse, sys, logging, hashlib, pysolr, urllib.request


# Defaults & Constants
# --------------------
#

_registryServiceURL = 'https://pds-dev-el7.jpl.nasa.gov/services/registry/pds'  # Default registry service
_bufsiz = 512  # Buffer size for reading from URL connections


# logging
# -------
_logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s %(message)s', level=logging.WARNING)


# Functions
# ---------

def _getPrimaries(bundle):
    '''Get the "primaries" from the given bundle XML.'''
    _logger.debug('Parsing XML in %r', bundle)
    primaries = []
    tree = ElementTree.parse(bundle)
    root = tree.getroot()
    members = root.findall('.//{http://pds.nasa.gov/pds4/pds/v1}Bundle_Member_Entry')
    for member in members:
        lid = kind = None
        for elem in member:
            if elem.tag == '{http://pds.nasa.gov/pds4/pds/v1}lid_reference':
                lid = elem.text.strip()
            elif elem.tag == '{http://pds.nasa.gov/pds4/pds/v1}member_status':
                kind = elem.text.strip().lower()
        if kind == 'primary' and lid:
            primaries.append(lid)
    _logger.debug('XML parse done, got %d primaries', len(primaries))
    return primaries


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
    lidvid
    '''
    for url, digest, lidvid in hashedFiles:
        manifest.write(f'{digest}\t{hashName}\t{url}\t{lidvid}\n')


def _produce(bundle, hashName, registryServiceURL, insecureConnectionFlag, manifest):
    '''Produce a SIP from the given bundle'''
    primaries = _getPrimaries(bundle)
    lidvidsToFiles = _getFileInfo(primaries, registryServiceURL, insecureConnectionFlag)
    hashedFiles = _getDigests(lidvidsToFiles, hashName)
    _writeTable(hashedFiles, hashName, manifest)


def main():
    '''Check the command-line for options and create a SIP from the given bundle XML'''
    parser = argparse.ArgumentParser(description='Generate Submission Information Packages (SIPs) from bundles')
    parser.add_argument(
        'bundle', nargs='?', type=argparse.FileType('r'), default=sys.stdin, metavar='BUNDLE.XML',
        help='Bundle XML file to read; defaults to stdin if none given'
    )
    parser.add_argument(
        'manifest', nargs='?', type=argparse.FileType('w'), default=sys.stdout, metavar='MANIFEST.TAB',
        help='Tab separated manifest file to generate; defaults to stdout'
    )
    parser.add_argument(
        '-a', '--algorithm', default='md5', choices=sorted(list(hashlib.algorithms_available)),
        help='File hash (checksum, but not really); default %(default)s'
    )
    parser.add_argument(
        '-u', '--url', default=_registryServiceURL,
        help='URL to the registry service; default %(default)s'
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
    _produce(args.bundle, args.algorithm, args.url, args.insecure, args.manifest)


if __name__ == '__main__':
    main()
