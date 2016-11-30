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
      TryteString.from_bytes(b'Hello, IOTA!').trytes,
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

    self.assertEqual(
      binary_type(TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')),
      b'Hello, IOTA!',
    )

  def test_equality_comparison(self):
    """Comparing TryteStrings for equality."""
    trytes1 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')
    trytes2 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')
    trytes3 = TryteString(b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA')

    self.assertTrue(trytes1 == trytes2)
    self.assertFalse(trytes1 != trytes2)

    self.assertFalse(trytes1 == trytes3)
    self.assertTrue(trytes1 != trytes3)

    self.assertTrue(trytes1 is trytes1)
    self.assertFalse(trytes1 is trytes2)
    self.assertFalse(trytes1 is trytes3)

  # noinspection PyTypeChecker
  def test_equality_comparison_error_wrong_type(self):
    """
    Attempting to compare a TryteString with something that is not a
      TryteString.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    with self.assertRaises(TypeError):
      trytes == b'RBTC9D9DCDQAEASBYBCCKBFA'

    with self.assertRaises(TypeError):
      trytes == bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA')

    # Identity comparison still works though.
    self.assertFalse(trytes is b'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertFalse(trytes is bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))

  def test_init_error_odd_length(self):
    """
    Attempting to create a TryteString from a sequence with length not
      divisible by 2.
    """
    with self.assertRaises(ValueError):
      TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA9')
