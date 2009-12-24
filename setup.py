#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glob

from distutils.cmd import Command

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# build targets
(DEFAULT, MAEMO) = range(2)

# import the mushin module locally for module metadata
sys.path.insert(0, 'python')
import mushin

# if we are running "setup.py sdist", include all targets (see below)
building_source = ('sdist' in sys.argv)


# build target
if 'TARGET' in os.environ:
    if os.environ['TARGET'].strip().lower() == 'maemo':
        target = MAEMO
else:
    target = DEFAULT


# files to install
inst_desktop_maemo = [ 'data/mushin-maemo.desktop' ]

data_files = []

packages = [
        'mushin',
            'mushin.command', 'mushin.common',
            'mushin.extern',
                'mushin.extern.log',
                'mushin.extern.command',
                'mushin.extern.paisley',
            'mushin.maemo', 'mushin.model'
]

if target == MAEMO or building_source:
    data_files += [
      ('share/applications/hildon', inst_desktop_maemo),
    ]
    packages += [
      'mushin.maemo',
    ]

requirements = ['python-twisted']
# if sys.version_info < (2, 6):
#    requirements += ['simplejson']



setup(
    name = 'mushin',
    version = '0.0.0',
    description = 'Application for Getting Things Done',
    long_description = \
"""This is an application to implement a Getting Things Done Workflow.
The application includes a command-line text client and a Maemo 5 application
for the N900.  It uses CouchDB for storage.""",
    author = 'Thomas Vander Stichele',
    author_email = 'thomas at apestaart dot org',
    license = 'GPLv3',
    url = 'http://thomas.apestaart.org/thomas/trac/',

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users',
        'License :: OSI Approved :: GPL License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
    ],
    package_dir = { '': 'python' },
    packages = packages,
    scripts = glob.glob('bin/*'),
    data_files = data_files,
    # test_suite = 'mushin.test',

#    install_requires = requirements,

#    entry_points = {
#        'console_scripts': [
#            'gtd = mushin.command.main:main',
#            'mushin-maemo = mushin.maemo.main:main',
#        ],
#    },
)
