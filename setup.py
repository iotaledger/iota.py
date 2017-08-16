#!/usr/bin/env python
# coding=utf-8
# :bc: Not importing unicode_literals because in Python 2 distutils,
# some values are expected to be byte strings.
from __future__ import absolute_import, division, print_function

from codecs import StreamReader, open

from setuptools import find_packages, setup

##
# Load long description for PyPi.
with open('README.rst', 'r', 'utf-8') as f: # type: StreamReader
  long_description = f.read()


##
# Off we go!
setup(
  name        = 'PyOTA',
  description = 'IOTA API library for Python',
  url         = 'https://github.com/iotaledger/iota.lib.py',
  version     = '1.2.0b1',

  long_description = long_description,

  packages =
    find_packages('.', exclude=(
      'examples', 'examples.*',
      'test', 'test.*',
    )),

  include_package_data  = True,

  # http://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point
  entry_points = {
    'console_scripts': [
      'iota-cli=iota.bin.repl:main',
    ],
  },

  install_requires = [
    'filters',
    'six',

    # ``security`` extra wasn't introduced until 2.4.1
    # http://docs.python-requests.org/en/latest/community/updates/#id35
    'requests[security] >= 2.4.1',

    'typing; python_version < "3.0"',
  ],

  extras_require = {
    'ccurl': ['pyota-ccurl'],
  },

  test_suite    = 'test',
  test_loader   = 'nose.loader:TestLoader',
  tests_require = [
    'mock; python_version < "3.0"',
    'nose',
  ],

  license = 'MIT',

  classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ],

  keywords =
    'iota,tangle,iot,internet of things,api,library,cryptocurrency,'
    'balanced ternary',

  author        = 'Phoenix Zerin',
  author_email  = 'phx@phx.ph',
)
