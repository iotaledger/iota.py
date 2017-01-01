# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from codecs import encode, decode
from unittest import TestCase


# noinspection SpellCheckingInspection
from iota.codecs import TrytesDecodeError


# noinspection SpellCheckingInspection
class TrytesCodecTestCase(TestCase):
  def test_encode_byte_string(self):
    """Encoding a byte string into trytes."""
    self.assertEqual(
      encode(b'Hello, IOTA!', 'trytes'),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_encode_bytearray(self):
    """Encoding a bytearray into trytes."""
    self.assertEqual(
      encode(bytearray(b'Hello, IOTA!'), 'trytes'),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_encode_error_wrong_type(self):
    """Attempting to encode a value with an incompatible type."""
    with self.assertRaises(TypeError):
      # List value not accepted; it can contain things other than bytes
      #   (ordinals in range(255), that is).
      encode([72, 101, 108, 108, 111, 44, 32, 73, 79, 84, 65, 33], 'trytes')

    with self.assertRaises(TypeError):
      # Unicode strings not accepted; it is ambiguous whether and how
      #   to encode to bytes.
      encode('Hello, IOTA!', 'trytes')

  def test_decode_byte_string(self):
    """Decoding trytes to a byte string."""
    self.assertEqual(
      decode(b'RBTC9D9DCDQAEASBYBCCKBFA', 'trytes'),
      b'Hello, IOTA!',
    )

  def test_decode_bytearray(self):
    """Decoding a bytearray of trytes into a byte string."""
    self.assertEqual(
      decode(bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'), 'trytes'),
      b'Hello, IOTA!',
    )

  def test_decode_wrong_length_errors_strict(self):
    """
    Attempting to decode an odd number of trytes with errors='strict'.
    """
    with self.assertRaises(TrytesDecodeError):
      decode(b'RBTC9D9DCDQAEASBYBCCKBFA9', 'trytes', 'strict')

  def test_decode_wrong_length_errors_ignore(self):
    """
    Attempting to decode an odd number of trytes with errors='ignore'.
    """
    self.assertEqual(
      decode(b'RBTC9D9DCDQAEASBYBCCKBFA9', 'trytes', 'ignore'),
      b'Hello, IOTA!',
    )

  def test_decode_wrong_length_errors_replace(self):
    """
    Attempting to decode an odd number of trytes with errors='replace'.
    """
    self.assertEqual(
      decode(b'RBTC9D9DCDQAEASBYBCCKBFA9', 'trytes', 'replace'),
      b'Hello, IOTA!?',
    )

  def test_decode_invalid_pair_errors_strict(self):
    """
    Attempting to decode an un-decodable pair of trytes with
      errors='strict'.
    """
    with self.assertRaises(TrytesDecodeError):
      decode(b'ZJVYUGTDRPDYFGFXMK', 'trytes', 'strict')

  def test_decode_invalid_pair_errors_ignore(self):
    """
    Attempting to decode an un-decodable pair of trytes with
      errors='ignore'.
    """
    self.assertEqual(
      decode(b'ZJVYUGTDRPDYFGFXMK', 'trytes', 'ignore'),
      b'\xd2\x80\xc3',
    )

  def test_decode_invalid_pair_errors_replace(self):
    """
    Attempting to decode an un-decodable pair of trytes with
      errors='replace'.
    """
    self.assertEqual(
      decode(b'ZJVYUGTDRPDYFGFXMK', 'trytes', 'replace'),
      b'??\xd2\x80??\xc3??',
    )
