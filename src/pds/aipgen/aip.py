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


from .constants import PDS_NS_URI, XML_SCHEMA_INSTANCE_NS_URI, PDS_SCHEMA_URL, XML_MODEL_PI, INFORMATION_MODEL_VERSION
from .utils import getPrimariesAndOtherInfo, getMD5, parseXML, addLoggingArguments
from datetime import datetime
from lxml import etree
import argparse, logging, sys, os, os.path, hashlib


# Constants
# ---------

# For ``--help``:
_version = '0.0.0'
_description = '''Generate an Archive Information Package or AIP. An AIP consists of three files:
 ➀ a "checksum manifest" which contains MD5 hashes of *all* files in a product;
 ➁ a "transfer manifest" which lists the "lidvids" for files within each XML label mentioned in a product; and
 ➂ an XML label for these two files. You can use the checksum manifest file ➀ as input to ``sipgen`` in
 order to create a Submission Information Package.'''

# Prefix to use for logical IDs for labels for AIPs
_aipProductPrefix = 'urn:nasa:pds:system_bundle:product_aip:'

# Comment to insert near the top of an AIP XML label
_iaComment = 'Parse name from bundle logical_identifier, e.g. urn:nasa:pds:ladee_mission_bundle would be ladee_mission_bundle'

# Logging:
_logger = logging.getLogger(__name__)


# Functions
# ---------

def _writeChecksumManifest(checksumManifestFN, dn):
    '''Come up with a "checksum manifest"† for the files in the directory named by ``dn``
    and write it to the file named ``checksumManifestFN``, overwriting any existing file.
    Return the hex MD5 digest, byte size of the file we created, and the number of records
    in the file.
    '''
    _logger.info('🧾 Writing checksum manifest for %s to %s', dn, checksumManifestFN)
    md5, size, count = hashlib.new('md5'), 0, 0
    prefixLen = len(dn)
    with open(checksumManifestFN, 'wb') as o:
        for dirpath, dirnames, filenames in os.walk(dn):
            for fn in filenames:
                fileToHash = os.path.join(dirpath, fn)
                with open(fileToHash, 'rb') as i:
                    digest = getMD5(i)
                    strippedFN = fileToHash[prefixLen + 1:]
                    entry = f'{digest}\t{strippedFN}\n'.encode('utf-8')
                    o.write(entry)
                    md5.update(entry)
                    size += len(entry)
                    count += 1
    return md5.hexdigest(), size, count


def _getLIDVIDandFileInventory(xmlFile):
    '''In the named local ``xmlFile ``, return a double of its logical identifier + double colon
    + version identifier and all ``file_name`` entries. If there's no logical identifier or version
    identifier, return None and None.
    '''
    _logger.debug('📜 Analyzing XML in %s', xmlFile)
    tree = parseXML(xmlFile)
    root = tree.getroot()
    matches = root.findall(f'./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}logical_identifier')
    if not matches:
        _logger.warning('📯 XML file %s lacks a logical_identifier; skipping it', xmlFile)
        return None, None
    lid = matches[0].text.strip()

    matches = root.findall(f'./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}version_id')
    if not matches:
        _logger.warning('📯 XML file %s lacks a version_id; skipping it', xmlFile)
        return None, None
    lidvid = lid + '::' + matches[0].text.strip()

    if not lid: return None, None
    dirname = os.path.dirname(xmlFile)
    matches = root.findall(f'.//{{{PDS_NS_URI}}}file_name')
    files = [os.path.join(dirname, i.text.strip()) for i in matches]

    _logger.debug('🔍 For %s in %s we have %d files', lidvid, xmlFile, len(files))
    return lidvid, files


def _writeTransferManifest(transferManifestFN, dn):
    '''Check for all ``.xml`` files in the directory tree rooted at ``dn`` and get each one's
    "lidvid" and set of all files mentioned within.  Write a transfer manifest for every file
    mentioned inlcuding the XML files too prefixed and grouped by "lidvid". Root paths in the
    transfer manifest at the top level of the bundle file given and turn all ``/`` directory
    separators into backslashes. Return a triple of the MD5 digest, byte size, and number of
    entries in the transfer manifest we created.'''
    _logger.info('🚢 Writing transfer manifest for %s to %s', dn, transferManifestFN)
    md5, size, count = hashlib.new('md5'), 0, 0
    lidvidsToFiles = {}
    for dirpath, dirnames, filenames in os.walk(dn):
        for fn in filenames:
            if fn.lower().endswith('.xml'):
                xmlFile = os.path.join(dirpath, fn)
                lidvid, inventory = _getLIDVIDandFileInventory(xmlFile)
                if lidvid is None: continue
                files = lidvidsToFiles.get(lidvid, set())
                files |= set(inventory)
                files.add(xmlFile)
                lidvidsToFiles[lidvid] = files
    prefixLen = len(dn)
    with open(transferManifestFN, 'wb') as o:
        for lidvid, filenames in lidvidsToFiles.items():
            for fn in filenames:
                transformedFN = '\\' + fn[prefixLen + 1:].replace('/', '\\')
                entry = f'{lidvid:255} {transformedFN:255}\n'.encode('utf-8')
                o.write(entry)
                md5.update(entry)
                size += len(entry)
                count += 1
    return md5.hexdigest(), size, count


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
    '''

    _logger.info('🏷  Writing AIP label to %s', labelOutputFile)
    ts = datetime.utcnow()
    ts = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, microsecond=0, tzinfo=None)

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
    etree.SubElement(identificationArea, prefix + 'logical_identifier').text = _aipProductPrefix + logicalIDfragment.split(':')[-1]
    etree.SubElement(identificationArea, prefix + 'version_id').text = '1.0'
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
    etree.SubElement(modificationDetail, prefix + 'modification_date').text = ts.date().isoformat()
    etree.SubElement(modificationDetail, prefix + 'version_id').text = '1.0'
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
    etree.SubElement(f, prefix + 'creation_date_time').text = ts.isoformat()
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
    etree.SubElement(f, prefix + 'creation_date_time').text = ts.isoformat()
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
    fc = etree.Element(prefix + 'Field_Character')
    rc.append(fc)
    etree.SubElement(fc, prefix + 'name').text = 'LIDVID'
    etree.SubElement(fc, prefix + 'field_location', unit='byte').text = '1'
    etree.SubElement(fc, prefix + 'data_type').text = 'ASCII_String'
    etree.SubElement(fc, prefix + 'field_length', unit='byte').text = '255'
    fc = etree.Element(prefix + 'Field_Character')
    rc.append(fc)
    etree.SubElement(fc, prefix + 'name').text = 'File Specification Name'
    etree.SubElement(fc, prefix + 'field_location', unit='byte').text = '2'
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


def process(bundle):
    '''Generate a "checksum manifest", a "transfer manifest", and a PDS label from the given
    ``bundle``, which is an open file stream (with a ``name`` atribute) on the local
    filesystem. Return the name of the generated checksum manifest file.
    '''
    _logger.info('🏃‍♀️ Starting AIP generation for %s', bundle.name)
    d = os.path.dirname(os.path.abspath(bundle.name))

    # Get the bundle's primary collections and other useful info
    primaries, bundleLID, title, bundleVID = getPrimariesAndOtherInfo(bundle)
    strippedLogicalID = bundleLID.split(':')[-1]

    # Easy one: the checksum† manifest
    # †It's actually an MD5 *hash*, not a checksum 😅
    chksumFN = strippedLogicalID + '_checksum_manifest_v' + bundleVID + '.tab'
    chksumMD5, chksumSize, chksumNum = _writeChecksumManifest(chksumFN, d)

    # Next: the transfer manifest.
    xferFN = strippedLogicalID + '_transfer_manifest_v' + bundleVID + '.tab'
    xferMD5, xferSize, xferNum = _writeTransferManifest(xferFN, d)

    # Finally, the XML label.
    labelFN = strippedLogicalID + '_aip_v' + bundleVID + '.xml'
    _writeLabel(
        labelFN,
        strippedLogicalID,
        bundleLID,
        bundleVID,
        chksumFN,
        chksumMD5,
        chksumSize,
        chksumNum,
        xferFN,
        xferMD5,
        xferSize,
        xferNum
    )
    _logger.info('🎉  Success! AIP done, files generated:')
    _logger.info('• Checksum manifest: %s', chksumFN)
    _logger.info('• Transfer manifest: %s', xferFN)
    _logger.info('• XML label for them both: %s', labelFN)
    return chksumFN


def main():
    '''Check the command-line for options and create an AIP from the given bundle XML'''
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument('--version', action='version', version=f'%(prog)s {_version}')
    addLoggingArguments(parser)
    parser.add_argument(
        'bundle', type=argparse.FileType('rb'), metavar='IN-BUNDLE.XML', help='Root bundle XML file to read'
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, format='%(levelname)s %(message)s')
    _logger.debug('⚙️ command line args = %r', args)
    process(args.bundle)
    _logger.info('👋 Thanks for using this program! Bye!')
    sys.exit(0)


if __name__ == '__main__':
    main()
