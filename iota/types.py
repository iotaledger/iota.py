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
    tryte_string = bytearray()

    # :bc: In Python 2, iterating over a byte string yields characters
    #   instead of integers.
    if not isinstance(bytes_, bytearray):
      bytes_ = bytearray(bytes_)

    for c in bytes_:
      second, first = divmod(c, len(cls.alphabet))

      tryte_string.append(cls.alphabet[first])
      tryte_string.append(cls.alphabet[second])

    return cls(tryte_string)

  def __init__(self, value, pad=False):
    # type: (Union[binary_type, bytearray], bool) -> None
    super(TryteString, self).__init__()

    if len(value) % 2:
      if pad:
        value += self.alphabet[0]
      else:
        raise ValueError(
          'Length of TryteString must be divisible by 2.'
        )

    self.value = value if isinstance(value, bytearray) else bytearray(value)

  def __repr__(self):
    # type: () -> Text
    return 'TryteString({value!r})'.format(value=binary_type(self.value))

  def __bytes__(self):
    # type: () -> Text
    """Converts the TryteString into a byte string."""
    byte_string = bytearray()

    for i in range(0, len(self.value), 2):
      byte_string.append(
          self.index[self.value[i]]
        + (self.index[self.value[i+1]] * len(self.index))
      )

    return binary_type(byte_string)

  if PY2:
    __str__ = __bytes__
