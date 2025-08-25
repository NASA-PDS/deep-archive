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
"""PDS AIP-GEN test base classes."""
import codecs
import filecmp
import importlib.resources
import os
import shutil
import sqlite3
import tempfile
import unittest
from datetime import date
from datetime import datetime

from lxml import etree
from pds2.aipgen.aip import process as produce_aip
from pds2.aipgen.constants import PDS_NS_URI
from pds2.aipgen.sip import produce as produce_sip
from pds2.aipgen.utils import comprehenddirectory
from pds2.aipgen.utils import createschema


class _FunctionalTestCase(unittest.TestCase):
    """Abstract test harness for functional tests.

    This just sets up an input stream and temporary testing area for generated
    files. Subclasses actually do the tests.
    """

    def getbundlefile(self):
        """Return the name of the bundle file to test with."""
        raise NotImplementedError("Subclasses must implement ``getbundlefile``")

    def getallcollectionsflag(self):
        """Return if we're doing all collections or just the latest when faced with lid-only references."""
        raise NotImplementedError("Subclasses must implement ``getallcollectionsflag``")

    def setUp(self):
        super(_FunctionalTestCase, self).setUp()
        bundledir = importlib.resources.files(__name__).joinpath(os.path.dirname(self.getbundlefile()))
        self.dbfile = tempfile.NamedTemporaryFile()
        self.con = sqlite3.connect(self.dbfile.name)
        with self.con:
            createschema(self.con)
            comprehenddirectory(bundledir, self.con)
        self.input = importlib.resources.files(__name__).joinpath(self.getbundlefile()).open("rb")
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
    """Functional test case for SIP generation."""

    _urlxpath = f"./{{{PDS_NS_URI}}}Information_Package_Component_Deep_Archive/{{{PDS_NS_URI}}}manifest_url"

    @classmethod
    def setUpClass(cls):
        """Child classes must override this method.

        In fact, they must define ``getvalidsipfilename`` as well as ``getsiteid`` and ``getbaseurl``.
        """
        raise unittest.SkipTest

    def getvalidsipfilename(self):
        """Return the name of the valid SIP file to compare against."""
        raise NotImplementedError("Subclasses must implement ``getvalidsipfilename``")

    def getbaseurl(self):
        """Return the URL prefix to use for node data archives."""
        raise NotImplementedError("Subclasses must implement ``getbaseurl``")

    def getsiteid(self):
        """Return the site ID for the manifest's label."""
        raise NotImplementedError("Subclasses must implement ``getsiteid``")

    def setUp(self):
        """Set up this text fixture, duh."""
        super(SIPFunctionalTestCase, self).setUp()
        self.valid = importlib.resources.files(__name__).joinpath(self.getvalidsipfilename())

    def test_sip(self):
        """Test if a SIP manifest works as expected."""
        manifest, ignoredlabel = produce_sip(
            bundle=self.input,
            hashname="md5",
            registryserviceurl=None,
            insecureconnectionflag=True,
            site=self.getsiteid(),
            baseurl=self.getbaseurl(),
            allcollections=self.getallcollectionsflag(),
            aipfile=None,
            con=self.con,
            timestamp=self.timestamp,
        )
        self.assertTrue(filecmp.cmp(manifest, self.valid), "SIP manifest doesn't match the valid version")

    @unittest.skip("temporarily skipping test per https://github.com/NASA-PDS/deep-archive/issues/169")
    def test_label_url(self):
        """Test if the label of a SIP manifest has the right ``manifest_url``."""
        ignoredmanifest, label = produce_sip(
            bundle=self.input,
            hashname="md5",
            registryserviceurl=None,
            insecureconnectionflag=True,
            site="PDS_ATM",
            baseurl="https://atmos.nmsu.edu/PDS/data/PDS4/LADEE/",
            allcollections=self.getallcollectionsflag(),
            aipfile=None,
            con=self.con,
            timestamp=self.timestamp,
        )
        matches = etree.parse(label).getroot().findall(self._urlxpath)
        self.assertEqual(1, len(matches))
        url = matches[0].text
        self.assertTrue(url.startswith("https://pds.nasa.gov/data/pds4/manifests/"))
        # https://github.com/NASA-PDS/pds-deep-archive/issues/93
        currentyear = date.today().year
        # Account for the possibility that it's "Happy New Year 🍾" between label generation and testing
        legalyears = str(currentyear), str(currentyear + 1)
        urlend = url.split("/")[-2]
        self.assertTrue(urlend in legalyears, f"Expected {url} to contain either {legalyears} but didn't")


class AIPFunctionalTestCase(_FunctionalTestCase):
    """Functional test case for AIP generation."""

    @classmethod
    def setUpClass(cls):
        """Child classes must override this method and define ``getmanifests``."""
        raise unittest.SkipTest

    def getmanifests(self):
        """Return a tuple of valid manifest file names, with checksum first and transfer second."""
        raise NotImplementedError("Subclasses must implement ``getmanifests``")

    def setUp(self):
        """Set up this test fixture."""
        super(AIPFunctionalTestCase, self).setUp()
        self.csum = importlib.resources.files(__name__).joinpath(self.getmanifests()[0])
        self.xfer = importlib.resources.files(__name__).joinpath(self.getmanifests()[1])

    def test_manifests(self):
        """See if the AIP generator makes the two manifest files."""
        csum, xfer, ignoredlabel = produce_aip(
            self.input, allcollections=self.getallcollectionsflag(), con=self.con, timestamp=self.timestamp
        )

        # Normally we'd just do:
        #     self.assertTrue(filecmp.cmp(xfer, self.xfer, "AIP checksum manifest doesn't match the valid version"))
        # but can't simply check the valid version by a file comparison because the so-called "valid" version
        # has entries that are in a different (but still correct) order. So read them both in and see if their
        # data structures and line counts match.

        def _readtransfermanifest(fn):
            d, lc = {}, 0
            with codecs.open(fn, encoding="utf-8") as f:
                for line in f:
                    uri, fn = line.split()
                    fns = d.get(uri, set())
                    fns.add(fn)
                    d[uri] = fns
                    lc += 1
            return d, lc

        (xfers, xl), (valids, vl) = _readtransfermanifest(xfer), _readtransfermanifest(self.xfer)
        self.assertEqual(xl, vl, "AIP transfer manifest line counts don't match")
        self.assertEqual(xfers, valids, "AIP transfer manifest doesn't match the valid version")
