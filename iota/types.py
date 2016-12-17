# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from codecs import encode, decode
from itertools import chain
from typing import Dict, Generator, Iterable, Optional, Text, Union, List

from six import PY2, binary_type

from iota import TrytesCodec


TrytesCompatible = Union[binary_type, bytearray, 'TryteString']


def trytes_from_int(n):
  # type: (int) -> List[List[int]]
  """
  Returns a tryte representation of an integer value.
  """
  trytes = []

  while True:
    # divmod does weird things if ``n`` is negative.
    # :see: http://stackoverflow.com/q/10063546/
    quotient, remainder = divmod(abs(n), 27)

    sign = -1 if n < 0 else 1
    remainder *= sign
    quotient  *= sign

    if remainder not in _trytes_dict:
      trits = trits_from_int(remainder)
      # Pad the tryte out to 3 trits if necessary.
      trits += [0] * (3 - len(trits))

      _trytes_dict[remainder] = trits

    trytes.append(_trytes_dict[remainder])

    if quotient == 0:
      break

    n = quotient

  return trytes

_trytes_dict = {} # type: Dict[int, List[int]]
"""
Caches tryte values for :py:func:`trytes_from_int`.

There are only 27 possible tryte configurations, so it's a relatively
small amount of memory; the tradeoff is usually worth it for the
reduced CPU load.
"""


def trits_from_int(n):
  # type: (int) -> List[int]
  """
  Returns a trit representation of an integer value.

  References:
    - https://dev.to/buntine/the-balanced-ternary-machines-of-soviet-russia
    - https://en.wikipedia.org/wiki/Balanced_ternary
    - https://rosettacode.org/wiki/Balanced_ternary#Python
  """
  if n == 0:
    return []

  quotient, remainder = divmod(n, 3)

  if remainder == 2:
    # Lend 1 to the next place so we can make this trit negative.
    quotient  += 1
    remainder = -1

  return [remainder] + trits_from_int(quotient)


def int_from_trits(trits):
  # type: (Iterable[int]) -> int
  """
  Converts a sequence of trits into an integer value.
  """
  # Normally we'd have to wrap ``enumerate`` inside ``reversed``, but
  # balanced ternary puts least significant digits first.
  return sum(base * (3 ** power) for power, base in enumerate(trits))


class TryteString(object):
  """
  A string representation of a sequence of trytes.

  A tryte string is similar in concept to Python's byte string, except
  it has a more limited alphabet.  Byte strings are limited to ASCII
  (256 possible values), while the tryte string alphabet only has 27
  characters (one for each possible tryte configuration).

  IMPORTANT: A TryteString does not represent a numeric value!
  """
  @classmethod
  def from_bytes(cls, bytes_):
    # type: (Union[binary_type, bytearray]) -> TryteString
    """
    Creates a TryteString from an ASCII representation.
    """
    return cls(encode(bytes_, 'trytes'))

  @classmethod
  def from_trytes(cls, trytes):
    # type: (Iterable[Iterable[int]]) -> TryteString
    """
    Creates a TryteString from a sequence of trytes.

    References:
      - :py:func:`trytes_from_int`
      - :py:meth:`as_trytes`
    """
    chars = bytearray()

    for t in trytes:
      converted = int_from_trits(t)

      # :py:meth:`_tryte_from_int`
      if converted < 0:
        converted += 27

      chars.append(TrytesCodec.alphabet[converted])

    return cls(chars)

  @classmethod
  def from_trits(cls, trits, pad=False):
    # type: (Iterable[int], bool) -> TryteString
    """
    Creates a TryteString from a sequence of trits.

    :param trits:
      Iterable of trit values (-1, 0, 1).

    :param pad:
      How to handle a sequence with length not divisible by 3:

      - ``False`` (default): raise a :py:class:`ValueError`.
      - ``True``: pad to a valid length, using null trits.

      Note that this parameter behaves differently than in
        :py:meth:`__init__`.

    References:
      - :py:func:`int_from_trits`
      - :py:meth:`as_trits`
    """
    # Allow passing a generator or other non-Sized value to this
    # method.
    trits = list(trits)

    if pad:
      trits += [0] * max(0, 3 - (len(trits) % 3))

    if len(trits) % 3:
      raise ValueError(
        'Cannot convert sequence with length {length} to trytes; '
        'length must be divisible by 3.'.format(
          length = len(trits),
        ),
      )

    return cls.from_trytes([
      # :see: http://stackoverflow.com/a/1751478/
      trits[i:i+3] for i in range(0, len(trits), 3)
    ])

  def __init__(self, trytes, pad=None):
    # type: (TrytesCompatible, int) -> None
    """
    :param trytes:
      Byte string or bytearray.

    :param pad:
      Ensure at least this many trytes.

      If there are too few, null trytes will be appended to the
      TryteString.

      Note:  If the TryteString is too long, it will _not_ be
      truncated!
    """
    super(TryteString, self).__init__()

    if isinstance(trytes, (int, float)):
      raise TypeError(
        'Converting {type} is not supported; '
        '{cls} is not a numeric type.'.format(
          type  = type(trytes).__name__,
          cls   = type(self).__name__,
        ),
      )

    if isinstance(trytes, TryteString):
      # Create a copy of the incoming TryteString's trytes, to ensure
      # we don't modify it when we apply padding.
      trytes = bytearray(trytes._trytes)
    else:
      if not isinstance(trytes, bytearray):
        trytes = bytearray(trytes)

      for i, ordinal in enumerate(trytes):
        if ordinal not in TrytesCodec.index:
          raise ValueError(
            'Invalid character {char!r} at position {i} '
            '(expected A-Z or 9).'.format(
              char  = chr(ordinal),
              i     = i,
            ),
          )

    if pad:
      trytes += b'9' * max(0, pad - len(trytes))

    self._trytes = trytes

  def __repr__(self):
    # type: () -> Text
    return 'TryteString({trytes!r})'.format(trytes=binary_type(self._trytes))

  def __bytes__(self):
    # type: () -> binary_type
    """
    Converts the TryteString into a string representation.

    Note that this method will NOT convert the trytes back into bytes;
    use :py:meth:`as_bytes` for that.
    """
    return binary_type(self._trytes)

  # :bc: Magic method has a different name in Python 2.
  if PY2:
    __str__ = __bytes__

  def __len__(self):
    # type: () -> int
    return len(self._trytes)

  def __iter__(self):
    # type: () -> Generator[binary_type]
    # :see: http://stackoverflow.com/a/14267935/
    return (self._trytes[i:i + 1] for i in range(len(self)))

  def as_bytes(self, errors='strict'):
    # type: (Text) -> binary_type
    """
    Converts the TryteString into a byte string.

    :param errors:
      How to handle trytes that can't be converted:
        - 'strict':   raise a TrytesDecodeError.
        - 'replace':  replace with '?'.
        - 'ignore':   omit the tryte from the byte string.
    """
    # :bc: In Python 2, `decode` does not accept keyword arguments.
    return decode(self._trytes, 'trytes', errors)

  def as_json(self):
    # type: () -> Text
    """
    Converts the TryteString into a JSON representation.

    See :py:class:`iota.json.JsonEncoder`.
    """
    return self._trytes.decode('ascii')

  def as_trytes(self):
    """
    Converts the TryteString into a sequence of trytes.

    Each tryte is represented as a list with 3 trit values.

    See :py:meth:`as_trits` for more info.

    IMPORTANT: TryteString is not a numeric type, so the result of this
    method should not be interpreted as an integer!
    """
    return [
      self._tryte_from_int(TrytesCodec.index[c])
        for c in self._trytes
    ]

  def as_trits(self):
    """
    Converts the TryteString into a sequence of trit values.

    A trit may have value 1, 0, or -1.

    References:
      - https://en.wikipedia.org/wiki/Balanced_ternary

    IMPORTANT: TryteString is not a numeric type, so the result of this
    method should not be interpreted as an integer!
    """
    # http://stackoverflow.com/a/952952/5568265#comment4204394_952952
    return list(chain.from_iterable(self.as_trytes()))

  @staticmethod
  def _tryte_from_int(n):
    """
    Converts an integer into a single tryte.

    This method is specialized for TryteStrings:
      - The value must fit inside a single tryte.
      - If the value is greater than 13, it will trigger an overflow.
    """
    if n > 26:
      raise ValueError('{n} cannot be represented by a single tryte.'.format(
        n = n,
      ))

    # For values greater than 13, trigger an overflow.
    # E.g., 14 => -13, 15 => -12, etc.
    if n > 13:
      n -= 27

    return trytes_from_int(n)[0]

  def __eq__(self, other):
    # type: (TrytesCompatible) -> bool
    if isinstance(other, TryteString):
      return self._trytes == other._trytes
    elif isinstance(other, (binary_type, bytearray)):
      return self._trytes == other
    else:
      raise TypeError(
        'Invalid type for TryteString comparison '
        '(expected Union[TryteString, binary_type, bytearray], '
        'actual {type}).'.format(
          type = type(other).__name__,
        ),
      )

  # :bc: In Python 2 this must be defined explicitly.
  def __ne__(self, other):
    # type: (TrytesCompatible) -> bool
    return not (self == other)


class Address(TryteString):
  """
  A TryteString that acts as an address, with support for generating
  and validating checksums.
  """
  LEN = 81

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(Address, self).__init__(trytes, pad=self.LEN)

    if len(self._trytes) > self.LEN:
      raise ValueError('Addresses must be 81 trytes long.')


class Tag(TryteString):
  """
  A TryteString that acts as a transaction tag.
  """
  LEN = 27

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(Tag, self).__init__(trytes, pad=self.LEN)

    if len(self._trytes) > self.LEN:
      raise ValueError('Tags must be 27 trytes long.')


class TransactionId(TryteString):
  """
  A TryteString that acts as a transaction or bundle ID.
  """
  LEN = 81

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(TransactionId, self).__init__(trytes, pad=self.LEN)

    if len(self._trytes) > self.LEN:
      raise ValueError('TransactionIds must be 81 trytes long.')


class Transfer(object):
  """
  A message [to be] published to the Tangle.
  """
  def __init__(self, recipient, value, message=None, tag=None):
    # type: (Address, int, Optional[TryteString], Optional[Tag]) -> None
    self.recipient  = recipient
    self.value      = value,
    self.message    = TryteString(message or b'')
    self.tag        = Tag(tag or b'')


Bundle = List[Transfer]
"""
Placeholder for Bundle type in docstrings.
"""
