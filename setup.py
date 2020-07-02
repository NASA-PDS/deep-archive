#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2019–2020 California Institute of Technology ("Caltech").
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


'''PDS Deep Archive Utilities'''


from codecs import open
from os import path
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()
with open(path.join(here, 'CHANGES.rst'), encoding='utf-8') as changes_file:
    changes = changes_file.read()
with open(path.join(here, 'src', 'pds', 'aipgen', 'version.txt'), encoding='utf-8') as version_file:
    version = version_file.read().strip()


_requirements = [
    'setuptools',  # All modern setup.py's should require setuptools
    'lxml',        # Needed for generating XML labels (since ElementTree can't add XML PIs above the root elem!)
]


setup(
    name='pds.deeparchive',
    version=version,
    description='PDS Deep Archive software for generating OAIS AIPs and SIPs for PDS4 Archives.',
    long_description=readme + '\n\n' + changes,
    keywords='PDS CCSDS OAIS AIP SIP metadata submission archive package',
    author='Sean Kelly',
    author_email='sean.kelly@jpl.nasa.gov',
    url='https://github.com/NASA-PDS/pds-deep-archive/',
    entry_points={
        'console_scripts': [
            'sipgen=pds.aipgen.sip:main',
            'aipgen=pds.aipgen.aip:main',
            'pds-deep-archive=pds.aipgen.main:main'
        ]
    },
    test_suite='pds.aipgen.tests.test_suite',
    namespace_packages=['pds'],
    packages=find_packages('src', exclude=['docs', 'tests', 'bootstrap', 'ez_setup']),
    package_dir={'': 'src'},
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst']
    },
    include_package_data=True,
    zip_safe=True,
    install_requires=_requirements,
    extras_require={'test': []},
    license='ALv2',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
    ]
)
