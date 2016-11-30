# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Text, Union

from six import PY2, binary_type


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
  # :bc: Without the bytearray cast, Python 2 will populate the dict
  #   with characters instead of integers.
  # noinspection SpellCheckingInspection
  alphabet  = dict(enumerate(bytearray(b'9ABCDEFGHIJKLMNOPQRSTUVWXYZ')))
  index     = dict(zip(alphabet.values(), alphabet.keys()))

  @classmethod
  def from_bytes(cls, bytes_):
    # type: (Union[binary_type, bytearray]) -> TryteString
    """Creates a TryteString from a byte string."""
    trytes = bytearray()

    # :bc: In Python 2, iterating over a byte string yields characters
    #   instead of integers.
    if not isinstance(bytes_, bytearray):
      bytes_ = bytearray(bytes_)

    for c in bytes_:
      second, first = divmod(c, len(cls.alphabet))

      trytes.append(cls.alphabet[first])
      trytes.append(cls.alphabet[second])

    return cls(trytes)

  def __init__(self, trytes, pad=False):
    # type: (Union[binary_type, bytearray], bool) -> None
    super(TryteString, self).__init__()

    if len(trytes) % 2:
      if pad:
        trytes += self.alphabet[0]
      else:
        raise ValueError(
          'Length of TryteString must be divisible by 2.'
        )

    self.trytes =\
      trytes if isinstance(trytes, bytearray) else bytearray(trytes)

  def __repr__(self):
    # type: () -> Text
    return 'TryteString({trytes!r})'.format(trytes=binary_type(self.trytes))

  def __bytes__(self):
    # type: () -> Text
    """Converts the TryteString into a byte string."""
    bytes_ = bytearray()

    for i in range(0, len(self.trytes), 2):
      bytes_.append(
          self.index[self.trytes[i]]
        + (self.index[self.trytes[i + 1]] * len(self.index))
      )

    return binary_type(bytes_)

  # :bc: Magic method has a different name in Python 2.
  if PY2:
    __str__ = __bytes__

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
