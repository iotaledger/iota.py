# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from math import ceil
from typing import List, MutableSequence, Optional, Sequence

from six import PY2

__all__ = [
  'Curl',
  'HASH_LENGTH',
]

HASH_LENGTH   = 243
STATE_LENGTH  = 3 * HASH_LENGTH

NUMBER_OF_ROUNDS  = 27
TRUTH_TABLE       = [1, 0, -1, 1, -1, 0, -1, 1, 0]


class Curl(object):
  """
  Python implementation of Curl.

  **IMPORTANT: Not thread-safe!**
  """
  def __init__(self):
    # type: (Optional[Sequence[int]]) -> None
    self.reset()

  # noinspection PyAttributeOutsideInit
  def reset(self):
    # type: () -> None
    """
    Resets internal state.
    """
    self._state = [0] * STATE_LENGTH # type: List[int]

  def absorb(self, trits):
    # type: (Sequence[int], Optional[int]) -> None
    """
    Absorb trits into the sponge.

    :param trits:
      Sequence of trits to absorb.
      Note: Only the first 729 trits will be absorbed.
    """
    self._copy_and_transform(trits, self._state, len(trits))

  def squeeze(self, trits):
    # type: (MutableSequence[int]) -> None
    """
    Squeeze trits from the sponge.

    :param trits:
      Sequence that the squeezed trits will be copied to.
      Note: this object will be modified!
    """
    self._copy_and_transform(self._state, trits, len(trits))

  def _copy_and_transform(self, source, target, length):
    """
    Copies trits from ``source`` to ``target`` one hash at a time,
    transforming in between hashes.
    """
    for i in range(int(ceil(length / HASH_LENGTH))):
      start = i * HASH_LENGTH
      stop  = min(len(target), len(source), start + HASH_LENGTH)

      target[start:stop] = source[start:stop]
      self._transform()

  def _transform(self):
    # type: () -> None
    """
    Transforms internal state.
    """
    # Copy some values locally so we can reduce the number of dot
    # lookups we have to perform per list iteration.
    # :see: https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Avoiding_dots...
    state_length  = STATE_LENGTH
    truth_table   = TRUTH_TABLE

    # Optimization for Python 2
    if PY2:
      # noinspection PyUnresolvedReferences
      range_ = xrange
    else:
      range_ = range

    # :see: http://stackoverflow.com/a/2612990/
    prev_state  = self._state[:]
    new_state   = prev_state[:]

    index = 0
    for _ in range_(NUMBER_OF_ROUNDS):
      # noinspection PyUnusedLocal
      for pos in range_(state_length):
        prev_index = index
        index += (364 if index < 365 else -365)

        new_state[pos] = (
            truth_table[
                prev_state[prev_index]
              + (3 * prev_state[index])
              + 4
            ]
        )

      prev_state  = new_state
      new_state   = new_state[:]

    self._state = prev_state
