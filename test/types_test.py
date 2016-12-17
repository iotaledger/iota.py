# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import TrytesDecodeError
from iota.types import Address, Tag, TransactionId, TryteString
from six import binary_type


# noinspection SpellCheckingInspection
class TryteStringTestCase(TestCase):
  def test_from_bytes(self):
    """
    Converting a sequence of bytes into a TryteString.
    """
    self.assertEqual(
      binary_type(TryteString.from_bytes(b'Hello, IOTA!')),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

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
    self.assertListEqual(TryteString(b'9').as_trytes(), [[ 0,  0,  0]])
    self.assertListEqual(TryteString(b'A').as_trytes(), [[ 1,  0,  0]])
    self.assertListEqual(TryteString(b'B').as_trytes(), [[-1,  1,  0]])
    self.assertListEqual(TryteString(b'C').as_trytes(), [[ 0,  1,  0]])
    self.assertListEqual(TryteString(b'D').as_trytes(), [[ 1,  1,  0]])
    self.assertListEqual(TryteString(b'E').as_trytes(), [[-1, -1,  1]])
    self.assertListEqual(TryteString(b'F').as_trytes(), [[ 0, -1,  1]])
    self.assertListEqual(TryteString(b'G').as_trytes(), [[ 1, -1,  1]])
    self.assertListEqual(TryteString(b'H').as_trytes(), [[-1,  0,  1]])
    self.assertListEqual(TryteString(b'I').as_trytes(), [[ 0,  0,  1]])
    self.assertListEqual(TryteString(b'J').as_trytes(), [[ 1,  0,  1]])
    self.assertListEqual(TryteString(b'K').as_trytes(), [[-1,  1,  1]])
    self.assertListEqual(TryteString(b'L').as_trytes(), [[ 0,  1,  1]])
    self.assertListEqual(TryteString(b'M').as_trytes(), [[ 1,  1,  1]])
    self.assertListEqual(TryteString(b'N').as_trytes(), [[-1, -1, -1]])
    self.assertListEqual(TryteString(b'O').as_trytes(), [[ 0, -1, -1]])
    self.assertListEqual(TryteString(b'P').as_trytes(), [[ 1, -1, -1]])
    self.assertListEqual(TryteString(b'Q').as_trytes(), [[-1,  0, -1]])
    self.assertListEqual(TryteString(b'R').as_trytes(), [[ 0,  0, -1]])
    self.assertListEqual(TryteString(b'S').as_trytes(), [[ 1,  0, -1]])
    self.assertListEqual(TryteString(b'T').as_trytes(), [[-1,  1, -1]])
    self.assertListEqual(TryteString(b'U').as_trytes(), [[ 0,  1, -1]])
    self.assertListEqual(TryteString(b'V').as_trytes(), [[ 1,  1, -1]])
    self.assertListEqual(TryteString(b'W').as_trytes(), [[-1, -1,  0]])
    self.assertListEqual(TryteString(b'X').as_trytes(), [[ 0, -1,  0]])
    self.assertListEqual(TryteString(b'Y').as_trytes(), [[ 1, -1,  0]])
    self.assertListEqual(TryteString(b'Z').as_trytes(), [[-1,  0,  0]])

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
    self.assertListEqual(TryteString(b'9').as_trits(), [ 0,  0,  0])
    self.assertListEqual(TryteString(b'A').as_trits(), [ 1,  0,  0])
    self.assertListEqual(TryteString(b'B').as_trits(), [-1,  1,  0])
    self.assertListEqual(TryteString(b'C').as_trits(), [ 0,  1,  0])
    self.assertListEqual(TryteString(b'D').as_trits(), [ 1,  1,  0])
    self.assertListEqual(TryteString(b'E').as_trits(), [-1, -1,  1])
    self.assertListEqual(TryteString(b'F').as_trits(), [ 0, -1,  1])
    self.assertListEqual(TryteString(b'G').as_trits(), [ 1, -1,  1])
    self.assertListEqual(TryteString(b'H').as_trits(), [-1,  0,  1])
    self.assertListEqual(TryteString(b'I').as_trits(), [ 0,  0,  1])
    self.assertListEqual(TryteString(b'J').as_trits(), [ 1,  0,  1])
    self.assertListEqual(TryteString(b'K').as_trits(), [-1,  1,  1])
    self.assertListEqual(TryteString(b'L').as_trits(), [ 0,  1,  1])
    self.assertListEqual(TryteString(b'M').as_trits(), [ 1,  1,  1])
    self.assertListEqual(TryteString(b'N').as_trits(), [-1, -1, -1])
    self.assertListEqual(TryteString(b'O').as_trits(), [ 0, -1, -1])
    self.assertListEqual(TryteString(b'P').as_trits(), [ 1, -1, -1])
    self.assertListEqual(TryteString(b'Q').as_trits(), [-1,  0, -1])
    self.assertListEqual(TryteString(b'R').as_trits(), [ 0,  0, -1])
    self.assertListEqual(TryteString(b'S').as_trits(), [ 1,  0, -1])
    self.assertListEqual(TryteString(b'T').as_trits(), [-1,  1, -1])
    self.assertListEqual(TryteString(b'U').as_trits(), [ 0,  1, -1])
    self.assertListEqual(TryteString(b'V').as_trits(), [ 1,  1, -1])
    self.assertListEqual(TryteString(b'W').as_trits(), [-1, -1,  0])
    self.assertListEqual(TryteString(b'X').as_trits(), [ 0, -1,  0])
    self.assertListEqual(TryteString(b'Y').as_trits(), [ 1, -1,  0])
    self.assertListEqual(TryteString(b'Z').as_trits(), [-1,  0,  0])

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
