#!/usr/bin/env python
# coding=utf-8
# :bc: Not importing unicode_literals because in Python 2 distutils,
# certain values (e.g., extension name) have to be byte strings.
from __future__ import absolute_import, division, print_function

from codecs import StreamReader, open

from os.path import join, basename
from setuptools import Extension, setup
from setuptools.glob import iglob
from six import PY3

with open('README.rst', 'r', 'utf-8') as f: # type: StreamReader
  long_description = f.read()

ccurl_sources = [
  f for f in iglob(join('ext', 'ccurl', 'src', '*.[ci]'))
    if not basename(f).endswith('_wrap.c')
]

if not ccurl_sources:
  raise EnvironmentError(
    'Unable to find ccurl sources.  Try running `git submodule init` first.',
  )

swig_opts = ['-py3'] if PY3 else []

setup(
  name        = 'PyOTA',
  description = 'IOTA API library for Python',
  url         = 'https://github.com/iotaledger/pyota',
  version     = '1.0.0',

  packages    = ['iota', 'ccurl'],
  package_dir = {
    'iota':   '',
    'ccurl':  'ext/ccurl/src',
  },

  long_description = long_description,

  install_requires = [
    'filters',
    'requests',
    'six',
    'typing ; python_version < "3.5"',
  ],

  ext_modules = [
    Extension('_ccurl', ccurl_sources, swig_opts=swig_opts),
  ],

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
