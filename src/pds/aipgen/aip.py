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

'''Archive Information Package'''


from .constants import (
    INFORMATION_MODEL_VERSION, PDS_LABEL_FILENAME_EXTENSION, PDS_NS_URI, PDS_SCHEMA_URL, PDS_TABLE_FILENAME_EXTENSION,
    XML_MODEL_PI, XML_SCHEMA_INSTANCE_NS_URI, AIP_SIP_DEFAULT_VERSION
)
from .utils import (
    addBundleArguments, addLoggingArguments, comprehendDirectory, createSchema, getLogicalVersionIdentifier,
    getMD5, parseXML
)
from . import VERSION
from datetime import datetime
from lxml import etree
import argparse, logging, sys, os, os.path, hashlib, tempfile, sqlite3, shutil


# Constants
# ---------

# Module metadata

__version__ = VERSION

# For ``--help``; note this is hand-wrapped at 80 columns:
_description = '''Generate an Archive Information Package or AIP. An AIP consists of three
files:
➀ a "checksum manifest" which contains MD5 hashes of *all* files in a
  product;
➁ a "transfer manifest" which lists the "lidvids" for files within each
  XML label mentioned in a product; and
➂ an XML label for these two files.
You can use the checksum manifest file ➀ as input to ``sipgen`` in order
to create a Submission Information Package.'''

# Prefix to use for logical IDs for labels for AIPs
_aipProductPrefix = 'urn:nasa:pds:system_bundle:product_aip:'

# Comment to insert near the top of an AIP XML label
_iaComment = 'Parse name from bundle logical_identifier, e.g. urn:nasa:pds:ladee_mission_bundle would be ladee_mission_bundle'

# Logging:
_logger = logging.getLogger(__name__)


# Functions
# ---------

def _writeLabel(
    labelOutputFile,
    logicalIDfragment,
    bundleLID,
    bundleVID,
    chksumFN,
    chksumMD5,
    chksumSize,
    chksumNum,
    xferFN,
    xferMD5,
    xferSize,
    xferNum,
    timestamp
):
    '''Create an XML label in ``labelOutputFile`` which will be overwritten and using the following
    information:

    • ``logicalIDfragment`` — the last colon-separated component of the "lidvid"
    • ``bundleLID``— the full "lid" without the vid
    • ``bundleVID`` — the "vid" without the lid
    • ``chksumFN`` — the name of the AIP checksum file we generated
    • ``chksumMD5`` — MD5 hash of the AIP checksum file
    • ``chksumSize`` — size in bytes of the AIP checksum file
    • ``chksumNum`` — count of records in the AIP checksum file
    • ``xferFN`` — the name of the AIP transfer manifest file we generated
    • ``xferMD5`` — the MD5 hash of the transfer manifest file
    • ``xferSize`` — size in bytes of the transfer manifest file
    • ``xferNum`` — count of records in the transfer manifest file
    • ``timestamp`` — what to use for creation date + modification date, in the label
    '''

    _logger.debug('🏷  Writing AIP label to %s', labelOutputFile)

    # Contrive the logical identifer of the label
    labelLID = _aipProductPrefix + logicalIDfragment.split(':')[-1] + '_' + timestamp.date().strftime('%Y%m%d')

    # Set up convenient prefixes for XML namespaces
    nsmap = {
        None: PDS_NS_URI,
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    prefix = f'{{{PDS_NS_URI}}}'

    # Root of the XML document: Product_AIP
    root = etree.Element(
        prefix + 'Product_AIP',
        attrib={f'{{{XML_SCHEMA_INSTANCE_NS_URI}}}' + 'schemaLocation': PDS_SCHEMA_URL},
        nsmap=nsmap
    )

    identificationArea = etree.Element(prefix + 'Identification_Area')
    root.append(identificationArea)
    identificationArea.append(etree.Comment(_iaComment))
    etree.SubElement(identificationArea, prefix + 'logical_identifier').text = labelLID
    etree.SubElement(identificationArea, prefix + 'version_id').text = AIP_SIP_DEFAULT_VERSION
    identificationArea.append(etree.Comment('Use the title from the bundle label'))
    title = 'Archive Information Package for ' + logicalIDfragment + '::' + bundleVID
    etree.SubElement(identificationArea, prefix + 'title').text = title
    etree.SubElement(identificationArea, prefix + 'information_model_version').text = INFORMATION_MODEL_VERSION
    etree.SubElement(identificationArea, prefix + 'product_class').text = 'Product_AIP'

    modificationHistory = etree.Element(prefix + 'Modification_History')
    identificationArea.append(modificationHistory)
    modificationDetail = etree.Element(prefix + 'Modification_Detail')
    modificationHistory.append(modificationDetail)
    modificationDetail.append(etree.Comment('Creation date in format YYYY-MM-DD'))
    etree.SubElement(modificationDetail, prefix + 'modification_date').text = timestamp.date().isoformat()
    etree.SubElement(modificationDetail, prefix + 'version_id').text = AIP_SIP_DEFAULT_VERSION
    etree.SubElement(modificationDetail, prefix + 'description').text = 'Archive Information Package was versioned and created'

    ipc = etree.Element(prefix + 'Information_Package_Component')
    root.append(ipc)
    etree.SubElement(ipc, prefix + 'checksum_manifest_checksum').text = chksumMD5
    etree.SubElement(ipc, prefix + 'checksum_type').text = 'MD5'
    etree.SubElement(ipc, prefix + 'transfer_manifest_checksum').text = xferMD5
    ipc.append(etree.Comment('Include reference to the Bundle being described'))
    internalRef = etree.Element(prefix + 'Internal_Reference')
    ipc.append(internalRef)
    internalRef.append(etree.Comment('The LIDVID from the bundle label (combination of logical_identifier and version_id)'))
    etree.SubElement(internalRef, prefix + 'lidvid_reference').text = bundleLID + '::' + bundleVID
    etree.SubElement(internalRef, prefix + 'reference_type').text = 'package_has_bundle'
    etree.SubElement(internalRef, prefix + 'comment').text = 'Links this AIP to the specific version of the bundle product in the PDS registry system'

    chksum = etree.Element(prefix + 'File_Area_Checksum_Manifest')
    ipc.append(chksum)
    f = etree.Element(prefix + 'File')
    chksum.append(f)
    etree.SubElement(f, prefix + 'file_name').text = chksumFN
    f.append(etree.Comment('Creation date time in formation YYYY-MM-DDTHH:mm:ss'))
    etree.SubElement(f, prefix + 'creation_date_time').text = timestamp.isoformat()
    etree.SubElement(f, prefix + 'file_size', unit='byte').text = str(chksumSize)
    etree.SubElement(f, prefix + 'records').text = str(chksumNum)
    cm = etree.Element(prefix + 'Checksum_Manifest')
    chksum.append(cm)
    etree.SubElement(cm, prefix + 'name').text = 'checksum manifest'
    etree.SubElement(cm, prefix + 'offset', unit='byte').text = '0'
    etree.SubElement(cm, prefix + 'object_length', unit='byte').text = str(chksumSize)
    etree.SubElement(cm, prefix + 'parsing_standard_id').text = 'MD5Deep 4.n'
    etree.SubElement(cm, prefix + 'record_delimiter').text = 'Carriage-Return Line-Feed'

    manifest = etree.Element(prefix + 'File_Area_Transfer_Manifest')
    ipc.append(manifest)
    f = etree.Element(prefix + 'File')
    manifest.append(f)
    etree.SubElement(f, prefix + 'file_name').text = xferFN
    etree.SubElement(f, prefix + 'creation_date_time').text = timestamp.isoformat()
    etree.SubElement(f, prefix + 'file_size', unit='byte').text = str(xferSize)
    etree.SubElement(f, prefix + 'records').text = str(xferNum)  # Do it once here
    tm = etree.Element(prefix + 'Transfer_Manifest')
    manifest.append(tm)
    etree.SubElement(tm, prefix + 'name').text = 'transfer manifest'
    etree.SubElement(tm, prefix + 'offset', unit='byte').text = '0'
    etree.SubElement(tm, prefix + 'records').text = str(xferNum)  # And again here! 🤷‍♀️
    etree.SubElement(tm, prefix + 'record_delimiter').text = 'Carriage-Return Line-Feed'
    rc = etree.Element(prefix + 'Record_Character')
    tm.append(rc)
    etree.SubElement(rc, prefix + 'fields').text = '2'
    etree.SubElement(rc, prefix + 'groups').text = '0'
    etree.SubElement(rc, prefix + 'record_length', unit='byte').text = '512'
    fc = etree.Element(prefix + 'Field_Character')
    rc.append(fc)
    etree.SubElement(fc, prefix + 'name').text = 'LIDVID'
    etree.SubElement(fc, prefix + 'field_location', unit='byte').text = '1'
    etree.SubElement(fc, prefix + 'data_type').text = 'ASCII_String'
    etree.SubElement(fc, prefix + 'field_length', unit='byte').text = '255'
    fc = etree.Element(prefix + 'Field_Character')
    rc.append(fc)
    etree.SubElement(fc, prefix + 'name').text = 'File Specification Name'
    etree.SubElement(fc, prefix + 'field_location', unit='byte').text = '256'
    etree.SubElement(fc, prefix + 'data_type').text = 'ASCII_File_Specification_Name'
    etree.SubElement(fc, prefix + 'field_length', unit='byte').text = '255'

    aip = etree.Element(prefix + 'Archival_Information_Package')
    root.append(aip)
    descr = 'Archival Information Package for ' + bundleLID + '::' + bundleVID
    etree.SubElement(aip, prefix + 'description').text = descr

    # Add the xml-model PI, write out the tree
    model = etree.ProcessingInstruction('xml-model', XML_MODEL_PI)
    root.addprevious(model)
    tree = etree.ElementTree(root)
    tree.write(labelOutputFile, encoding='utf-8', xml_declaration=True, pretty_print=True)


def _getFiles(con, lid, vid, allCollections):
    '''Get the files specified in the database at ``con`` referenced by the label ``lid``::``vid``.
    Recursively find files specified by the labels references as bundle member entries in the label
    for ``lid``::``vid``. Note that some references might be by ``lid`` only; when this is the case,
    we choose only the latest version found in ``con`` except if ``allCollections`` is True, then
    we put in *every* referenced version.

    Returns a sequence of triples (lid, vid, filepath) where filepath is the full path of a
    referenced file.
    '''
    _logger.debug('🕵️‍♀️ Finding files for %s::%s', lid, vid)
    cursor = con.cursor()
    cursor.execute('SELECT filepath FROM label_file_references WHERE lid = ? AND vid = ?', ((lid, vid)))
    files = set([(lid, vid, i[0]) for i in cursor.fetchall()])

    _logger.debug('🕵️‍♂️ Finding inter-label references from %s::%s with allCollections=%r', lid, vid, allCollections)
    cursor.execute('SELECT to_lid, to_vid FROM inter_label_references WHERE lid = ? AND vid = ?', ((lid, vid)))
    for to_lid, to_vid in cursor.fetchall():
        # For a lid-only reference, we can include all of the potential vids or just the latest
        if to_vid is None:
            # lid-only, so what's it gonna be, all or latest 🤷‍♀️
            if allCollections:
                cursor.execute('SELECT vid FROM labels WHERE lid = ?', (to_lid,))
                for to_vid in [i[0] for i in cursor.fetchall()]:
                    files |= _getFiles(con, to_lid, to_vid, allCollections)
            else:
                # Note that ``max(vid)`` doesn't cut it since it would make 2.0 > 10.0; however  to fix this
                # we'd either have to make (major, minor) columns out of version IDs or provide a sqlite3 C
                # extension with a version collator. But this is close enough for now. 🧐
                cursor.execute('SELECT max(vid) FROM labels WHERE lid = ?', (to_lid,))
                to_vid = cursor.fetchone()[0]
                files |= _getFiles(con, to_lid, to_vid, allCollections)
        else:
            # full lid-vid reference
            files |= _getFiles(con, to_lid, to_vid, allCollections)
    return files


def _writeChecksumManifest(chksumFN, lid, vid, con, prefixLen, allCollections):
    '''Write the checksum manifest for the label ``lid``::``vid`` found in database ``con`` to the
    file ``chksumFN``, stripping the prefixes of local filenames up to ``prefixLen`` characters,
    and optionally including ``allCollections`` for labels that reference bundle member entries
    by lid-only if True, otherwise the latest version only if False.
    '''
    _logger.debug('🧾 Writing checksum manifest for %s::%s to %s', lid, vid, chksumFN)
    md5, size, count = hashlib.new('md5'), 0, 0
    files = _getFiles(con, lid, vid, allCollections)
    with open(chksumFN, 'wb') as o:
        # The tuples are (lid, vid, filepath)—we care just about filepath
        for f in [i[2] for i in files]:
            with open(f, 'rb') as i:
                digest = getMD5(i)
                strippedFN = f[prefixLen:]
                entry = f'{digest}\t{strippedFN}\r\n'.encode('utf-8')
                o.write(entry)
                md5.update(entry)
                size += len(entry)
                count += 1
                if count % 100 == 0:
                    _logger.debug('⏲ Wrote %d entries into the checksum manifest', count)
    return md5.hexdigest(), size, count, files


def _writeTransferManifest(xferFN, prefixLen, files):
    '''Write the transfer manifest to the file ``xferFN`` for the given ``files``, stripping the prefix
    of local file paths up to ``prefixLen`` characters away.  ``files`` is a sequence of triples of
    (lid, vid, filepath).
    '''
    _logger.debug('🚢 Writing transfer manifest to %s', xferFN)
    md5, size, count = hashlib.new('md5'), 0, 0

    # First, organize by lid::vids → sequences of files
    lidvidsToFiles = {}
    for lid, vid, f in files:
        lidvid, transformedFN = f'{lid}::{vid}', '/' + f[prefixLen:]
        perLidvid = lidvidsToFiles.get(lidvid, [])
        perLidvid.append(transformedFN)
        lidvidsToFiles[lidvid] = perLidvid

    # Now write those organized into groups of lidvids
    with open(xferFN, 'wb') as o:
        for lidvid, filenames in lidvidsToFiles.items():
            for fn in filenames:
                entry = f'{lidvid:255}{fn:255}\r\n'.encode('utf-8')
                o.write(entry)
                md5.update(entry)
                size += len(entry)
                count += 1
                if count % 100 == 0:
                    _logger.debug('⌚️ Wrote %d entries into the transfer manifest', count)
    return md5.hexdigest(), size, count


def process(bundle, allCollections, con, timestamp):
    '''Generate a "checksum manifest", a "transfer manifest", and a PDS label from the given
    ``bundle``, which is an open file stream (with a ``name`` atribute) on the local
    filesystem. Return the name of the generated checksum manifest file. ``con`` is a sqlite3
    database connection containing information about the bundle. The ``timestamp`` tells us
    what to put into the label for thie AIP files about creation date and also to create
    filenames of our generated files.
    '''
    _logger.info('🏃‍♀️ Starting AIP generation for %s', bundle.name)

    prefixLen = len(os.path.dirname(os.path.abspath(bundle.name))) + 1
    lid, vid = getLogicalVersionIdentifier(parseXML(bundle))
    strippedLogicalID, slate = lid.split(':')[-1] + '_v' + vid, timestamp.date().strftime('%Y%m%d')

    # Easy one: the checksum† manifest
    # †It's actually an MD5 *hash*, not a checksum 😅
    chksumFN = strippedLogicalID + '_' + slate + '_checksum_manifest_v' + AIP_SIP_DEFAULT_VERSION + PDS_TABLE_FILENAME_EXTENSION
    chksumMD5, chksumSize, chksumNum, files = _writeChecksumManifest(
        chksumFN, lid, vid, con, prefixLen, allCollections
    )

    # Next: the transfer manifest
    xferFN = strippedLogicalID + '_' + slate + '_transfer_manifest_v' + AIP_SIP_DEFAULT_VERSION + PDS_TABLE_FILENAME_EXTENSION
    xferMD5, xferSize, xferNum = _writeTransferManifest(xferFN, prefixLen, files)

    # Finally, the XML label
    labelFN = strippedLogicalID + '_' + slate + '_aip_v' + AIP_SIP_DEFAULT_VERSION + PDS_LABEL_FILENAME_EXTENSION
    _writeLabel(
        labelFN,
        strippedLogicalID,
        lid,
        vid,
        chksumFN,
        chksumMD5,
        chksumSize,
        chksumNum,
        xferFN,
        xferMD5,
        xferSize,
        xferNum,
        timestamp
    )
    _logger.info('🎉 Success! AIP done, files generated:')
    _logger.info('📄 Checksum manifest: %s', chksumFN)
    _logger.info('📄 Transfer manifest: %s', xferFN)
    _logger.info('📄 XML label for them both: %s', labelFN)
    return chksumFN, xferFN, labelFN


def main():
    '''Check the command-line for options and create an AIP from the given bundle XML'''
    parser = argparse.ArgumentParser(description=_description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    addLoggingArguments(parser)
    addBundleArguments(parser)
    parser.add_argument(
        'bundle', type=argparse.FileType('rb'), metavar='IN-BUNDLE.XML', help='Root bundle XML file to read'
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, format='%(levelname)s %(message)s')
    _logger.debug('⚙️ command line args = %r', args)
    tempdir = tempfile.mkdtemp(suffix='.dir', prefix='aip')
    try:
        # Scout the enemy line
        dbfile = os.path.join(tempdir, 'pds-deep-archive.sqlite3')
        con = sqlite3.connect(dbfile)
        _logger.debug('⚙️ Creating potentially future-mulitprocessing–capable DB in %s', dbfile)
        with con:
            createSchema(con)
            comprehendDirectory(os.path.dirname(os.path.abspath(args.bundle.name)), con)

        # Make a timestamp but drop the microsecond resolution
        ts = datetime.utcnow()
        ts = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, microsecond=0, tzinfo=None)

        # Here we go, daddy
        process(args.bundle, args.include_latest_collection_only, con, ts)
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)

    _logger.info('👋 Thanks for using this program! Bye!')
    sys.exit(0)


if __name__ == '__main__':
    main()
