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


from .base import SIPFunctionalTestCase, AIPFunctionalTestCase
import unittest


class LADEESIPTest(SIPFunctionalTestCase):
    '''Test case for SIP generation for all collections from the LADEE test bundle, produced on behalf of
    the PDS Atmospheres node and using an ``atmost.nmsu.edu``-style base URL.
    '''
    def getBundleFile(self):
        return 'data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml'
    def getAllCollectionsFlag(self):
        return True
    def getValidSIPFileName(self):
        return 'data/ladee_test/valid/ladee_mission_bundle_v1.0_sip_v1.0.tab'
    def getBaseURL(self):
        return 'https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/'
    def getSiteID(self):
        return 'PDS_ATM'


class LADEAIPTest(AIPFunctionalTestCase):
    '''Test case for AIP generation for all collections from the LADEE test bundle'''
    def getBundleFile(self):
        return 'data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml'
    def getAllCollectionsFlag(self):
        return True
    def getManifests(self):
        base = 'data/ladee_test/valid/ladee_mission_bundle_v1.0_'
        return (base + 'checksum_manifest_v1.0.tab', base + 'transfer_manifest_v1.0.tab')


class _InsightSIPTest(SIPFunctionalTestCase):
    '''Abstract test case for SIP generation for the Insight Documents test bundle, produced on behalf of
    the Geo node and using a ``pds.nasa.gov``-style base URL. Subclasses further make concrete test cases
    that use either all collections or just the latest.
    '''
    def getBundleFile(self):
        return 'data/insight_documents/urn-nasa-pds-insight_documents/bundle_insight_documents.xml'
    def getBaseURL(self):
        return 'https://pds.nasa.gov/data/pds4/test-bundles/'
    def getSiteID(self):
        return 'PDS_GEO'


class _InsightAIPTest(AIPFunctionalTestCase):
    '''Abstract test case for AIP generation for the Insight Documents test bundle. Subclasses make
    concrete test cases for either all collections or just the latest when lid-only references appear.
    '''
    def getBundleFile(self):
        return 'data/insight_documents/urn-nasa-pds-insight_documents/bundle_insight_documents.xml'


class InsightAllSIPTest(_InsightSIPTest):
    '''Test case for SIP generation for all collections for the Insight Documents test bundle.'''
    def getValidSIPFileName(self):
        return 'data/insight_documents/valid/all/insight_documents_v2.0_sip_v1.0_20200702.tab'
    def getAllCollectionsFlag(self):
        return True


class InsightAllAIPTest(_InsightAIPTest):
    '''Test case for AIP generation for all collections for the Insight Documents test bundle.'''
    def getAllCollectionsFlag(self):
        return True
    def getManifests(self):
        base, suffix = 'data/insight_documents/valid/all/insight_documents_v2.0_', '_manifest_v2.0_20200702.tab'
        return (base + 'checksum' + suffix, base + 'transfer' + suffix)


class InsightLatestSIPTest(_InsightSIPTest):
    '''Test case for SIP generation for the latest versions for the Insight Documents test bundle.'''
    def getValidSIPFileName(self):
        return 'data/insight_documents/valid/latest/insight_documents_v2.0_sip_v1.0_20200702.tab'
    def getAllCollectionsFlag(self):
        return False


class InsightLatestAIPTest(_InsightAIPTest):
    '''Test case for AIP generation for the latest versions for the Insight Documents test bundle.'''
    def getAllCollectionsFlag(self):
        return False
    def getManifests(self):
        base, suffix = 'data/insight_documents/valid/latest/insight_documents_v2.0_', '_manifest_v2.0_20200702.tab'
        return (base + 'checksum' + suffix, base + 'transfer' + suffix)


class SecondaryCollectionSIPTest(SIPFunctionalTestCase):
    '''Test case for SIP generation when there are secondary collections in the bundle.'''
    def getBundleFile(self):
        return 'data/secondary_test/mission_bundle/LADEE_Bundle_1101.xml'
    def getAllCollectionsFlag(self):
        return True
    def getValidSIPFileName(self):
        return 'data/secondary_test/valid/ladee_mission_bundle_v1.0_sip_v1.0.tab'
    def getBaseURL(self):
        return 'https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/'
    def getSiteID(self):
        return 'PDS_ATM'


class SecondaryCollectionAIPTest(AIPFunctionalTestCase):
    '''Test case for AIP generation when there are secondary collections in the bundle.'''
    def getBundleFile(self):
        return 'data/secondary_test/mission_bundle/LADEE_Bundle_1101.xml'
    def getAllCollectionsFlag(self):
        return True
    def getManifests(self):
        base = 'data/secondary_test/valid/ladee_mission_bundle_v1.0_'
        return (base + 'checksum_manifest_v1.0.tab', base + 'transfer_manifest_v1.0.tab')


def test_suite():
    return unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromTestCase(LADEESIPTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(LADEAIPTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(InsightAllSIPTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(InsightAllAIPTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(InsightLatestSIPTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(InsightLatestAIPTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(SecondaryCollectionSIPTest),
        unittest.defaultTestLoader.loadTestsFromTestCase(SecondaryCollectionAIPTest),
    ])
