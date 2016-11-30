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

  def test_init_padding(self):
    """Apply padding to ensure a TryteString has a minimum length."""
    trytes = TryteString(
      trytes =
        b'ZJVYUGTDRPDYFGFXMKOTV9ZWSGFK9CFPXTITQL'
        b'QNLPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY',

      pad = 81,
    )

    self.assertEqual(
      trytes.trytes,

      # Note the additional Tryte([-1, -1, -1]) values appended to the
      #   end of the sequence (represented in ASCII as '9').
      b'ZJVYUGTDRPDYFGFXMKOTV9ZWSGFK9CFPXTITQLQN'
      b'LPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY9999'
    )
