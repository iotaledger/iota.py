# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals


try:
  from ckerl import Kerl, trits_to_bytes, bytes_to_trits, trits_to_trytes, \
    trytes_to_trits
except ImportError:
  from .pykerl import Kerl
  from .conv import trits_to_bytes, bytes_to_trits, trits_to_trytes, \
    trytes_to_trits
