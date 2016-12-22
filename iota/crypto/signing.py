# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, List, MutableSequence

from iota import TryteString, TrytesCompatible
from iota.crypto import Curl, HASH_LENGTH
from iota.crypto.types import SigningKey
from iota.exceptions import with_context

__all__ = [
  'KeyGenerator',
]


class KeyGenerator(object):
  """
  Generates signing keys for messages.
  """
  HASHES_PER_BLOCK = 27
  """
  Number of hashes that make up one block in a signing key.
  """

  def __init__(self, seed):
    # type: (TrytesCompatible) -> None
    super(KeyGenerator, self).__init__()

    self.seed = TryteString(seed)

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
      raise with_context(
        exc = ValueError('``count`` must be positive.'),

        context = {
          'start':      start,
          'count':      count,
          'step':       step,
          'iterations': iterations,
        },
      )

    if not step:
      raise with_context(
        exc = ValueError('``step`` must not be zero.'),

        context = {
          'start':      start,
          'count':      count,
          'step':       step,
          'iterations': iterations,
        },
      )

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
      raise with_context(
        exc = ValueError('``start`` cannot be negative.'),

        context = {
          'start':      start,
          'step':       step,
          'iterations': iterations,
        },
      )

    if iterations < 1:
      raise with_context(
        exc = ValueError('``iterations`` must be >= 1.'),

        context = {
          'start':      start,
          'step':       step,
          'iterations': iterations,
        },
      )

    current = start

    while current >= 0:
      sponge = self._create_sponge(current)

      # Multiply by 3 to convert trytes into trits.
      block_length = SigningKey.BLOCK_LEN * 3

      key     = [0] * (block_length * iterations)
      buffer  = [0] * HASH_LENGTH # type: MutableSequence[int]

      for block_seq in range(iterations):
        # Squeeze trits from the buffer and append them to the key, one
        # hash at a time.
        for hash_seq in range(self.HASHES_PER_BLOCK):
          sponge.squeeze(buffer)

          key_start = (block_seq * block_length) + (hash_seq * HASH_LENGTH)
          key_stop  = key_start + HASH_LENGTH

          key[key_start:key_stop] = buffer

      yield SigningKey.from_trits(key)

      current += step

  def _create_sponge(self, index):
    # type: (int) -> Curl
    """
    Prepares the Curl sponge for the generator.
    """
    seed = self.seed.as_trits() # type: MutableSequence[int]

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
