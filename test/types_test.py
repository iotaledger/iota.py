# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from six import binary_type, text_type

from iota import Address, AddressChecksum, AsciiTrytesCodec, Hash, Tag, \
  TryteString, TrytesDecodeError


# noinspection SpellCheckingInspection
class TryteStringTestCase(TestCase):
  def test_ascii_bytes(self):
    """
    Getting an ASCII representation of a TryteString, as bytes.
    """
    self.assertEqual(
      binary_type(TryteString(b'HELLOIOTA')),
      b'HELLOIOTA',
    )

  def test_ascii_str(self):
    """
    Getting an ASCII representation of a TryteString, as a unicode
    string.
    """
    self.assertEqual(
      text_type(TryteString(b'HELLOIOTA')),
      'HELLOIOTA',
    )

  def test_comparison(self):
    """
    Comparing TryteStrings for equality.
    """
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

    # Comparing against strings is also allowed.
    self.assertTrue(trytes1 == b'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertFalse(trytes1 != b'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertFalse(trytes3 == b'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertTrue(trytes3 != b'RBTC9D9DCDQAEASBYBCCKBFA')

    self.assertTrue(trytes1 == 'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertFalse(trytes1 != 'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertFalse(trytes3 == 'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertTrue(trytes3 != 'RBTC9D9DCDQAEASBYBCCKBFA')

    # Ditto for bytearrays.
    self.assertTrue(trytes1 == bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))
    self.assertFalse(trytes1 != bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))
    self.assertFalse(trytes3 == bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))
    self.assertTrue(trytes3 != bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))

  # noinspection PyTypeChecker
  def test_comparison_error_wrong_type(self):
    """
    Attempting to compare a TryteString with something that is not a
    TrytesCompatible.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    with self.assertRaises(TypeError):
      # TryteString is not a numeric type, so comparing against a
      # numeric value doesn't make any sense.
      # noinspection PyStatementEffect
      trytes == 42

    # Identity comparison still works though.
    self.assertFalse(trytes is 'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertTrue(trytes is not 'RBTC9D9DCDQAEASBYBCCKBFA')

  def test_bool_cast(self):
    """
    Casting a TryteString as a boolean.
    """
    # Empty TryteString evaluates to False.
    self.assertIs(bool(TryteString(b'')), False)

    # TryteString that is nothing but padding also evaluates to False.
    self.assertIs(bool(TryteString(b'9')), False)
    self.assertIs(bool(TryteString(b'', pad=1024)), False)

    # A single non-padding tryte evaluates to True.
    self.assertIs(bool(TryteString(b'A')), True)
    self.assertIs(bool(TryteString(b'9'*1024 + b'Z')), True)

  def test_container(self):
    """
    Checking whether a TryteString contains a sequence.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    self.assertTrue(trytes in trytes)
    self.assertTrue(TryteString(b'RBTC9D') in trytes)
    self.assertTrue(TryteString(b'DQAEAS') in trytes)
    self.assertTrue(TryteString(b'CCKBFA') in trytes)

    self.assertFalse(TryteString(b'9RBTC9D9DCDQAEASBYBCCKBFA') in trytes)
    self.assertFalse(TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA9') in trytes)
    self.assertFalse(TryteString(b'RBTC9D9DCDQA9EASBYBCCKBFA') in trytes)
    self.assertFalse(TryteString(b'X') in trytes)

    # Any TrytesCompatible value will work here.
    self.assertTrue(b'EASBY' in trytes)
    self.assertTrue('EASBY' in trytes)
    self.assertFalse(b'QQQ' in trytes)
    self.assertFalse('QQQ' in trytes)
    self.assertTrue(bytearray(b'CCKBF') in trytes)
    self.assertFalse(bytearray(b'ZZZ') in trytes)

  def test_container_error_wrong_type(self):
    """
    Checking whether a TryteString contains a sequence with an
    incompatible type.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    with self.assertRaises(TypeError):
      # TryteString is not a numeric type, so this makes about as much
      # sense as ``16 in b'Hello, world!'``.
      # noinspection PyStatementEffect,PyTypeChecker
      16 in trytes

    with self.assertRaises(TypeError):
      # This is too ambiguous.  Is this a list of trit values that can
      # appar anywhere in the tryte sequence, or does it have to match
      # a tryte exactly?
      # noinspection PyStatementEffect,PyTypeChecker
      [0, 1, 1, 0, -1, 0] in trytes

    with self.assertRaises(TypeError):
      # This makes more sense than the previous example, but for
      # consistency, we will not allow checking for trytes inside
      # of a TryteString.
      # noinspection PyStatementEffect,PyTypeChecker
      [[0, 0, 0], [1, 1, 0]] in trytes

    with self.assertRaises(TypeError):
      # Did I miss something? When did we get to DisneyLand?
      # noinspection PyStatementEffect,PyTypeChecker
      None in trytes

  def test_concatenation(self):
    """
    Concatenating TryteStrings with TrytesCompatibles.
    """
    trytes1 = TryteString(b'RBTC9D9DCDQA')
    trytes2 = TryteString(b'EASBYBCCKBFA')

    concat = trytes1 + trytes2
    self.assertIsInstance(concat, TryteString)
    self.assertEqual(binary_type(concat), b'RBTC9D9DCDQAEASBYBCCKBFA')

    # You can also concatenate a TryteString with any TrytesCompatible.
    self.assertEqual(
      binary_type(trytes1 + b'EASBYBCCKBFA'),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

    self.assertEqual(
      binary_type(trytes1 + 'EASBYBCCKBFA'),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

    self.assertEqual(
      binary_type(trytes1 + bytearray(b'EASBYBCCKBFA')),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_concatenation_error_wrong_type(self):
    """
    Attempting to concatenate a TryteString with something that is not
    a TrytesCompatible.
    """
    trytes = TryteString(b'RBTC9D9DCDQA')

    with self.assertRaises(TypeError):
      # TryteString is not a numeric type, so adding a numeric value
      # doesn't make any sense.
      trytes += 42

    with self.assertRaises(TypeError):
      # What is this I don't even..
      trytes += None

  def test_slice_accessor(self):
    """
    Taking slices of a TryteString.
    """
    ts = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    self.assertEqual(ts[4], TryteString(b'9'))
    self.assertEqual(ts[:4], TryteString(b'RBTC'))
    self.assertEqual(ts[:-4], TryteString(b'RBTC9D9DCDQAEASBYBCC'))
    self.assertEqual(ts[4:], TryteString(b'9D9DCDQAEASBYBCCKBFA'))
    self.assertEqual(ts[-4:], TryteString(b'KBFA'))
    self.assertEqual(ts[4:-4:4], TryteString(b'9CEY'))

    with self.assertRaises(IndexError):
      # noinspection PyStatementEffect
      ts[42]

    # To match the behavior of built-in types, TryteString will allow
    # you to access a slice that occurs after the end of the sequence.
    # There's nothing in it, of course, but you can access it.
    self.assertEqual(ts[42:43], TryteString(b''))

  def test_slice_mutator(self):
    """
    Modifying slices of a TryteString.
    """
    ts = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    ts[4] = TryteString(b'A')
    self.assertEqual(ts, TryteString(b'RBTCAD9DCDQAEASBYBCCKBFA'))

    ts[:4] = TryteString(b'BCDE')
    self.assertEqual(ts, TryteString(b'BCDEAD9DCDQAEASBYBCCKBFA'))

    # The lengths do not have to be the same...
    ts[:-4] = TryteString(b'EFGHIJ')
    self.assertEqual(ts, TryteString(b'EFGHIJKBFA'))

    # ... unless you are trying to set a single tryte.
    with self.assertRaises(ValueError):
      ts[4] = TryteString(b'99')

    # Any TrytesCompatible value will work.
    ts[3:-3] = b'FOOBAR'
    self.assertEqual(ts, TryteString(b'EFGFOOBARBFA'))

    # I have no idea why you would ever need to do this, but I'm not
    # going to judge, either.
    ts[2:-2:2] = b'IOTA'
    self.assertEqual(ts, TryteString(b'EFIFOOTAABFA'))

    with self.assertRaises(IndexError):
      ts[42] = b'9'

    # To match the behavior of built-in types, TryteString will allow
    # you to modify a slice that occurs after the end of the sequence.
    ts[42:43] = TryteString(b'9')
    self.assertEqual(ts, TryteString(b'EFIFOOTAABFA9'))

  def test_iter_chunks(self):
    """
    Iterating over a TryteString in constant-size chunks.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    self.assertListEqual(
      list(trytes.iter_chunks(9)),

      [
        TryteString(b'RBTC9D9DC'),
        TryteString(b'DQAEASBYB'),
        # The final chunk is padded as necessary.
        TryteString(b'CCKBFA999'),
      ],
    )

  def test_init_from_unicode_string(self):
    """
    Initializing a TryteString from a unicode string.
    """
    trytes1 = TryteString('RBTC9D9DCDQAEASBYBCCKBFA')
    trytes2 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    self.assertEqual(trytes1, trytes2)

  def test_init_from_unicode_string_error_not_ascii(self):
    """
    Attempting to initialize a TryteString from a unicode string that
    contains non-ASCII characters.
    """
    with self.assertRaises(UnicodeEncodeError):
      TryteString('¡Hola, IOTA!')

  def test_init_from_tryte_string(self):
    """
    Initializing a TryteString from another TryteString.
    """
    trytes1 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')
    trytes2 = TryteString(trytes1)

    self.assertFalse(trytes1 is trytes2)
    self.assertTrue(trytes1 == trytes2)

  def test_init_from_tryte_string_error_wrong_subclass(self):
    """
    Initializing a TryteString from a conflicting subclass instance.

    This restriction does not apply when initializing a TryteString
    instance; only subclasses.
    """
    tag = Tag(b'RBTC9D9DCDQAEASBYBCCKBFA')

    with self.assertRaises(TypeError):
      # When initializing a subclassed TryteString, you have to use the
      # same type (or a generic TryteString).
      Address(tag)

    # If you are 110% confident that you know what you are doing, you
    # can force the conversion by casting as a generic TryteString
    # first.
    addy = Address(TryteString(tag))

    self.assertEqual(
      binary_type(addy),

      b'RBTC9D9DCDQAEASBYBCCKBFA9999999999999999'
      b'99999999999999999999999999999999999999999',
    )

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
    Attempting to reset a TryteString with a value that contains
    invalid characters.
    """
    with self.assertRaises(ValueError):
      TryteString(b'not valid')

  # noinspection PyTypeChecker
  def test_init_error_int(self):
    """
    Attempting to reset a TryteString from an int.
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

  def test_as_string(self):
    """
    Converting a sequence of trytes into a Unicode string.
    """
    trytes = TryteString(b'LH9GYEMHCF9GWHZFEELHVFOEOHNEEEWHZFUD')

    self.assertEqual(trytes.as_string(), '你好，世界！')

  def test_as_string_strip(self):
    """
    Strip trailing padding from a TryteString before converting.
    """
    # Note odd number of trytes!
    trytes = TryteString(b'LH9GYEMHCF9GWHZFEELHVFOEOHNEEEWHZFUD9999999999999')

    self.assertEqual(trytes.as_string(), '你好，世界！')

  def test_as_string_no_strip(self):
    """
    Prevent stripping trailing padding when converting to string.
    """
    trytes = TryteString(b'LH9GYEMHCF9GWHZFEELHVFOEOHNEEEWHZFUD999999999999')

    self.assertEqual(
      trytes.as_string(strip_padding=False),
      '你好，世界！\x00\x00\x00\x00\x00\x00',
    )

  def test_as_string_not_utf8_errors_strict(self):
    """
    The tryte sequence does not represent a valid UTF-8 sequence, and
    errors='strict'.
    """
    # Chop off a couple of trytes to break up a multi-byte sequence.
    trytes = TryteString.from_string('你好，世界！')[:-2]

    # Note the exception type.  The trytes were decoded to bytes
    # successfully; the exception occurred while trying to decode the
    # bytes into Unicode code points.
    with self.assertRaises(UnicodeDecodeError):
      trytes.as_string('strict')

  def test_as_string_not_utf8_errors_ignore(self):
    """
    The tryte sequence does not represent a valid UTF-8 sequence, and
    errors='ignore'.
    """
    # Chop off a couple of trytes to break up a multi-byte sequence.
    trytes = TryteString.from_string('你好，世界！')[:-2]

    self.assertEqual(
      trytes.as_string('ignore'),
      '你好，世界',
    )

  def test_as_string_not_utf8_errors_replace(self):
    """
    The tryte sequence does not represent a valid UTF-8 sequence, and
    errors='replace'.
    """
    # Chop off a couple of trytes to break up a multi-byte sequence.
    trytes = TryteString.from_string('你好，世界！')[:-2]

    self.assertEqual(
      trytes.as_string('replace'),

      # Note that the replacement character is the Unicode replacement
      # character, not '?'.
      '你好，世界�',
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
          for c in AsciiTrytesCodec.alphabet.values()
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
          for c in AsciiTrytesCodec.alphabet.values()
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

  def test_random(self):
    """
    Generating a random sequence of trytes.
    """
    trytes = TryteString.random(Hash.LEN)

    # It is (hopefully!) impossible to predict what the actual trytes
    # will be, but at least we can verify that the correct number were
    # generated!
    self.assertEqual(len(trytes), Hash.LEN)

  def test_from_bytes(self):
    """
    Converting a sequence of bytes into a TryteString.
    """
    self.assertEqual(
      binary_type(TryteString.from_bytes(b'Hello, IOTA!')),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_from_string(self):
    """
    Converting a Unicode string into a TryteString.
    """
    self.assertEqual(
      binary_type(TryteString.from_string('你好，世界！')),
      b'LH9GYEMHCF9GWHZFEELHVFOEOHNEEEWHZFUD',
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
      binary_type(TryteString.from_trits(trits)),
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
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999',
    )

    # This attribute will make more sense once we start working with
    # address checksums.
    self.assertEqual(
      binary_type(addy.address),

      b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999',
    )

    # Checksum is not generated automatically.
    self.assertIsNone(addy.checksum)

  def test_init_error_too_long(self):
    """
    Attempting to create an address longer than 81 trytes.
    """
    with self.assertRaises(ValueError):
      Address(
        # Extra padding at the end is not ignored.
        # If it's an address (without checksum), then it must be 81
        # trytes exactly.
        b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
        b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC99999'
      )

  def test_init_with_checksum(self):
    """
    Creating an address with checksum already attached.
    """
    addy = Address(
      b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
      b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVAFOXM9MUBX'
    )

    self.assertEqual(
      binary_type(addy),

      b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
      b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVAFOXM9MUBX',
    )

    self.assertEqual(
      binary_type(addy.address),

      b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
      b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVA',
    )

    self.assertEqual(
      binary_type(addy.checksum),
      b'FOXM9MUBX',
    )

  def test_init_error_checksum_too_long(self):
    """
    Attempting to create an address longer than 90 trytes.
    """
    with self.assertRaises(ValueError):
      Address(
        # Extra padding at the end is not ignored.
        # If it's a checksummed address, then it must be 90 trytes
        # exactly.
        b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
        b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVAFOXM9MUBX9'
      )

  def test_checksum_valid(self):
    """
    An address is created with a valid checksum.
    """
    addy = Address(
      b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
      b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVAITCOXAQSD',
    )

    self.assertTrue(addy.is_checksum_valid())

    self.assertEqual(
      binary_type(addy.with_valid_checksum()),

      b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
      b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVAITCOXAQSD',
    )

  def test_checksum_invalid(self):
    """
    An address is created with an invalid checksum.
    """
    trytes = (
      b'IGKUOZGEFNSVJXETLIBKRSUZAWMYSVDPMHGQPCETEFNZP'
      b'XSJLZMBLAWDRLUBWPIPKFNEPADIWMXMYYRKQ'
    )

    addy = Address(
      trytes + b'XYYNAFRMB' # <- Last tryte s/b 'A'.
    )

    self.assertFalse(addy.is_checksum_valid())

    self.assertEqual(
      binary_type(addy.with_valid_checksum()),

      b'IGKUOZGEFNSVJXETLIBKRSUZAWMYSVDPMHGQPCETEFNZP'
      b'XSJLZMBLAWDRLUBWPIPKFNEPADIWMXMYYRKQXYYNAFRMA',
    )

  def test_checksum_null(self):
    """
    An address is created without a checksum.
    """
    trytes = (
      b'ZKIUDZXQYQAWSHPKSAATJXPAQZPGYCDCQDRSMWWCGQJNI'
      b'PCOORMDRNREDUDKBMUYENYTFVUNEWDBAKXMV'
    )

    addy = Address(trytes)

    self.assertFalse(addy.is_checksum_valid())

    self.assertEqual(
      binary_type(addy.with_valid_checksum()),

      b'ZKIUDZXQYQAWSHPKSAATJXPAQZPGYCDCQDRSMWWCGQJNI'
      b'PCOORMDRNREDUDKBMUYENYTFVUNEWDBAKXMVJJJGBARPB',
    )

  def test_with_checksum_attributes(self):
    """
    :py:meth:`Address.with_valid_checksum` also copies attributes such
    as key index and balance.
    """
    addy =\
      Address(
        trytes =
          b'ZKIUDZXQYQAWSHPKSAATJXPAQZPGYCDCQDRSMWWCGQJNI'
          b'PCOORMDRNREDUDKBMUYENYTFVUNEWDBAKXMV',

        key_index = 42,
        balance   = 86,
      )

    checked = addy.with_valid_checksum()

    self.assertEqual(checked.key_index, 42)
    self.assertEqual(checked.balance, 86)


# noinspection SpellCheckingInspection
class AddressChecksumTestCase(TestCase):
  def test_init_happy_path(self):
    """
    Creating a valid address checksum.
    """
    self.assertEqual(binary_type(AddressChecksum(b'FOXM9MUBX')), b'FOXM9MUBX')

  def test_init_error_too_short(self):
    """
    Attempting to create an address checksum shorter than 9 trytes.
    """
    with self.assertRaises(ValueError):
      AddressChecksum(b'FOXM9MUB')

  def test_init_error_too_long(self):
    """
    Attempting to create an address checksum longer than 9 trytes.
    """
    with self.assertRaises(ValueError):
      # Extra padding characters are not ignored.
      # If it's an address checksum, it must be 9 trytes exactly.
      AddressChecksum(b'FOXM9MUBX9')


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
