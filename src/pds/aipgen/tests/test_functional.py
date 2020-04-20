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


import unittest, tempfile, shutil, os, pkg_resources, filecmp
from pds.aipgen.sip import produce


class SIPFunctionalTestCase(unittest.TestCase):
    '''Functional test case for SIP generation.

    TODO: factor this out so we can generically do AIP and other file-based functional tests too.
    '''
    def setUp(self):
        super(SIPFunctionalTestCase, self).setUp()
        self.input = pkg_resources.resource_stream(__name__, 'data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml')
        self.valid = pkg_resources.resource_filename(__name__, 'data/ladee_test/valid/ladee_mission_bundle_v1.0_sip_v1.0.tab')
        self.cwd, self.testdir = os.getcwd(), tempfile.mkdtemp()
        os.chdir(self.testdir)
    def test_sip_of_a_ladee(self):
        '''Test if the SIP manifest of LADEE bundle works as expected'''
        manifest, label = produce(
            bundle=self.input,
            hashName='md5',
            registryServiceURL=None,
            insecureConnectionFlag=True,
            site='PDS_ATM',
            offline=True,
            baseURL='https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/',
            aipFile=None
        )
        self.assertTrue(filecmp.cmp(manifest, self.valid), "SIP manifest doesn't match the valid version")
    def tearDown(self):
        self.input.close()
        os.chdir(self.cwd)
        shutil.rmtree(self.testdir, ignore_errors=True)
        super(SIPFunctionalTestCase, self).tearDown()


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
