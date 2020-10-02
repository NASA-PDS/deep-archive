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


u'''AIP and SIP generation'''

from . import VERSION
from .aip import process as aipProcess
from .constants import HASH_ALGORITHMS
from .sip import addSIParguments
from .sip import produce as sipProcess
from .utils import addLoggingArguments, addBundleArguments, createSchema, comprehendDirectory
from datetime import datetime
import argparse, sys, logging, tempfile, sqlite3, os, shutil


# Constants
# ---------

# Module metadata:
__version__ = VERSION

# For ``--help``; note this is hand-formatted to wrap at 80 columns:
_description = '''
Generate an Archive Information Package (AIP) and a Submission Information
Package (SIP). This creates three files for the AIP in the current directory
(overwriting them if they already exist):
① a "checksum manifest" which contains MD5 hashes of *all* files in a product
② a "transfer manifest" which lists the "lidvids" for files within each XML
  label mentioned in a product
③ an XML label for these two files.

It also creates two files for the SIP (also overwriting them if they exist):
① A "SIP manifest" file; and an XML label of that file too. The names of
  the generated files are based on the logical identifier found in the 
  bundle file, and any existing files are overwritten. The names of the 
  generated files are printed upon successful completion.
② A PDS XML label of that file.

The files are created in the current working directory when this program is
run. The names of the files are based on the logical identifier found in the
bundle file, and any existing files are overwritten. The names of the
generated files are printed upon successful completion.
'''

# Logging:
_logger = logging.getLogger(__name__)


# Functions
# ---------

def main():
    '''Make an AIP and a SIP'''
    parser = argparse.ArgumentParser(description=_description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    addBundleArguments(parser)
    addSIParguments(parser)
    addLoggingArguments(parser)
    parser.add_argument(
        'bundle', type=argparse.FileType('rb'), metavar='IN-BUNDLE.XML', help='Bundle XML file to read'
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, format='%(levelname)s %(message)s')
    _logger.info('👟 PDS Deep Archive, version %s', __version__)
    _logger.debug('⚙️ command line args = %r', args)
    tempdir = tempfile.mkdtemp(suffix='.dir', prefix='deep')
    try:
        # Make a site survey
        dbfile = os.path.join(tempdir, 'pds-deep-archive.sqlite3')
        con = sqlite3.connect(dbfile)
        _logger.debug('⚙️ Creating potentially future-mulitprocessing–capable DB in %s', dbfile)
        with con:
            createSchema(con)
            comprehendDirectory(os.path.dirname(os.path.abspath(args.bundle.name)), con)

        # Make a timestamp but without microseconds
        ts = datetime.utcnow()
        ts = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second, microsecond=0, tzinfo=None)

        chksumFN, dummy, dummy = aipProcess(args.bundle, args.include_latest_collection_only, con, ts)
        with open(chksumFN, 'rb') as chksumStream:
            sipProcess(
                args.bundle,
                # TODO: Temporarily hardcoding these values until other modes are available
                # HASH_ALGORITHMS[args.algorithm],
                # args.url,
                # args.insecure,
                HASH_ALGORITHMS['MD5'],
                '',
                '',
                args.site,
                args.offline,
                args.bundle_base_url,
                chksumStream,
                args.include_latest_collection_only,
                con,
                ts
            )
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)
    _logger.info("👋 That's it! Thanks for making an AIP and SIP with us today. Bye!")
    sys.exit(0)


if __name__ == '__main__':
    main()
