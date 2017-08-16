# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from six import PY3

if PY3:
  # noinspection SpellCheckingInspection
  from . import pykerl_py3 as pykerl
else:
  # noinspection SpellCheckingInspection
  from . import pykerl_py2 as pykerl
