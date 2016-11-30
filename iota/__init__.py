# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

DEFAULT_PORT = 14265

# Activate TrytesCodec.
from .codecs import *

# Make some imports accessible from the top level of the package.
from .adapter import *
from .api import *

# Don't forget to update version number in setup.py!
__version__ = '1.0.0'
