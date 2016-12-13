#!/usr/bin/env python
# coding=utf-8
# :bc: Not importing unicode_literals because in Python 2 distutils,
# some values are expected to be byte strings.
from __future__ import absolute_import, division, print_function

from codecs import StreamReader, open
from sys import version_info

from setuptools import setup

with open('README.rst', 'r', 'utf-8') as f: # type: StreamReader
  long_description = f.read()

dependencies = [
    'filters',
    'requests',
    'six',
  ]

if version_info[0:2] < (3, 5):
  dependencies.append('typing')

setup(
  name        = 'PyOTA',
  description = 'IOTA API library for Python',
  url         = 'https://github.com/iotaledger/pyota',
  version     = '1.0.0',

  packages    = ['iota'],

  long_description = long_description,

  install_requires = dependencies,

  test_suite    = 'test',
  test_loader   = 'nose.loader:TestLoader',
  tests_require = [
    'mock',
    'nose',
  ],

  data_files = [
    ('', ['LICENSE']),
  ],

  license = 'MIT',

  classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ],

  keywords = 'iota,tangle,iot,internet of things,api,library',

  author        = 'Phoenix Zerin',
  author_email  = 'phx@phx.ph',
)
