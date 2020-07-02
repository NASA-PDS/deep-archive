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

'''Constants'''


# URI prefix for logical identifiers of volume identifiers for products for Archive Information Packages
AIP_PRODUCT_URI_PREFIX = 'urn:nasa:pds:system_bundle:product_aip:'

# Version ID for the current PDS information model
INFORMATION_MODEL_VERSION = '1.13.0.0'

# Namespace URI for PDS XML
PDS_NS_URI = 'http://pds.nasa.gov/pds4/pds/v1'

# XML tag for a PDS product collection
PRODUCT_COLLECTION_TAG = f'{{{PDS_NS_URI}}}Product_Collection'

# Where to find the PDS schema
PDS_SCHEMA_URL = 'http://pds.nasa.gov/pds4/pds/v1 https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1D00.xsd'

# XML model processing instruction
XML_MODEL_PI = '''href="https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1D00.sch"
schematypens="http://purl.oclc.org/dsdl/schematron"'''

# Namespace URI for XML Schema
XML_SCHEMA_INSTANCE_NS_URI = 'http://www.w3.org/2001/XMLSchema-instance'

# Filename extension to use with PDS labels
PDS_LABEL_FILENAME_EXTENSION = '.xml'

# Filename extension for PDS tables
PDS_TABLE_FILENAME_EXTENSION = '.tab'

# Defaut AIP / SIP Version
AIP_SIP_DEFAULT_VERSION = '1.0'

# Command-line names for hash algorithms mapped to Python *implementation*
# name which are standardized (as lower case, no less) in the ``hashlib``.
# There are a lot more possible message digest algorithms, but we choose
# to support just three.
HASH_ALGORITHMS = {
    'MD5':     'md5',
    'SHA-1':   'sha1',
    'SHA-256': 'sha256',
}

# The "well-defined" location for SIP manifests
SIP_MANIFEST_URL = 'https://pds.nasa.gov/data/pds4/manifests/'
