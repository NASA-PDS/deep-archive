#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2019 California Institute of Technology ("Caltech").
# ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.

from codecs import open
from os import path
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()
with open(path.join(here, 'CHANGES.rst'), encoding='utf-8') as changes_file:
    changes = changes_file.read()


_requirements = [
    'setuptools',  # All modern setup.py's should require setuptools
    'pysolr',
]


setup(
    name='pds.aipgen',
    version='0.0.0',
    description='SIP Generator',
    long_description=readme + '\n\n' + changes,
    keywords='CCSDS OAIS AIP SIP metadata submission archive package',
    author='Sean Kelly',
    author_email='sean.kelly@jpl.nasa.gov',
    url='https://github.jpl.nasa.gov/PDSEN/aip-gen',
    entry_points={
        'console_scripts': ['sipgen=pds.aipgen.sip:main']
    },
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
    license='Proprietary',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
    ]
)
