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

from .constants import PDS_NS_URI
from lxml import etree
import logging, hashlib, os.path


# Logging
# -------
_logger = logging.getLogger(__name__)


# Private Constants
# -----------------

_bufsiz = 512  # Is there a better place to set this—or a better place to find it?


# Functions
# ---------

def getPrimariesAndOtherInfo(bundle):
    '''Get the "primaries" from the given bundle XML plus the logical identifier,
    plus the title plus the version ID (this function does too much)'''
    _logger.debug('Parsing XML in %r', bundle)
    primaries = set()
    tree = etree.parse(bundle)
    root = tree.getroot()
    members = root.findall(f'.//{{{PDS_NS_URI}}}Bundle_Member_Entry')
    for member in members:
        lid = kind = None
        for elem in member:
            if elem.tag == f'{{{PDS_NS_URI}}}lid_reference':
                lid = elem.text.strip()
            elif elem.tag == f'{{{PDS_NS_URI}}}member_status':
                kind = elem.text.strip().lower()
        if kind == 'primary' and lid:
            primaries.add(lid)
    _logger.debug('XML parse done, got %d primaries', len(primaries))
    matches = root.findall(f'./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}logical_identifier')
    logicalID = matches[0].text.strip()
    matches = root.findall(f'./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}title')
    title = matches[0].text.strip()
    matches = root.findall(f'./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}version_id')
    versionID = matches[0].text.strip()
    return primaries, logicalID, title, versionID


def getMD5(i):
    '''Compute an MD5 digest of the input stream ``i`` and return it as a hex string'''
    md5 = hashlib.new('md5')
    while True:
        buf = i.read(_bufsiz)
        if len(buf) == 0: break
        md5.update(buf)
    return md5.hexdigest()


def getLogicalIdentifierAndFileInventory(xmlFile):
    '''In the named local ``xmlFile ``, return a triple of its logical identifier via the XPath
    expression ``Product_Collection/Identification_Area/logical_identifier``, its lidvid
    (combination of logical identifier and version_id), and all ``file_name``
    in ``File`` in ``File_Area_Inventory`` entries. If there's no logical identifier, just return
    None, None, None
    '''
    _logger.debug('Parsing XML in %s', xmlFile)
    tree = etree.parse(xmlFile)
    root = tree.getroot()
    matches = root.findall(f'./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}logical_identifier')
    if not matches: return None, None, None
    lid = matches[0].text.strip()

    matches = root.findall(f'./{{{PDS_NS_URI}}}Identification_Area/{{{PDS_NS_URI}}}version_id')
    if not matches: return None, None, None
    lidvid = lid + '::' + matches[0].text.strip()

    if not lid: return None, None, None
    dirname = os.path.dirname(xmlFile)
    matches = root.findall(f'./{{{PDS_NS_URI}}}File_Area_Inventory/{{{PDS_NS_URI}}}File/{{{PDS_NS_URI}}}file_name')

    return lid, lidvid, [os.path.join(dirname, i.text.strip()) for i in matches]
