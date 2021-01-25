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


'''PDS AIP-GEN test base classes'''


from datetime import datetime, date
from lxml import etree
from pds.aipgen.aip import process as produce_aip
from pds.aipgen.constants import PDS_NS_URI
from pds.aipgen.sip import produce as produce_sip
from pds.aipgen.utils import createSchema, comprehendDirectory
import unittest, tempfile, shutil, os, pkg_resources, filecmp, codecs, sqlite3


class _FunctionalTestCase(unittest.TestCase):
    '''Abstract test harness for functional tests.

    This just sets up an input stream and temporary testing area for generated
    files. Subclasses actually do the tests.
    '''
    def getBundleFile(self):
        '''Return the name of the bundle file to test with'''
        raise NotImplementedError('Subclasses must implement ``getBundleFile``')
    def getAllCollectionsFlag(self):
        '''Return if we're doing all collections or just the latest when faced with lid-only references'''
        raise NotImplementedError('Subclasses must implement ``getAllCollectionsFlag``')
    def setUp(self):
        super(_FunctionalTestCase, self).setUp()
        bundleDir = pkg_resources.resource_filename(__name__, os.path.dirname(self.getBundleFile()))
        self.dbfile = tempfile.NamedTemporaryFile()
        self.con = sqlite3.connect(self.dbfile.name)
        with self.con:
            createSchema(self.con)
            comprehendDirectory(bundleDir, self.con)
        self.input = pkg_resources.resource_stream(__name__, self.getBundleFile())
        self.cwd, self.testdir = os.getcwd(), tempfile.mkdtemp()
        os.chdir(self.testdir)
        ts = datetime.utcnow()
        self.timestamp = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, microsecond=0, tzinfo=None)
    def tearDown(self):
        self.input.close()
        self.con.close()
        os.chdir(self.cwd)
        shutil.rmtree(self.testdir, ignore_errors=True)
        super(_FunctionalTestCase, self).tearDown()


class SIPFunctionalTestCase(_FunctionalTestCase):
    '''Functional test case for SIP generation.
    '''
    _urlXPath = f'./{{{PDS_NS_URI}}}Information_Package_Component_Deep_Archive/{{{PDS_NS_URI}}}manifest_url'
    def getValidSIPFileName(self):
        '''Return the name of the valid SIP file to compare against'''
        raise NotImplementedError('Subclasses must implement ``getValidSIPFileName``')
    def getBaseURL(self):
        '''Return the URL prefix to use for node data archives'''
        raise NotImplementedError('Subclasses must implement ``getBaseURL``')
    def getSiteID(self):
        '''Return the site ID for the manifest's label'''
        raise NotImplementedError('Subclasses must implement ``getSiteID``')
    def setUp(self):
        super(SIPFunctionalTestCase, self).setUp()
        self.valid = pkg_resources.resource_filename(__name__, self.getValidSIPFileName())
    def test_sip(self):
        '''Test if a SIP manifest works as expected'''
        manifest, ignoredLabel = produce_sip(
            bundle=self.input,
            hashName='md5',
            registryServiceURL=None,
            insecureConnectionFlag=True,
            site=self.getSiteID(),
            offline=True,
            baseURL=self.getBaseURL(),
            allCollections=self.getAllCollectionsFlag(),
            aipFile=None,
            con=self.con,
            timestamp=self.timestamp
        )
        self.assertTrue(filecmp.cmp(manifest, self.valid), "SIP manifest doesn't match the valid version")
    def test_label_url(self):
        '''Test if the label of a SIP manifest has the right ``manifest_url``'''
        ignoredManifest, label = produce_sip(
            bundle=self.input,
            hashName='md5',
            registryServiceURL=None,
            insecureConnectionFlag=True,
            site='PDS_ATM',
            offline=True,
            baseURL='https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/',
            allCollections=self.getAllCollectionsFlag(),
            aipFile=None,
            con=self.con,
            timestamp=self.timestamp
        )
        matches = etree.parse(label).getroot().findall(self._urlXPath)
        self.assertEqual(1, len(matches))
        url = matches[0].text
        self.assertTrue(url.startswith('https://pds.nasa.gov/data/pds4/manifests/'))
        # https://github.com/NASA-PDS/pds-deep-archive/issues/93
        currentYear = date.today().year
        # Account for the possibility that it's "Happy New Year 🍾" between label generation and testing
        legalYears = str(currentYear), str(currentYear + 1)
        urlEnd = url.split('/')[-2]
        self.assertTrue(urlEnd in legalYears, f"Expected {url} to contain either {legalYears} but didn't")


class AIPFunctionalTestCase(_FunctionalTestCase):
    '''Functional test case for AIP generation.
    '''
    def getManifests(self):
        '''Return a tuple of valid manifest file names, with checksum first and transfer second'''
        raise NotImplementedError('Subclasses must implement ``getManifests``')
    def setUp(self):
        super(AIPFunctionalTestCase, self).setUp()
        self.csum = pkg_resources.resource_filename(__name__, self.getManifests()[0])
        self.xfer = pkg_resources.resource_filename(__name__, self.getManifests()[1])
    def test_manifests(self):
        '''See if the AIP generator makes the two manifest files'''
        csum, xfer, ignoredLabel = produce_aip(
            self.input,
            allCollections=self.getAllCollectionsFlag(),
            con=self.con,
            timestamp=self.timestamp
        )

        # Normally we'd just do:
        #     self.assertTrue(filecmp.cmp(xfer, self.xfer, "AIP checksum manifest doesn't match the valid version"))
        # but can't simply check the valid version by a file comparison because the so-called "valid" version
        # has entries that are in a different (but still correct) order. So read them both in and see if their
        # data structures and line counts match.

        def _readTransferManifest(fn):
            d, lc = {}, 0
            with codecs.open(fn, encoding='utf-8') as f:
                for line in f:
                    uri, fn = line.split()
                    fns = d.get(uri, set())
                    fns.add(fn)
                    d[uri] = fns
                    lc += 1
            return d, lc
        (xfers, xl), (valids, vl)  = _readTransferManifest(xfer), _readTransferManifest(self.xfer)
        self.assertEqual(xl, vl, "AIP transfer manifest line counts don't match")
        self.assertEqual(xfers, valids, "AIP transfer manifest doesn't match the valid version")
