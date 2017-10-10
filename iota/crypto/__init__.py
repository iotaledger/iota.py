# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals


# Load curl library.
# If a compiled c extension is available, we will prefer to load that;
# otherwise fall back to pure-Python implementation.
# https://pypi.python.org/pypi/PyOTA-CCurl
try:
  from ccurl import *
except ImportError:
  from .pycurl import *


FRAGMENT_LENGTH = 2187
"""
Number of trytes per fragment.

Fragments are used to divide up really long tryte sequences into
manageable chunks (similar in concept to AES blocks).
"""


class SeedWarning(Warning):
  """
  Warning for inappropriate seeds.
  """
  pass
