# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals


# Load curl library.
# If a compiled c extension is available, we will prefer to load that
# (once implemented).
from .pycurl import *
