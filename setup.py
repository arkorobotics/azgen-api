#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
from os.path import (abspath, dirname, join)
from subprocess import call

from setuptools import (Command, find_packages, setup)

from azapi.version import *

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(join(this_dir, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [r.strip() for r in f.readlines() if len(r.strip()) > 0]


class RunTests(Command):
    """Run all tests."""

    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        err_no = call(['py.test', '--cov=azapi', '--cov-report=term-missing'])
        raise SystemExit(err_no)


setup(
    name='azapi',
    version=__version__,
    description='The Activation.zone API.',
    long_description=long_description,
    url='https://github.com/arkorobotics/azgen-api',
    author=__author__,
    license=__license__,
    classifiers=[
        'Topic :: Utilities',
        'License :: {}'.format(__license__),
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='azgen, activation, zone, sota',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points={
        'console_scripts': [
            'azgen=azapi.cli:main'
        ],
    },
    cmdclass={'test': RunTests},
)
