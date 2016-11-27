#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from setuptools import setup

from iota import __version__

setup(
  name        = 'PyOTA',
  description = 'IOTA API library for Python',
  url         = 'https://github.com/iotaledger/iota.lib.py',
  version     = __version__,
  packages    = ['iota'],

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