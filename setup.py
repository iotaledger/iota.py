#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from codecs import StreamReader, open
from setuptools import setup


with open('README.rst', 'r', 'utf-8') as f: # type: StreamReader
  long_description = f.read()

setup(
  name        = 'PyOTA',
  description = 'IOTA API library for Python',
  url         = 'https://github.com/iotaledger/iota.lib.py',
  version     = '1.0.0',
  packages    = ['iota'],

  long_description = long_description,

  install_requires = [
    'requests',
    'six',
    'typing ; python_version < "3.5"',
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
