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


'''PDS AIP-GEN: Unit tests of the Utilities package'''


import unittest, tempfile, os, pkg_resources, argparse, logging
from pds.aipgen.utils import (
    getDigest, getMD5, getPrimariesAndOtherInfo, getLogicalIdentifierAndFileInventory, addLoggingArguments,
    LogicalReference
)


EMPTY_SHA1 = 'da39a3ee5e6b4b0d3255bfef95601890afd80709'
EMPTY_MD5 = 'd41d8cd98f00b204e9800998ecf8427e'


class HashingTestCase(unittest.TestCase):
    '''Test hashing utilities'''
    def setUp(self):
        super(HashingTestCase, self).setUp()
        fd, self.emptyFileName = tempfile.mkstemp()
        os.close(fd)
    def test_getDigest(self):
        '''Ensure getDigest works on URLs and various hashing algorithms'''
        self.assertEqual(EMPTY_SHA1, getDigest('file:' + self.emptyFileName, 'sha1'))
        self.assertEqual(EMPTY_MD5, getDigest('file:' + self.emptyFileName, 'md5'))
    def test_getMD5(self):
        '''Ensure getMD5 works on file streams'''
        with open(self.emptyFileName, 'rb') as i:
            self.assertEqual(EMPTY_MD5, getMD5(i))
    def tearDown(self):
        os.unlink(self.emptyFileName)


class BundleParsingTestCase(unittest.TestCase):
    '''Test handling of bundle XML files'''
    def setUp(self):
        super(BundleParsingTestCase, self).setUp()
        self.emptyBun = pkg_resources.resource_stream(__name__, 'data/ladee_test/mission_bundle/LADEE_Bundle_1101.xml')
        self.fullBunFN = pkg_resources.resource_filename(
            __name__, 'data/ladee_test/mission_bundle/context/collection_mission_context.xml'
        )
    def test_primaries_etc(self):
        primaries, logicalID, title, versionID = getPrimariesAndOtherInfo(self.emptyBun)
        primaries = sorted(list(primaries))
        primaries = [i.lid.split(':')[-1] for i in primaries]
        self.assertEqual(3, len(primaries))
        self.assertEqual(['context_collection', 'document_collection', 'xml_schema_collection'], primaries)
        self.assertEqual('urn:nasa:pds:ladee_mission_bundle', logicalID)
        self.assertEqual('LADEE Mission Bundle', title)
        self.assertEqual('1.0', versionID)
    def test_lid_file_inventory_with_no_files(self):
        lid, lidvid, files = getLogicalIdentifierAndFileInventory(self.emptyBun.name)
        self.assertEqual('urn:nasa:pds:ladee_mission_bundle', lid)
        self.assertEqual('urn:nasa:pds:ladee_mission_bundle::1.0', lidvid)
        self.assertEqual(0, len(files))
    def test_lid_file_inventory_with_files(self):
        lid, lidvid, files = getLogicalIdentifierAndFileInventory(self.fullBunFN)
        self.assertEqual('urn:nasa:pds:ladee_mission:context_collection', lid)
        self.assertEqual('urn:nasa:pds:ladee_mission:context_collection::1.0', lidvid)
        self.assertEqual(1, len(files))
        self.assertEqual('collection_mission_context_inventory.tab', os.path.basename(files[0]))
    def tearDown(self):
        self.emptyBun.close()
        super(BundleParsingTestCase, self).tearDown()


class ArgumentTestCase(unittest.TestCase):
    '''Test command-line argument parsing'''
    def test_logging_arguments(self):
        class NonExitingArgumentParser(argparse.ArgumentParser):
            def exit(self, status=0, message=None):
                raise ValueError('Bad args')
        parser = NonExitingArgumentParser(usage='')
        addLoggingArguments(parser)
        self.assertEqual(logging.INFO, parser.parse_args([]).loglevel)
        self.assertEqual(logging.DEBUG, parser.parse_args(['--debug']).loglevel)
        self.assertEqual(logging.WARNING, parser.parse_args(['--quiet']).loglevel)
        self.assertRaises(ValueError, parser.parse_args, ['--debug', '--quiet'])


class LogicalReferenceTestCase(unittest.TestCase):
    '''Test case the LogicalReference class'''
    def test_init(self):
        '''Ensure init args work'''
        self.assertRaises(TypeError, LogicalReference, None)
        r = LogicalReference('a')
        self.assertEqual('a', r.lid)
        self.assertTrue(r.vid is None)
        r = LogicalReference('a', 'b')
        self.assertEqual('a', r.lid)
        self.assertEqual('b', r.vid)
    def test_repr(self):
        '''Make sure the representation function works'''
        self.assertEqual('<LogicalReference(lid=a,vid=None)>', repr(LogicalReference('a')))
        self.assertEqual('<LogicalReference(lid=a,vid=b)>', repr(LogicalReference('a', 'b')))
    def test_str(self):
        '''Check if LogicalReferences can be stringified'''
        self.assertEqual('a', str(LogicalReference('a')))
        self.assertEqual('a::b', str(LogicalReference('a', 'b')))
    def test_hash(self):
        '''Test if hasing of LogicalReferences is sane'''
        same1, same2, diff = LogicalReference('a', 'b'), LogicalReference('a', 'b'), LogicalReference('c')
        self.assertEqual(hash(same1), hash(same2))
        self.assertNotEqual(hash(same1), hash(diff))
    def test_eq(self):
        '''Guarantee that equality works'''
        a1, a2 = LogicalReference('a'), LogicalReference('a')
        b1, b2 = LogicalReference('b', '1'), LogicalReference('b', '1')
        c1, c2 = LogicalReference('c', '1'), LogicalReference('c', '2')
        self.assertEqual(a1, a2)
        self.assertEqual(b1, b2)
        self.assertNotEqual(c1, c2)
        self.assertNotEqual(a1, b1)
        self.assertNotEqual(a1, c1)
        self.assertNotEqual(a2, c2)
    def test_cmp(self):
        '''Clinch that comparisons work'''
        a, b = LogicalReference('a'), LogicalReference('b')
        a1, b1 = LogicalReference('a', '1'), LogicalReference('b', '1')
        a2, b2 = LogicalReference('a', '2'), LogicalReference('b', '2')
        self.assertTrue(a < b)
        self.assertTrue(a < a1 < a2 < b < b1 < b2)
        # And make sure version numbers sort like version numbers and not strings or floats
        v1, v2 = LogicalReference('v', '2.9'), LogicalReference('v', '2.10')
        self.assertTrue(v1 < v2)
    def test_match(self):
        '''Corroborate that matching other lids or lidvids work'''
        a, a1 = LogicalReference('a'), LogicalReference('a', '1')
        self.assertFalse(a.match('x'))
        self.assertFalse(a1.match('x'))
        self.assertFalse(a.match('x::1'))
        self.assertFalse(a1.match('x::1'))
        self.assertTrue(a.match('a'))
        self.assertTrue(a.match('a::1'))
        self.assertTrue(a1.match('a'))
        self.assertTrue(a1.match('a::1'))
        self.assertTrue(a.match('a::2'))
        self.assertFalse(a1.match('a::2'))
        self.assertRaises(ValueError, a.match, 'a::b::c')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
