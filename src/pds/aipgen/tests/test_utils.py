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


from pds.aipgen.utils import addLoggingArguments, getDigest, getLogicalVersionIdentifier, getMD5, parseXML
import unittest, tempfile, os, pkg_resources, argparse, logging


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
    def test_lid_vid_retrieval(self):
        liv, vid = getLogicalVersionIdentifier(parseXML(self.emptyBun))
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


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
