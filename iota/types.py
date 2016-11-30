# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Iterable, List, Optional, Text, Union


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


class Tryte(object):
  """
  Ternary version of a byte.

  A tryte is a sequence of three trits.
  """
  def __init__(self, trits, pad=False):
    # type: (Iterable[Union[Trit, int]], bool) -> None
    """
    :param trits: Iterable of 3 trits (or compatible integers).
    :param pad: Whether to pad `trits` if it has less than 3 trits.
    """
    super(Tryte, self).__init__()

    if not isinstance(trits, Iterable):
      raise TypeError('Allowed types for Tryte: [Iterable[Trit]].')

    self.trits = [] # type: List[Trit]

    for trit in trits:
      self.trits.append(
        trit
          if isinstance(trit, Trit)
          else Trit(trit)
      )

    if pad and (len(self.trits) < 3):
      self.trits =\
        [Trit(-1) for _ in range(0, 3 - len(self.trits))] + self.trits

    if len(self.trits) != 3:
      raise ValueError(
        'Incorrect number of Trits for Tryte '
        '(expected 3, actual {count}).'.format(
          count = len(self.trits),
        ),
      )

  def __repr__(self):
    # type: () -> Text
    return 'Tryte({trits})'.format(trits=[trit.value for trit in self.trits])

  def __getitem__(self, item):
    # type: (int) -> Trit
    return self.trits[item]
