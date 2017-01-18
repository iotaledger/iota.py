#!/usr/bin/env python
# coding=utf-8
# :bc: Not importing unicode_literals because in Python 2 distutils,
# some values are expected to be byte strings.
from __future__ import absolute_import, division, print_function

from codecs import StreamReader, open
from sys import version_info

from setuptools import find_packages, setup

##
# Check Python version.
if version_info[0:2] < (2, 7):
  raise EnvironmentError('PyOTA requires Python 2.7 or greater.')

if (version_info[0] == 3) and (version_info[1] < 5):
  raise EnvironmentError('PyOTA requires Python 3.5 or greater.')

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
  version     = '1.0.0b6',

  packages              = find_packages('src'),
  include_package_data  = True,

  long_description = long_description,

  install_requires = [
    'filters',
    'requests',
    'six',
    'typing',
  ],

  test_suite    = 'test',
  test_loader   = 'nose.loader:TestLoader',
  tests_require = [
    'mock',
    'nose',
  ],

  license = 'MIT',

  classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ],

  keywords = 'iota,tangle,iot,internet of things,api,library',

  author        = 'Phoenix Zerin',
  author_email  = 'phx@phx.ph',
)
