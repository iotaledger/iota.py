# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Iterable, List, Optional, Union

__all__ = [
  'Curl',
]


TRUTH_TABLE = [1, 0, -1, 1, -1, 0, -1, 1, 0]


class Curl(object):
  """
  Python implementation of Curl.

  **IMPORTANT: Not thread-safe!**
  """
  STATE_LEN = 729

  def __init__(self, state=None):
    # type: (Optional[Iterable[int]]) -> None
    """
    :param state:
      Initial state.

      Note: this has the same effect as calling :py:meth:`absorb`
      immediately after initializing the object.
    """
    self._state = [0] * self.STATE_LEN # type: List[int]
    self._dirty = False

    if state is not None:
      self.absorb(state)

  def __getitem__(self, item):
    # type: (Union[int, slice]) -> List[int]
    """
    Alias for :py:meth:`squeeze`.
    """
    return self.squeeze(item)

  def absorb(self, trits):
    # type: (Iterable[int]) -> None
    """
    Absorb trits into the sponge.
    """
    for i, trit in enumerate(trits):
      self._state[i] = trit

    self._dirty = True

  def squeeze(self, slice_=None):
    # type: (Optional[Union[int, slice]]) -> List[int]
    """
    Squeeze trytes from the sponge.
    """
    self._transform()

    return (
      list(self._state)
        if slice_ is None
        else self._state[slice_]
    )

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
    Transforms internal state.
    """
    if self._dirty:
      index = 0

      for _ in range(27):
        temp_state = list(self._state)

        for pos in range(self.STATE_LEN):
          prev_index = index
          index += (364 if index < 365 else -365)

          self._state[pos] = (
              TRUTH_TABLE[
                  temp_state[prev_index]
                + (3 * temp_state[index])
                + 4
              ]
          )

    self._dirty = False
