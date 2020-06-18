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


'''PDS AIP-GEN functional tests'''


from datetime import datetime
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
    def setUp(self):
        super(_FunctionalTestCase, self).setUp()
        bundleDir = pkg_resources.resource_filename(__name__, 'data/ladee_test/mission_bundle')
        self.dbfile = tempfile.NamedTemporaryFile()
        self.con = sqlite3.connect(self.dbfile.name)
        with self.con:
            createSchema(self.con)
            comprehendDirectory(bundleDir, self.con)
        self.input = pkg_resources.resource_stream(__name__, 'data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml')
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
    def setUp(self):
        super(SIPFunctionalTestCase, self).setUp()
        self.valid = pkg_resources.resource_filename(
            __name__,
            'data/ladee_test/valid/ladee_mission_bundle_v1.0_sip_v1.0.tab'
        )
    def test_sip_of_a_ladee(self):
        '''Test if the SIP manifest of LADEE bundle works as expected'''
        manifest, ignoredLabel = produce_sip(
            bundle=self.input,
            hashName='md5',
            registryServiceURL=None,
            insecureConnectionFlag=True,
            site='PDS_ATM',
            offline=True,
            baseURL='https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/',
            allCollections=True,
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
            allCollections=True,
            aipFile=None,
            con=self.con,
            timestamp=self.timestamp
        )
        matches = etree.parse(label).getroot().findall(self._urlXPath)
        self.assertEqual(1, len(matches))
        self.assertTrue(matches[0].text.startswith('https://pds.nasa.gov/data/pds4/manifests/'))


class AIPFunctionalTestCase(_FunctionalTestCase):
    '''Functional test case for AIP generation.
    '''
    def setUp(self):
        super(AIPFunctionalTestCase, self).setUp()
        base = 'data/ladee_test/valid/ladee_mission_bundle_v1.0_'
        self.csum = pkg_resources.resource_filename(__name__, base + 'checksum_manifest_v1.0.tab')
        self.xfer = pkg_resources.resource_filename(__name__, base + 'transfer_manifest_v1.0.tab')
    def test_manifests(self):
        '''See if the AIP generator makes the two manifest files'''
        csum, xfer, ignoredLabel = produce_aip(
            self.input,
            allCollections=False,
            con=self.con,
            timestamp=self.timestamp
        )

        # Normally we'd just do:
        #     self.assertTrue(filecmp.cmp(xfer, self.xfer, "AIP checksum manifest doesn't match the valid version"))
        # but can't simply check the valid version by a file comparison because the so-called "valid" version
        # has entries that are in a different (but still correct) order. So read them both in and see if their
        # data structures match.

        def _readTransferManifest(fn):
            d = {}
            with codecs.open(fn, encoding='utf-8') as f:
                for line in f:
                    uri, fn = line.split()
                    fns = d.get(uri, set())
                    fns.add(fn)
                    d[uri] = fns
            return d
        xfers, valids = _readTransferManifest(xfer), _readTransferManifest(self.xfer)
        self.assertEqual(xfers, valids, "AIP transfer manifest doesn't match the valid version")


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
