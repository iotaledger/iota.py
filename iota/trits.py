# coding=utf-8
"""
Provides functions for manipulating sequences of trits.

Based on:
https://github.com/iotaledger/iota.lib.js/blob/v0.4.2/lib/crypto/helpers/adder.js
"""

from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Iterable, List, Optional, Sequence, Tuple

__all__ = [
  'add_trits',
  'int_from_trits',
  'trits_from_int',
]


def add_trits(left, right):
  # type: (Sequence[int], Sequence[int]) -> List[int]
  """
  Adds two sequences of trits together.

  The result is a list of trits equal in length to the longer of the
  two sequences.

  Note:  Overflow is possible.
  For example, ``add_trits([1], [1])`` returns ``[-1]``.
  """
  target_len = max(len(left), len(right))

  res = [0] * target_len
  left += [0] * (target_len - len(left))
  right += [0] * (target_len - len(right))

  carry = 0
  for i in range(len(res)):
    res[i], carry = _full_add_trits(left[i], right[i], carry)

  return res


def int_from_trits(trits):
  # type: (Iterable[int]) -> int
  """
  Converts a sequence of trits into an integer value.
  """
  # Normally we'd have to wrap ``enumerate`` inside ``reversed``, but
  # balanced ternary puts least significant digits first.
  return sum(base * (3 ** power) for power, base in enumerate(trits))


def trits_from_int(n, pad=1):
  # type: (int, Optional[int]) -> List[int]
  """
  Returns a trit representation of an integer value.

  :param n:
    Integer value to convert.

  :param pad:
    Ensure the result has at least this many trits.

  References:
    - https://dev.to/buntine/the-balanced-ternary-machines-of-soviet-russia
    - https://en.wikipedia.org/wiki/Balanced_ternary
    - https://rosettacode.org/wiki/Balanced_ternary#Python
  """
  if n == 0:
    trits = []
  else:
    quotient, remainder = divmod(n, 3)

    if remainder == 2:
      # Lend 1 to the next place so we can make this trit negative.
      quotient  += 1
      remainder = -1

    trits = [remainder] + trits_from_int(quotient, pad=0)

  if pad:
    trits += [0] * max(0, pad - len(trits))

  return trits


def _cons_trits(left, right):
  # type: (int, int) -> int
  """
  Compares two trits.  If they have the same value, returns that value.
  Otherwise, returns 0.
  """
  return left if left == right else 0


def _add_trits(left, right):
  # type: (int, int) -> int
  """
  Adds two individual trits together.

  The result is always a single trit.
  """
  res = left + right
  return res if -2 < res < 2 else (res < 0) - (res > 0)


def _any_trits(left, right):
  # type: (int, int) -> int
  """
  Adds two individual trits together and returns a single trit
  indicating whether the result is positive or negative.
  """
  res = left + right
  return (res > 0) - (res < 0)


def _full_add_trits(left, right, carry):
  # type: (int, int, int) -> Tuple[int, int]
  """
  Adds two trits together, with support for a carry trit.
  """
  sum_both    = _add_trits(left, right)
  cons_left   = _cons_trits(left, right)
  cons_right  = _cons_trits(sum_both, carry)

  return _add_trits(sum_both, carry), _any_trits(cons_left, cons_right)
