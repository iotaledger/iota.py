# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from six import binary_type

from iota.types import TryteString


# noinspection SpellCheckingInspection
class TryteStringTestCase(TestCase):
  def test_hello_world(self):
    """PoC test for TryteString"""
    self.assertEqual(
      TryteString.from_bytes(b'Hello, world!').value,
      b'RBTC9D9DCDQAEAKDCDFD9DSCFA',
    )

    self.assertEqual(
      binary_type(TryteString(b'RBTC9D9DCDQAEAKDCDFD9DSCFA')),
      b'Hello, world!',
    )
