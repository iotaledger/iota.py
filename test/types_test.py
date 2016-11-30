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
      TryteString.from_bytes(b'Hello, world!').trytes,
      b'RBTC9D9DCDQAEAKDCDFD9DSCFA',
    )

    self.assertEqual(
      binary_type(TryteString(b'RBTC9D9DCDQAEAKDCDFD9DSCFA')),
      b'Hello, world!',
    )

  def test_init_error_odd_length(self):
    """
    Attempting to create a TryteString from a sequence with length not
      divisible by 2.
    """
    with self.assertRaises(ValueError):
      TryteString(b'RBTC9D9DCDQAEAKDCDFD9DSCFA9')
