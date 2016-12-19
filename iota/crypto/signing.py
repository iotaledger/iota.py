# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, List, MutableSequence, Optional, Union

from iota import TryteString, TrytesCompatible
from iota.crypto import Curl

__all__ = [
  'KeyGenerator',
  'SigningKey',
]


class Seed(TryteString):
  """
  A TryteString that acts as a seed for generating new keys.
  """
  LEN = 81

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(Seed, self).__init__(trytes, pad=self.LEN)

    if len(self._trytes) > self.LEN:
      raise ValueError('{cls} values must be {len} trytes long.'.format(
        cls = type(self).__name__,
        len = self.LEN
      ))


class SigningKey(TryteString):
  """
  A TryteString that acts as a signing key, e.g., for generating
  message signatures, new addresses, etc.
  """
  LEN = 6561

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(SigningKey, self).__init__(trytes, pad=self.LEN)

    if len(self._trytes) > self.LEN:
      raise ValueError('{cls} values must be {len} trytes long.'.format(
        cls = type(self).__name__,
        len = self.LEN
      ))


class KeyGenerator(object):
  """
  Generates signing keys for messages.
  """
  def __init__(self, seed):
    # type: (TrytesCompatible) -> None
    super(KeyGenerator, self).__init__()

    self.seed = Seed(seed).as_trits()

  def __getitem__(self, slice_):
    # type: (Union[int, slice]) -> Union[SigningKey, List[SigningKey]]
    """
    Generates and returns one or more keys at the specified index(es).

    :param slice_:
      Index of key to generate, or a slice.

      Warning: This method may take awhile to run if the requested
      index(es) is a large number!

    :return:
      Behavior matches slicing behavior of other collections:

      - If an int is provided, a single key will be returned.
      - If a slice is provided, a list of keys will be returned.
    """
    return (
      self.get_keys(slice_.start, slice_.stop, slice_.step)
        if isinstance(slice_, slice)
        else self.get_keys(slice_)[0]
    )

  def get_keys(self, start, stop=None, step=1, iterations=1):
    # type: (int, Optional[int], int, int) -> List[SigningKey]
    """
    Generates and returns one or more keys at the specified index(es).

    This is a one-time operation; if you want to create lots of keys
    across multiple contexts, consider invoking
    :py:meth:`create_generator` and sharing the resulting generator
    object instead.

    Warning: This method may take awhile to run if the starting index
    and/or the number of requested keys is a large number!

    :param start:
      Starting index.

    :param stop:
      Stop before this index.
      If ``None``, only generate a single key.

    :param step:
      Number of indexes to advance after each key.

    :param iterations:
      Number of _transform iterations to apply to each key.
      Must be >= 1.

      Increasing this value makes key generation slower, but more
      resistant to brute-forcing.

    :return:
      Always returns a list, even if only one key is generated.
    """
    generator = self.create_generator(start, step, iterations)
    interval  = range(start, start+1 if stop is None else stop, step)

    keys = []
    for _ in interval:
      try:
        next_key = next(generator)
      except StopIteration:
        break
      else:
        keys.append(next_key)

    return keys

  def create_generator(self, start, step=1, iterations=1):
    # type: (int, int) -> Generator[SigningKey]
    """
    Creates a generator that can be used to progressively generate new
    keys.

    :param start:
      Starting index.

      Warning: This method may take awhile to reset if ``start``
      is a large number!

    :param step:
      Number of indexes to advance after each key.

      This value can be negative; the generator will exit if it
      reaches an index < 0.

      Warning: The generator may take awhile to advance between
      iterations if ``step`` is a large number!

    :param iterations:
      Number of _transform iterations to apply to each key.
      Must be >= 1.

      Increasing this value makes key generation slower, but more
      resistant to brute-forcing.
    """
    current = start

    while current >= 0:
      sponge = self._create_sponge(current)

      key = []

      for i in range(iterations):
        for j in range(27):
          # Multiply by 3 because sponge works with trits, but
          # ``Seed.LEN`` is a quantity of trytes.
          buffer = [0] * (Seed.LEN * 3) # type: MutableSequence[int]
          sponge.squeeze(buffer)
          key += buffer

      yield SigningKey.from_trits(key)

      current += step

  def _create_sponge(self, index):
    # type: (int) -> Curl
    """
    Prepares the Curl sponge for the generator.
    """
    seed = list(self.seed) # type: MutableSequence[int]

    for i in range(index):
      # Increment each tryte unless/until we overflow.
      for j in range(len(seed)):
        seed[j] += 1

        if seed[j] > 1:
          seed[j] = -1
        else:
          break

    sponge = Curl()
    sponge.absorb(seed)

    # Squeeze all of the trits out of the sponge and re-absorb them.
    # Note that Curl transforms several times per operation, so this
    # sequence is not as redundant as it looks at first glance.
    sponge.squeeze(seed)
    sponge.reset()
    sponge.absorb(seed)

    return sponge
