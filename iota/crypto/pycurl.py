# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from math import ceil
from typing import List, MutableSequence, Optional, Sequence

__all__ = [
  'Curl',
]


class Curl(object):
  """
  Python implementation of Curl.

  **IMPORTANT: Not thread-safe!**
  """
  HASH_LENGTH   = 243
  STATE_LENGTH  = 3 * HASH_LENGTH

  NUMBER_OF_ROUNDS = 27

  TRUTH_TABLE = [1, 0, -1, 1, -1, 0, -1, 1, 0]

  def __init__(self):
    # type: (Optional[Sequence[int]]) -> None
    self.reset()

  # noinspection PyAttributeOutsideInit
  def reset(self):
    # type: () -> None
    """
    Resets internal state.
    """
    self._state = [0] * self.STATE_LENGTH # type: List[int]

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
    for i in range(int(ceil(length / self.HASH_LENGTH))):
      start = i * self.HASH_LENGTH
      stop  = min(len(target), len(source), start + self.HASH_LENGTH)

      target[start:stop] = source[start:stop]
      self._transform()

  def _transform(self):
    # type: () -> None
    """
    Transforms internal state.
    """
    index = 0

    for _ in range(self.NUMBER_OF_ROUNDS):
      temp_state = list(self._state)

      for pos in range(self.STATE_LENGTH):
        prev_index = index
        index += (364 if index < 365 else -365)

        self._state[pos] = (
            self.TRUTH_TABLE[
                temp_state[prev_index]
              + (3 * temp_state[index])
              + 4
            ]
        )
