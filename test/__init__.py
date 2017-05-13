# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from six import PY3

if PY3:
  # In Python 3 the ``mock`` library was moved into the stdlib.
  # noinspection PyUnresolvedReferences
  from unittest import mock
else:
  # In Python 2, the ``mock`` library is included as a dependency.
  # noinspection PyUnresolvedReferences
  import mock
