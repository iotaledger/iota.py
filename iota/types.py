# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Optional, Text


class Trit(object):
  """
  Ternary version of a bit.

  A trit is similar to a bit, except that it has 3 states:  1, 0 and
    unknown.
  """
  def __init__(self, value):
    # type: (int) -> None
    if type(value) is not int:
      raise TypeError('Allowed types for Trit: [int].')

    if not -1 <= value <= 1:
      raise ValueError('Allowed values for Trit: [-1, 0, 1].')

    self.value = value

  def __repr__(self):
    # type: () -> Text
    return 'Trit({value})'.format(value=self.value)

  def __eq__(self, other):
    # type: (Trit) -> bool
    return self.__cmp__(other) in (0,)

  def __ne__(self, other):
    # type: (Trit) -> bool
    return self.__cmp__(other) in (-1, 1, None)

  def __lt__(self, other):
    # type: (Trit) -> bool
    return self.__cmp__(other) in (-1,)

  def __le__(self, other):
    # type: (Trit) -> bool
    return self.__cmp__(other) in (-1, 0)

  def __gt__(self, other):
    # type: (Trit) -> bool
    return self.__cmp__(other) in (1,)

  def __ge__(self, other):
    # type: (Trit) -> bool
    return self.__cmp__(other) in (0, 1)

  def __cmp__(self, other):
    # type: (Trit) -> Optional[int]
    if not isinstance(other, Trit):
      raise TypeError('Trits can only be compared to other Trits.')

    if -1 in (self.value, other.value):
      return None

    # :see: https://docs.python.org/3/whatsnew/3.0.html#ordering-comparisons
    return (self.value > other.value) - (self.value < other.value)
