#!/usr/bin/env python
# coding=utf-8
# :bc: Not importing unicode_literals because in Python 2 distutils,
# some values are expected to be byte strings.
from __future__ import absolute_import, division, print_function

from codecs import StreamReader, open
from sys import version_info

from setuptools import find_packages, setup

##
# Load long description for PyPi.
with open('README.rst', 'r', 'utf-8') as f: # type: StreamReader
  long_description = f.read()


##
# Certain dependencies are optional depending on Python version.
dependencies = [
  'filters',
  'six',

  # ``security`` extra wasn't introduced until 2.4.1
  # http://docs.python-requests.org/en/latest/community/updates/#id35
  'requests[security] >= 2.4.1',
]

if version_info[0] < 3:
  dependencies.extend([
    'typing',
  ])


##
# Off we go!
setup(
  name        = 'PyOTA',
  description = 'IOTA API library for Python',
  url         = 'https://github.com/iotaledger/iota.lib.py',
  version     = '1.1.3',

  packages              = find_packages('src'),
  include_package_data  = True,

  long_description = long_description,

  install_requires = dependencies,

  extras_require = {
    'ccurl': ['pyota-ccurl'],
  },

  test_suite    = 'test',
  test_loader   = 'nose.loader:TestLoader',
  tests_require = [
    'mock',
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
