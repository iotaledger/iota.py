# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from codecs import decode, encode
from unittest import TestCase
from warnings import catch_warnings, simplefilter as simple_filter

from six import text_type

from iota.codecs import AsciiTrytesCodec, TrytesDecodeError


# noinspection SpellCheckingInspection
class AsciiTrytesCodecTestCase(TestCase):
  def test_encode_byte_string(self):
    """
    Encoding a byte string into trytes.
    """
    self.assertEqual(
      encode(b'Hello, IOTA!', AsciiTrytesCodec.name),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_encode_bytearray(self):
    """
    Encoding a bytearray into trytes.
    """
    self.assertEqual(
      encode(bytearray(b'Hello, IOTA!'), AsciiTrytesCodec.name),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_encode_error_wrong_type(self):
    """
    Attempting to encode a value with an incompatible type.
    """
    with self.assertRaises(TypeError):
      # List value not accepted; it can contain things other than bytes
      # (ordinals in range(255), that is).
      encode(
        [72, 101, 108, 108, 111, 44, 32, 73, 79, 84, 65, 33],
        AsciiTrytesCodec.name,
      )

    with self.assertRaises(TypeError):
      # Unicode strings not accepted; it is ambiguous whether and how
      #   to encode to bytes.
      encode('Hello, IOTA!', AsciiTrytesCodec.name)

  def test_decode_byte_string(self):
    """
    Decoding trytes to a byte string.
    """
    self.assertEqual(
      decode(b'RBTC9D9DCDQAEASBYBCCKBFA', AsciiTrytesCodec.name),
      b'Hello, IOTA!',
    )

  def test_decode_bytearray(self):
    """
    Decoding a bytearray of trytes into a byte string.
    """
    self.assertEqual(
      decode(bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'), AsciiTrytesCodec.name),
      b'Hello, IOTA!',
    )

  def test_decode_wrong_length_errors_strict(self):
    """
    Attempting to decode an odd number of trytes with errors='strict'.
    """
    with self.assertRaises(TrytesDecodeError):
      decode(b'RBTC9D9DCDQAEASBYBCCKBFA9', AsciiTrytesCodec.name, 'strict')

  def test_decode_wrong_length_errors_ignore(self):
    """
    Attempting to decode an odd number of trytes with errors='ignore'.
    """
    self.assertEqual(
      decode(b'RBTC9D9DCDQAEASBYBCCKBFA9', AsciiTrytesCodec.name, 'ignore'),
      b'Hello, IOTA!',
    )

  def test_decode_wrong_length_errors_replace(self):
    """
    Attempting to decode an odd number of trytes with errors='replace'.
    """
    self.assertEqual(
      decode(b'RBTC9D9DCDQAEASBYBCCKBFA9', AsciiTrytesCodec.name, 'replace'),
      b'Hello, IOTA!?',
    )

  def test_decode_invalid_pair_errors_strict(self):
    """
    Attempting to decode an un-decodable pair of trytes with
    errors='strict'.
    """
    with self.assertRaises(TrytesDecodeError):
      decode(b'ZJVYUGTDRPDYFGFXMK', AsciiTrytesCodec.name, 'strict')

  def test_decode_invalid_pair_errors_ignore(self):
    """
    Attempting to decode an un-decodable pair of trytes with
    errors='ignore'.
    """
    self.assertEqual(
      decode(b'ZJVYUGTDRPDYFGFXMK', AsciiTrytesCodec.name, 'ignore'),
      b'\xd2\x80\xc3',
    )

  def test_decode_invalid_pair_errors_replace(self):
    """
    Attempting to decode an un-decodable pair of trytes with
    errors='replace'.
    """
    self.assertEqual(
      decode(b'ZJVYUGTDRPDYFGFXMK', AsciiTrytesCodec.name, 'replace'),
      b'??\xd2\x80??\xc3??',
    )

  def test_compat_name(self):
    """
    A warning is raised when using the codec's old name.
    """
    with catch_warnings(record=True) as warnings:
      simple_filter('always', category=DeprecationWarning)

      self.assertEqual(
        # Provide the old codec name to :py:func:`encode`.
        encode(b'Hello, IOTA!', AsciiTrytesCodec.compat_name),
        b'RBTC9D9DCDQAEASBYBCCKBFA',
      )

    self.assertEqual(len(warnings), 1)
    self.assertEqual(warnings[0].category, DeprecationWarning)
    self.assertIn('codec will be removed', text_type(warnings[0].message))
