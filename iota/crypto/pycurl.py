# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

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
    """
    length  = len(trits)
    offset  = 0

    # Copy trits from ``trits`` into internal state, one hash at a
    # time, transforming internal state in between hashes.
    while offset < length:
      start = offset
      stop  = min(start + HASH_LENGTH, length)

      #
      # Copy the next hash worth of trits to internal state.
      #
      # Note that we always copy the trits to the start of the state.
      # ``self._state`` is 3 hashes long, but only the first hash is
      # "public"; the other 2 are only accessible to
      # :py:meth:`_transform`.
      #
      self._state[0:stop-start] = trits[start:stop]

      # Transform.
      self._transform()

      # Move on to the next hash.
      offset += HASH_LENGTH

  def squeeze(self, trits):
    # type: (MutableSequence[int]) -> None
    """
    Squeeze trits from the sponge.

    :param trits:
      Sequence that the squeezed trits will be copied to.
      Note: this object will be modified!
    """
    #
    # Squeeze is kind of like the opposite of absorb; it copies trits
    # from internal state to the ``trits`` parameter, one hash at a
    # time, and transforming internal state in between hashes.
    #
    # However, only the first hash of the state is "public", so we
    # can simplify the implementation somewhat.
    #

    # Note that we copy at most len(trits) trits!
    length = min(HASH_LENGTH, len(trits))
    trits[0:length] = self._state[0:length]

    # One hash worth of trits copied; now transform.
    self._transform()

  def _transform(self):
    # type: () -> None
    """
    Transforms internal state.
    """
    # Copy some values locally so we can avoid global lookups in the
    # inner loop.
    # :see: https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Local_Variables
    state_length  = STATE_LENGTH
    truth_table   = TRUTH_TABLE

    # Optimization: Ensure that we use a generator to create ranges.
    if PY2:
      # In Python 2, ``range`` returns a list, while ``xrange`` returns
      # a generator.
      # noinspection PyUnresolvedReferences
      range_ = xrange
    else:
      # In Python 3, ``range`` returns a generator, and ``xrange`` is
      # baleeted.
      range_ = range

    # Operate on a copy of ``self._state`` to eliminate dot lookups in
    # the inner loop.
    # :see: https://wiki.python.org/moin/PythonSpeed/PerformanceTips#Avoiding_dots...
    # :see: http://stackoverflow.com/a/2612990/
    prev_state  = self._state[:]
    new_state   = prev_state[:]

    index = 0
    for _ in range_(NUMBER_OF_ROUNDS):
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

    self._state = new_state
