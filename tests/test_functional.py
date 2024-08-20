# encoding: utf-8
#
# Copyright © 2020–2021 California Institute of Technology ("Caltech").
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
"""PDS AIP-GEN functional tests."""
import unittest
from urllib.error import URLError

from base import AIPFunctionalTestCase
from base import SIPFunctionalTestCase


class LADEESIPTest(SIPFunctionalTestCase):
    """Test case for SIP generation for all collections from the LADEE test bundle.

    This case is produced on behalf of the PDS Atmospheres node and using an ``atmost.nmsu.edu``-style base URL.
    """

    @classmethod
    def setUpClass(cls):
        """Override the abstract base class which just skips itself."""
        pass

    def getbundlefile(self):
        """Get the bundle file."""
        return "data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml"

    def getallcollectionsflag(self):
        """Get the all collections flag."""
        return True

    def getvalidsipfilename(self):
        """Get the valid SIP file name."""
        return "data/ladee_test/valid/ladee_mission_bundle_v1.0_sip_v1.0.tab"

    def getbaseurl(self):
        """Get the base URL."""
        return "https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/"

    def getsiteid(self):
        """Get the site ID."""
        return "PDS_ATM"


class LADEEAIPTest(AIPFunctionalTestCase):
    """Test case for AIP generation for all collections from the LADEE test bundle."""

    @classmethod
    def setUpClass(cls):
        """Override the abstract base class which just skips itself."""
        pass

    def getbundlefile(self):
        """Get the bundle file."""
        return "data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml"

    def getallcollectionsflag(self):
        """Get the all collections flag."""
        return True

    def getmanifests(self):
        """Get the manifests."""
        base = "data/ladee_test/valid/ladee_mission_bundle_v1.0_"
        return (base + "checksum_manifest_v1.0.tab", base + "transfer_manifest_v1.0.tab")


class SensitivityAIPTest(AIPFunctionalTestCase):
    """Test case for AIP generation with mixed-case "P-lines"."""

    @classmethod
    def setUpClass(cls):
        """Override the abstract base class which just skips itself."""
        pass

    def getbundlefile(self):
        """Get the bundle file."""
        return "data/sensitivity/mission_bundle/LADEE_Bundle_1101.xml"

    def getallcollectionsflag(self):
        """Get the all collections flag."""
        return True

    def getmanifests(self):
        """Get the manifests."""
        base = "data/sensitivity/valid/ladee_mission_bundle_v1.0_"
        return (base + "checksum_manifest_v1.0.tab", base + "transfer_manifest_v1.0.tab")


class SensitivitySIPTest(SIPFunctionalTestCase):
    """Test case for SIP generation with mixed-case "P-lines"."""

    @classmethod
    def setUpClass(cls):
        """Override the abstract base class which skips the test."""
        pass

    def getbundlefile(self):
        """Get the bundle file."""
        return "data/sensitivity/mission_bundle/LADEE_Bundle_1101.xml"

    def getallcollectionsflag(self):
        """Get the all collections flag (True)."""
        return True

    def getvalidsipfilename(self):
        """Get the valid SIP file name."""
        return "data/sensitivity/valid/ladee_mission_bundle_v1.0_sip_v1.0.tab"

    def getbaseurl(self):
        """Get the base URL."""
        return "https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/"

    def getsiteid(self):
        """Get the site ID."""
        return "PDS_ATM"


class _InsightSIPTest(SIPFunctionalTestCase):
    """Abstract test case for SIP generation for the Insight Documents test bundle.

    These tests are produced on behalf of the Geo node and using a ``pds.nasa.gov``-style base URL. Subclasses
    further make concrete test cases that use either all collections or just the latest.
    """

    def getbundlefile(self):
        """Get the bundle file."""
        return "data/insight_documents/urn-nasa-pds-insight_documents/bundle_insight_documents.xml"

    def getbaseurl(self):
        """Get the base URL."""
        return "https://pds.nasa.gov/data/pds4/test-bundles/"

    def getsiteid(self):
        """Get the site ID."""
        return "PDS_GEO"


class _InsightAIPTest(AIPFunctionalTestCase):
    """Abstract test case for AIP generation for the Insight Documents test bundle.

    Subclasses make concrete test cases for either all collections or just the latest when lid-only references appear.
    """

    def getbundlefile(self):
        """Get the bundle file."""
        return "data/insight_documents/urn-nasa-pds-insight_documents/bundle_insight_documents.xml"


class InsightAllSIPTest(_InsightSIPTest):
    """Test case for SIP generation for all collections for the Insight Documents test bundle."""

    def getvalidsipfilename(self):
        """Get the valid SIP file name."""
        return "data/insight_documents/valid/all/insight_documents_v2.0_sip_v1.0_20200702.tab"

    def getallcollectionsflag(self):
        """Get the all collections flag (True)."""
        return True


class InsightAllAIPTest(_InsightAIPTest):
    """Test case for AIP generation for all collections for the Insight Documents test bundle."""

    def getallcollectionsflag(self):
        """Get the all collections flag (True)."""
        return True

    def getmanifests(self):
        """Get the manifests."""
        base, suffix = "data/insight_documents/valid/all/insight_documents_v2.0_", "_manifest_v2.0_20200702.tab"
        return (base + "checksum" + suffix, base + "transfer" + suffix)


class InsightLatestSIPTest(_InsightSIPTest):
    """Test case for SIP generation for the latest versions for the Insight Documents test bundle."""

    def getvalidsipfilename(self):
        """Get the valid SIP file name."""
        return "data/insight_documents/valid/latest/insight_documents_v2.0_sip_v1.0_20200702.tab"

    def getallcollectionsflag(self):
        """Get the all collections flag (False)."""
        return False


class InsightLatestAIPTest(_InsightAIPTest):
    """Test case for AIP generation for the latest versions for the Insight Documents test bundle."""

    @classmethod
    def setUpClass(cls):
        """Override the abstract base class which just skips itself."""
        pass

    def getallcollectionsflag(self):
        """Get the all collections flag (False)."""
        return False

    def getmanifests(self):
        """Get the manifests."""
        base, suffix = "data/insight_documents/valid/latest/insight_documents_v2.0_", "_manifest_v2.0_20200702.tab"
        return (base + "checksum" + suffix, base + "transfer" + suffix)


class SecondaryCollectionSIPTest(SIPFunctionalTestCase):
    """Test case for SIP generation when there are secondary collections in the bundle."""

    @classmethod
    def setUpClass(cls):
        """Override the abstract base class which just skips this test."""
        pass

    def getbundlefile(self):
        """Get the bundle file."""
        return "data/secondary_test/mission_bundle/LADEE_Bundle_1101.xml"

    def getallcollectionsflag(self):
        """Get the all collections flag (True)."""
        return True

    def getvalidsipfilename(self):
        """Get the valid SIP file name."""
        return "data/secondary_test/valid/ladee_mission_bundle_v1.0_sip_v1.0.tab"

    def getbaseurl(self):
        """Get the base URL."""
        return "https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/"

    def getsiteid(self):
        """Get the site ID."""
        return "PDS_ATM"


class SecondaryCollectionAIPTest(AIPFunctionalTestCase):
    """Test case for AIP generation when there are secondary collections in the bundle."""

    def getbundlefile(self):
        """Get the bundle file."""
        return "data/secondary_test/mission_bundle/LADEE_Bundle_1101.xml"

    def getallcollectionsflag(self):
        """Get the all collections flag (True)."""
        return True

    def getmanifests(self):
        """Get the manifests."""
        base = "data/secondary_test/valid/ladee_mission_bundle_v1.0_"
        return (base + "checksum_manifest_v1.0.tab", base + "transfer_manifest_v1.0.tab")


class DuplicateTabFileTest(AIPFunctionalTestCase):
    """Test case for to see if we can handle tab files with duplicate P-lines in them."""

    @classmethod
    def setUpClass(cls):
        """Override the abstract base class which just skips itself."""
        pass

    def getbundlefile(self):
        """Get the bundle file."""
        return "data/duplicate_test/mission_bundle/Duplicate_Bundle_1101.xml"

    def getallcollectionsflag(self):
        """Get the all collections flag."""
        return True

    def getmanifests(self):
        """Get the manifests."""
        base = "data/duplicate_test/valid/ladee_mission_bundle_v1.0_"
        return (base + "checksum_manifest_v1.0.tab", base + "transfer_manifest_v1.0.tab")


class NAIF3SIPWithBadbaseurlTest(SIPFunctionalTestCase):
    """This is the test fixture for NAIF3 SIPs but with bad base URLs."""

    @classmethod
    def setUpClass(cls):
        """Override the abstract base class which just skips itself."""
        pass

    def getbundlefile(self):
        """Get the bundle file."""
        return "data/naif3/bundle_mars2020_spice_v003.xml"

    def getallcollectionsflag(self):
        """Get the all collections flag."""
        return True

    def getvalidsipfilename(self):
        """Get the valid SIP file name.

        This doesn't really matter because the goal is to raise a URLError when the SIP
        is generated.
        """
        return "does/not/matter.tab"

    def getsiteid(self):
        """Get the site ID."""
        return "PDS_ATM"

    def setUp(self):
        """Set up this text fixture."""
        super().setUp()
        from zope.component import provideUtility  # type: ignore
        from pds2.aipgen.utils import URLValidator

        self.validator = URLValidator()
        provideUtility(self.validator)

    def tearDown(self):
        """Tear down this text fixture."""
        del self.validator
        super().tearDown()

    def getbaseurl(self):
        """Get the base URL."""
        # This should always be a non-existent path no matter where this test is being run.
        # If you go out of your way to actually create this path on your system, please take
        # a moment to question your other life choices 🧐
        return "file:/definitely/a/non/exist/int/path/prefix/"

    # https://github.com/NASA-PDS/pds-deep-archive/issues/102
    def test_sip(self):
        """Make sure that the SIP generation fails with a URLError due to a non-existent base URL."""
        with self.assertRaises(URLError):
            super().test_sip()


def test_suite():
    """Return a suite of tests, duh flake8."""
    return unittest.TestSuite(
        [
            unittest.defaultTestLoader.loadTestsFromTestCase(DuplicateTabFileTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(InsightAllAIPTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(InsightAllSIPTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(InsightLatestAIPTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(InsightLatestSIPTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(LADEEAIPTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(LADEESIPTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(NAIF3SIPWithBadbaseurlTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(SecondaryCollectionAIPTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(SecondaryCollectionSIPTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(SensitivityAIPTest),
            unittest.defaultTestLoader.loadTestsFromTestCase(SensitivitySIPTest),
        ]
    )
