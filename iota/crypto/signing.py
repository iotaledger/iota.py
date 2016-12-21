# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, List, MutableSequence

from iota import TryteString, TrytesCompatible
from iota.crypto import Curl, HASH_LENGTH
from iota.crypto.types import SigningKey

__all__ = [
  'KeyGenerator',
]


class KeyGenerator(object):
  """
  Generates signing keys for messages.
  """
  def __init__(self, seed):
    # type: (TrytesCompatible) -> None
    super(KeyGenerator, self).__init__()

    self.seed = TryteString(seed, pad=81).as_trits()

  def get_keys(self, start, count=1, step=1, iterations=1):
    # type: (int, int, int, int) -> List[SigningKey]
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
      Must be >= 0.

    :param count:
      Number of keys to generate.
      Must be > 0.

    :param step:
      Number of indexes to advance after each key.
      This may be any non-zero (positive or negative) integer.

    :param iterations:
      Number of _transform iterations to apply to each key.
      Must be >= 1.

      Increasing this value makes key generation slower, but more
      resistant to brute-forcing.

    :return:
      Always returns a list, even if only one key is generated.

      The returned list will contain ``count`` keys, except when
      ``step * count < start`` (only applies when ``step`` is
      negative).
    """
    if count < 1:
      raise ValueError('``count`` must be positive.')

    if not step:
      raise ValueError('``step`` must not be zero.')

    generator = self.create_generator(start, step, iterations)

    keys = []
    for _ in range(count):
      try:
        next_key = next(generator)
      except StopIteration:
        break
      else:
        keys.append(next_key)

    return keys

  def create_generator(self, start=0, step=1, iterations=1):
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
    if start < 0:
      raise ValueError('``start`` cannot be negative.')

    current = start

    while current >= 0:
      sponge = self._create_sponge(current)

      key = []

      for i in range(iterations):
        for j in range(27):
          # Multiply by 3 because sponge works with trits, but
          # ``Seed.LEN`` is a quantity of trytes.
          buffer = [0] * HASH_LENGTH # type: MutableSequence[int]
          sponge.squeeze(buffer)
          key += buffer

      yield SigningKey.from_trits(key)

      current += step

  def _create_sponge(self, index):
    # type: (int) -> Curl
    """
    Prepares the Curl sponge for the generator.
    """
    # :see: http://stackoverflow.com/a/2612990/
    seed = self.seed[:] # type: MutableSequence[int]

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
