#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2019–2021 California Institute of Technology ("Caltech").
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


import setuptools, versioneer


# Package Metadata
# ----------------
#
# Everything pertinent to the package is here (although we should really
# transition to the declarative all-in-setup.cfg style some day).

name               = 'pds.deeparchive'
description        = 'PDS Deep Archive software for generating OAIS AIPs and SIPs for PDS4 Archives.'
keywords           = ['PDS', 'CCSDS', 'OAIS', 'AIP', 'SIP', 'metadata', 'submission', 'archive', 'package']
zip_safe           = True
namespace_packages = ['pds']
test_suite         = 'pds.aipgen.tests.test_suite'
extras_require     = {'test': []}

entry_points = {
    'console_scripts': [
        'sipgen=pds.aipgen.sip:main',
        'aipgen=pds.aipgen.aip:main',
        'pds-deep-archive=pds.aipgen.main:main',
        'pds-deep-registry-archive=pds.aipgen.registry:main'
    ]
}

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: Other/Proprietary License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Scientific/Engineering',
]

requirements = [
    'setuptools',             # All modern setup.py's should require setuptools
    'lxml',                   # Needed for making XML labels (since ElementTree can't add XML PIs above the root elem!)
    # The next two packages are to support https://github.com/NASA-PDS/pds-deep-archive/issues/102
    'zope.component',         # To support singleton utilities
    'zope.interface',         # Interfaces and their implementations
    # This is for https://github.com/NASA-PDS/pds-deep-archive/issues/7
    'pds.api-client==0.4.0',  # So we don't have to ReST
    'sphinx-rtd-theme',
    'sphinxemoji',
]

# Below here, you shouldn't have to change anything:

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    author='PDS',
    author_email='pds_operator@jpl.nasa.gov',
    classifiers=classifiers,
    cmdclass=versioneer.get_cmdclass(),
    description=description,
    download_url='https://github.com/NASA-PDS/' + name + '/releases/download/…',
    entry_points=entry_points,
    extras_require=extras_require,
    include_package_data=True,
    install_requires=requirements,
    keywords=keywords,
    license='apache-2.0',  # There's almost no standardization about what goes here, even amongst ALv2 projects
    long_description=long_description,
    long_description_content_type='text/markdown',
    name=name,
    namespace_packages=namespace_packages,
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src', exclude=['docs', 'tests']),
    python_requires='>=3.6',
    test_suite=test_suite,
    url='https://github.com/NASA-PDS/' + name,
    version=versioneer.get_version(),
    zip_safe=zip_safe,
)
