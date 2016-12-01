# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from codecs import encode, decode
from typing import Text, Union

from six import PY2, binary_type

from iota import TrytesCodec


class TryteString(object):
  """
  A string representation of a sequence of trytes.

  A trit can be thought of as the ternary version of a bit.  It can
    have one of three values:  1, 0 or unknown.

  A tryte can be thought of as the ternary version of a byte.  It is a
    sequence of 3 trits.

  A tryte string is similar in concept to Python's byte string, except
    it has a more limited alphabet.  Byte strings are limited to ASCII
    (256 possible values), while the tryte string alphabet only has
    27 characters (one for each possible tryte configuration).
  """
  @classmethod
  def from_bytes(cls, bytes_):
    # type: (Union[binary_type, bytearray]) -> TryteString
    """Creates a TryteString from a byte string."""
    return cls(encode(bytes_, 'trytes'))

  def __init__(self, trytes, pad=None):
    # type: (Union[binary_type, bytearray, TryteString], int) -> None
    """
    :param trytes: Byte string or bytearray.
    :param pad: Ensure at least this many trytes.
      If there are too few, additional Tryte([-1, -1, -1]) values
        will be appended to the TryteString.

      Note:  If the TryteString is too long, it will _not_ be
        truncated!
    """
    super(TryteString, self).__init__()

    if isinstance(trytes, TryteString):
      # Create a copy of the incoming TryteString's trytes, to ensure
      #   we don't modify it when we apply padding.
      trytes = bytearray(trytes.trytes)
    else:
      if not isinstance(trytes, bytearray):
        trytes = bytearray(trytes)

      for i, ordinal in enumerate(trytes):
        if ordinal not in TrytesCodec.index:
          raise ValueError(
            'Invalid character {char} at position {i} '
            '(expected A-Z or 9).'.format(
              char  = chr(ordinal),
              i     = i,
            ),
          )

    if pad:
      trytes += b'9' * max(0, pad - len(trytes))

    self.trytes = trytes

  def __repr__(self):
    # type: () -> Text
    return 'TryteString({trytes!r})'.format(trytes=binary_type(self.trytes))

  def __bytes__(self):
    # type: () -> Text
    """
    Converts the TryteString into a byte string.

    If the value contains any trytes that can't be converted, they will
      be replaced with '?'.

    If you want different handling of un-convertible trytes, use
      `as_bytes` instead.
    """
    return self.as_bytes()

  # :bc: Magic method has a different name in Python 2.
  if PY2:
    __str__ = __bytes__

  def as_bytes(self, errors='strict'):
    # type: (Text) -> binary_type
    """
    Converts the TryteString into a byte string.

    :param errors: How to handle trytes that can't be converted:
      - 'strict':   raise a TrytesDecodeError.
      - 'replace':  replace with '?'.
      - 'ignore':   omit the tryte from the byte string.
    """
    # :bc: In Python 2, `decode` does not accept keyword arguments.
    return decode(self.trytes, 'trytes', errors)

  def __eq__(self, other):
    # type: (TryteString) -> bool
    if not isinstance(other, TryteString):
      raise TypeError(
        'TryteStrings can only be compared to other TryteStrings.',
      )

    return self.trytes == other.trytes

  # :bc: In Python 2 this must be defined explicitly.
  def __ne__(self, other):
    # type: (TryteString) -> bool
    return not (self == other)


class TransactionId(TryteString):
  """A TryteString that acts as a transaction ID."""
  def __init__(self, trytes):
    super(TransactionId, self).__init__(trytes, pad=81)

    if len(self.trytes) > 81:
      raise ValueError('TransactionIds must be 81 trytes long.')
