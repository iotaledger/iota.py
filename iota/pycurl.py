# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota import TryteString


TRUTH_TABLE = [1, 0, -1, 1, -1, 0, -1, 1, 0]


class Curl(object):
  """
  Python implementation of Curl.

  **IMPORTANT: Not thread-safe!**
  """
  def __init__(self):
    self._state = []
    self._dirty = False

  def absorb(self, trytes):
    # type: (TryteString) -> None
    """
    Absorb trytes into the sponge.
    """
    for i, trit in enumerate(trytes.as_trits()):
      self._state[i] = trit

    self._dirty = True

  def squeeze(self):
    # type: () -> TryteString
    """
    Squeeze trytes from the sponge.
    """
    self._transform()
    return TryteString.from_trytes(self._state)

  def reset(self):
    # type: () -> None
    """
    Resets the internal state.
    """
    self._state = []
    self._dirty = False

  def _transform(self):
    # type: () -> None
    """
    Prepares internal state.
    """
    if self._dirty:
      index = 0

      for _ in range(27):
        temp_state = list(self._state)

        for i in range(729):
          self._state[i] = (
              TRUTH_TABLE[
                  temp_state[index]
                + temp_state[index + (364 if index < 365 else -365)]
              ]
            * 3
            + 4
          )

    self._dirty = False
