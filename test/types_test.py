# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import (
  Address,
  Tag,
  TransactionId,
  TryteString,
  TrytesCodec,
  TrytesDecodeError,
)
from six import binary_type


# noinspection SpellCheckingInspection
class TryteStringTestCase(TestCase):
  def test_equality_comparison(self):
    """Comparing TryteStrings for equality."""
    trytes1 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')
    trytes2 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')
    trytes3 = TryteString(
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA',
    )

    self.assertTrue(trytes1 == trytes2)
    self.assertFalse(trytes1 != trytes2)

    self.assertFalse(trytes1 == trytes3)
    self.assertTrue(trytes1 != trytes3)

    self.assertTrue(trytes1 is trytes1)
    self.assertFalse(trytes1 is not trytes1)

    self.assertFalse(trytes1 is trytes2)
    self.assertTrue(trytes1 is not trytes2)

    self.assertFalse(trytes1 is trytes3)
    self.assertTrue(trytes1 is not trytes3)

    # Comparing against byte strings is also allowed.
    self.assertTrue(trytes1 == b'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertFalse(trytes1 != b'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertFalse(trytes3 == b'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertTrue(trytes3 != b'RBTC9D9DCDQAEASBYBCCKBFA')

    # Ditto for bytearrays.
    self.assertTrue(trytes1 == bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))
    self.assertFalse(trytes1 != bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))
    self.assertFalse(trytes3 == bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))
    self.assertTrue(trytes3 != bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))

  # noinspection PyTypeChecker
  def test_equality_comparison_error_wrong_type(self):
    """
    Attempting to compare a TryteString with something that is not a
    TryteString.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    with self.assertRaises(TypeError):
      # Comparing against unicode strings is not allowed because it is
      # ambiguous how to encode the unicode string for comparison.
      trytes == 'RBTC9D9DCDQAEASBYBCCKBFA'

    with self.assertRaises(TypeError):
      # We might support this at some point, but not at the moment.
      trytes == 42

    # Identity comparison still works though.
    self.assertFalse(trytes is 'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertTrue(trytes is not 'RBTC9D9DCDQAEASBYBCCKBFA')

  def test_init_from_tryte_string(self):
    """
    Initializing a TryteString from another TryteString.
    """
    trytes1 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')
    trytes2 = TryteString(trytes1)

    self.assertFalse(trytes1 is trytes2)
    self.assertTrue(trytes1 == trytes2)

  def test_init_padding(self):
    """
    Apply padding to ensure a TryteString has a minimum length.
    """
    trytes = TryteString(
      trytes =
        b'ZJVYUGTDRPDYFGFXMKOTV9ZWSGFK9CFPXTITQL'
        b'QNLPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY',

      pad = 81,
    )

    self.assertEqual(
      binary_type(trytes),

      # Note the additional Tryte([-1, -1, -1]) values appended to the
      #   end of the sequence (represented in ASCII as '9').
      b'ZJVYUGTDRPDYFGFXMKOTV9ZWSGFK9CFPXTITQLQN'
      b'LPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY9999'
    )

  def test_init_from_tryte_string_with_padding(self):
    """
    Initializing a TryteString from another TryteString, and padding
    the new one to a specific length.
    """
    trytes1 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')
    trytes2 = TryteString(trytes1, pad=27)

    self.assertFalse(trytes1 is trytes2)
    self.assertFalse(trytes1 == trytes2)

    self.assertEqual(binary_type(trytes2), b'RBTC9D9DCDQAEASBYBCCKBFA999')

  def test_init_error_invalid_characters(self):
    """
    Attempting to initialize a TryteString with a value that contains
    invalid characters.
    """
    with self.assertRaises(ValueError):
      TryteString(b'not valid')

  # noinspection PyTypeChecker
  def test_init_error_int(self):
    """
    Attempting to initialize a TryteString from an int.
    """
    with self.assertRaises(TypeError):
      TryteString(42)

  def test_length(self):
    """
    Just like byte strings, TryteStrings have length.
    """
    self.assertEqual(len(TryteString(b'RBTC')), 4)
    self.assertEqual(len(TryteString(b'RBTC', pad=81)), 81)

  def test_iterator(self):
    """
    Just like byte strings, you can iterate over TryteStrings.
    """
    self.assertListEqual(
      list(TryteString(b'RBTC')),
      [b'R', b'B', b'T', b'C'],
    )

    self.assertListEqual(
      list(TryteString(b'RBTC', pad=6)),
      [b'R', b'B', b'T', b'C', b'9', b'9'],
    )

  def test_string_conversion(self):
    """
    A TryteString can be converted into an ASCII representation.
    """
    self.assertEqual(
      binary_type(TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')),

      # Note that the trytes are NOT converted into bytes!
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_as_bytes_partial_sequence_errors_strict(self):
    """
    Attempting to convert an odd number of trytes into bytes using the
    `as_bytes` method with errors='strict'.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA9')

    with self.assertRaises(TrytesDecodeError):
      trytes.as_bytes(errors='strict')

  def test_as_bytes_partial_sequence_errors_ignore(self):
    """
    Attempting to convert an odd number of trytes into bytes using the
    `as_bytes` method with errors='ignore'.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA9')

    self.assertEqual(
      trytes.as_bytes(errors='ignore'),

      # The extra tryte is ignored.
      b'Hello, IOTA!',
    )

  def test_as_bytes_partial_sequence_errors_replace(self):
    """
    Attempting to convert an odd number of trytes into bytes using the
    `as_bytes` method with errors='replace'.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA9')

    self.assertEqual(
      trytes.as_bytes(errors='replace'),

      # The extra tryte is replaced with '?'.
      b'Hello, IOTA!?',
    )

  def test_as_bytes_non_ascii_errors_strict(self):
    """
    Converting a sequence of trytes into bytes using the `as_bytes`
    method yields non-ASCII characters, and errors='strict'.
    """
    trytes = TryteString(b'ZJVYUGTDRPDYFGFXMK')

    with self.assertRaises(TrytesDecodeError):
      trytes.as_bytes(errors='strict')

  def test_as_bytes_non_ascii_errors_ignore(self):
    """
    Converting a sequence of trytes into bytes using the `as_bytes`
    method yields non-ASCII characters, and errors='ignore'.
    """
    trytes = TryteString(b'ZJVYUGTDRPDYFGFXMK')

    self.assertEqual(
      trytes.as_bytes(errors='ignore'),
      b'\xd2\x80\xc3',
    )

  def test_as_bytes_non_ascii_errors_replace(self):
    """
    Converting a sequence of trytes into bytes using the `as_bytes`
    method yields non-ASCII characters, and errors='replace'.
    """
    trytes = TryteString(b'ZJVYUGTDRPDYFGFXMK')

    self.assertEqual(
      trytes.as_bytes(errors='replace'),
      b'??\xd2\x80??\xc3??',
    )

  def test_as_trytes_single_tryte(self):
    """
    Converting a single-tryte TryteString into a sequence of tryte
    values.
    """
    # Fortunately, there's only 27 possible tryte configurations, so
    # it's not too painful to test them all.
    self.assertDictEqual(
      {
        chr(c): TryteString(chr(c).encode('ascii')).as_trytes()
          for c in TrytesCodec.alphabet.values()
      },

      {
        '9': [[ 0,  0,  0]],  #   0
        'A': [[ 1,  0,  0]],  #   1
        'B': [[-1,  1,  0]],  #   2
        'C': [[ 0,  1,  0]],  #   3
        'D': [[ 1,  1,  0]],  #   4
        'E': [[-1, -1,  1]],  #   5
        'F': [[ 0, -1,  1]],  #   6
        'G': [[ 1, -1,  1]],  #   7
        'H': [[-1,  0,  1]],  #   8
        'I': [[ 0,  0,  1]],  #   9
        'J': [[ 1,  0,  1]],  #  10
        'K': [[-1,  1,  1]],  #  11
        'L': [[ 0,  1,  1]],  #  12
        'M': [[ 1,  1,  1]],  #  13
        'N': [[-1, -1, -1]],  # -13 (overflow)
        'O': [[ 0, -1, -1]],  # -12
        'P': [[ 1, -1, -1]],  # -11
        'Q': [[-1,  0, -1]],  # -10
        'R': [[ 0,  0, -1]],  #  -9
        'S': [[ 1,  0, -1]],  #  -8
        'T': [[-1,  1, -1]],  #  -7
        'U': [[ 0,  1, -1]],  #  -6
        'V': [[ 1,  1, -1]],  #  -5
        'W': [[-1, -1,  0]],  #  -4
        'X': [[ 0, -1,  0]],  #  -3
        'Y': [[ 1, -1,  0]],  #  -2
        'Z': [[-1,  0,  0]],  #  -1
      },
    )

  def test_as_trytes_mulitple_trytes(self):
    """
    Converting a multiple-tryte TryteString into a sequence of
    tryte values.
    """
    self.assertListEqual(
      TryteString(b'ZJVYUGTDRPDYFGFXMK').as_trytes(),

      [
        [-1,  0,  0],
        [ 1,  0,  1],
        [ 1,  1, -1],
        [ 1, -1,  0],
        [ 0,  1, -1],
        [ 1, -1,  1],
        [-1,  1, -1],
        [ 1,  1,  0],
        [ 0,  0, -1],
        [ 1, -1, -1],
        [ 1,  1,  0],
        [ 1, -1,  0],
        [ 0, -1,  1],
        [ 1, -1,  1],
        [ 0, -1,  1],
        [ 0, -1,  0],
        [ 1,  1,  1],
        [-1,  1,  1],
      ],
    )

  def test_as_trits_single_tryte(self):
    """
    Converting a single-tryte TryteString into a sequence of trit
    values.
    """
    # Fortunately, there's only 27 possible tryte configurations, so
    # it's not too painful to test them all.
    self.assertDictEqual(
      {
        chr(c): TryteString(chr(c).encode('ascii')).as_trits()
          for c in TrytesCodec.alphabet.values()
      },

      {
        '9': [ 0,  0,  0],  #   0
        'A': [ 1,  0,  0],  #   1
        'B': [-1,  1,  0],  #   2
        'C': [ 0,  1,  0],  #   3
        'D': [ 1,  1,  0],  #   4
        'E': [-1, -1,  1],  #   5
        'F': [ 0, -1,  1],  #   6
        'G': [ 1, -1,  1],  #   7
        'H': [-1,  0,  1],  #   8
        'I': [ 0,  0,  1],  #   9
        'J': [ 1,  0,  1],  #  10
        'K': [-1,  1,  1],  #  11
        'L': [ 0,  1,  1],  #  12
        'M': [ 1,  1,  1],  #  13
        'N': [-1, -1, -1],  # -13 (overflow)
        'O': [ 0, -1, -1],  # -12
        'P': [ 1, -1, -1],  # -11
        'Q': [-1,  0, -1],  # -10
        'R': [ 0,  0, -1],  #  -9
        'S': [ 1,  0, -1],  #  -8
        'T': [-1,  1, -1],  #  -7
        'U': [ 0,  1, -1],  #  -6
        'V': [ 1,  1, -1],  #  -5
        'W': [-1, -1,  0],  #  -4
        'X': [ 0, -1,  0],  #  -3
        'Y': [ 1, -1,  0],  #  -2
        'Z': [-1,  0,  0],  #  -1
      },
    )

  def test_as_trits_multiple_trytes(self):
    """
    Converting a multiple-tryte TryteString into a sequence of trit
    values.
    """
    self.assertListEqual(
      TryteString(b'ZJVYUGTDRPDYFGFXMK').as_trits(),
      [
        -1,  0,  0,
         1,  0,  1,
         1,  1, -1,
         1, -1,  0,
         0,  1, -1,
         1, -1,  1,
        -1,  1, -1,
         1,  1,  0,
         0,  0, -1,
         1, -1, -1,
         1,  1,  0,
         1, -1,  0,
         0, -1,  1,
         1, -1,  1,
         0, -1,  1,
         0, -1,  0,
         1,  1,  1,
        -1,  1,  1,
      ],
    )

  def test_from_bytes(self):
    """
    Converting a sequence of bytes into a TryteString.
    """
    self.assertEqual(
      binary_type(TryteString.from_bytes(b'Hello, IOTA!')),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_from_trytes(self):
    """
    Converting a sequence of tryte values into a TryteString.
    """
    trytes = [
      [0, 0, -1],
      [-1, 1, 0],
      [-1, 1, -1],
      [0, 1, 0],
      [0, 0, 0],
      [1, 1, 0],
      [0, 0, 0],
      [1, 1, 0],
      [0, 1, 0],
      [1, 1, 0],
      [-1, 0, -1],
      [1, 0, 0],
      [-1, -1, 1],
      [1, 0, 0],
      [1, 0, -1],
      [-1, 1, 0],
      [1, -1, 0],
      [-1, 1, 0],
      [0, 1, 0],
      [0, 1, 0],
      [-1, 1, 1],
      [-1, 1, 0],
      [0, -1, 1],
      [1, 0, 0],
    ]

    self.assertEqual(
      binary_type(TryteString.from_trytes(trytes)),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_from_trits(self):
    """
    Converting a sequence of trit values into a TryteString.
    """
    trits = [
      0, 0, -1,
      -1, 1, 0,
      -1, 1, -1,
      0, 1, 0,
      0, 0, 0,
      1, 1, 0,
      0, 0, 0,
      1, 1, 0,
      0, 1, 0,
      1, 1, 0,
      -1, 0, -1,
      1, 0, 0,
      -1, -1, 1,
      1, 0, 0,
      1, 0, -1,
      -1, 1, 0,
      1, -1, 0,
      -1, 1, 0,
      0, 1, 0,
      0, 1, 0,
      -1, 1, 1,
      -1, 1, 0,
      0, -1, 1,
      1, 0, 0,
    ]

    self.assertEqual(
      binary_type(TryteString.from_trits(trits)),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_from_trits_error_wrong_length(self):
    """
    Converting a sequence of trit values with length not divisible by 3
    into a TryteString.
    """
    trits = [
      0, 0, -1,
      -1, 1, 0,
      -1, 1, -1,
      0, 1, # 0, <- Oops, did you lose something?
    ]

    with self.assertRaises(ValueError):
      TryteString.from_trits(trits)

  def test_from_trits_wrong_length_padded(self):
    """
    Automatically padding a sequence of trit values with length not
    divisible by 3 so that it can be converted into a TryteString.
    """
    trits = [
      0, 0, -1,
      -1, 1, 0,
      -1, 1, -1,
      0, 1, # 0, <- Oops, did you lose something?
    ]

    self.assertEqual(
      binary_type(TryteString.from_trits(trits, pad=True)),
      b'RBTC',
    )


# noinspection SpellCheckingInspection
class AddressTestCase(TestCase):
  def test_init_automatic_pad(self):
    """
    Addresses are automatically padded to 81 trytes.
    """
    addy = Address(
      b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC'
    )

    self.assertEqual(
      binary_type(addy),

      # Note the extra 9's added to the end.
      b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
    )

  def test_init_error_too_long(self):
    """
    Attempting to create an address longer than 81 trytes.
    """
    with self.assertRaises(ValueError):
      Address(
        b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
        b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC99999'
      )


# noinspection SpellCheckingInspection
class TagTestCase(TestCase):
  def test_init_automatic_pad(self):
    """
    Tags are automatically padded to 27 trytes.
    """
    tag = Tag(b'COLOREDCOINS')

    self.assertEqual(binary_type(tag), b'COLOREDCOINS999999999999999')

  def test_init_error_too_long(self):
    """
    Attempting to create a tag longer than 27 trytes.
    """
    with self.assertRaises(ValueError):
      # 28 chars = no va.
      Tag(b'COLOREDCOINS9999999999999999')


# noinspection SpellCheckingInspection
class TransactionIdTestCase(TestCase):
  def test_init_automatic_pad(self):
    """
    Transaction IDs are automatically padded to 81 trytes.
    """
    txn = TransactionId(
      b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC'
    )

    self.assertEqual(
      binary_type(txn),

      # Note the extra 9's added to the end.
      b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
    )

  def test_init_error_too_long(self):
    """
    Attempting to create a transaction ID longer than 81 trytes.
    """
    with self.assertRaises(ValueError):
      TransactionId(
        b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
        b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC99999'
      )
