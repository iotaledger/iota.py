# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, List, MutableSequence, Optional

from iota import TryteString, TrytesCompatible
from iota.crypto import Curl, HASH_LENGTH

__all__ = [
  'KeyGenerator',
  'Seed',
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
  BLOCK_LEN = 2187
  """
  Similar to RSA keys, SigningKeys must have a length that is divisible
  by a certain number of trytes.
  """

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(SigningKey, self).__init__(trytes)

    if len(self._trytes) % self.BLOCK_LEN:
      raise ValueError(
        'Length of {cls} values must be a multiple of {len} trytes.'.format(
          cls = type(self).__name__,
          len = self.BLOCK_LEN
        ),
      )

  @property
  def block_count(self):
    # type: () -> int
    """
    Returns the length of this key, expressed in blocks.
    """
    return len(self) // self.BLOCK_LEN

  def get_digest_trits(self):
    # type: () -> List[int]
    """
    Generates the digest used to do the actual signing.

    Signing keys can have variable length and tend to be quite long,
    which makes them not-well-suited for use in crypto algorithms.

    The digest is essentially the result of running the signing key
    through a PBKDF, yielding a constant-length hash that can be used
    for crypto.
    """
    # Multiply by 3 to convert trytes into trits.
    block_size  = self.BLOCK_LEN * 3
    raw_trits   = self.as_trits()

    # Initialize list with the correct length to improve performance.
    digest = [0] * HASH_LENGTH  # type: List[int]

    for i in range(self.block_count):
      block_start = i * block_size
      block_end   = block_start + block_size

      block_trits = raw_trits[block_start:block_end]

      # Initialize ``key_fragment`` with the correct length to
      # improve performance.
      key_fragment = [0] * block_size # type: List[int]

      buffer = [] # type: List[int]

      for j in range(27):
        hash_start = j * HASH_LENGTH
        hash_end   = hash_start + HASH_LENGTH

        buffer = block_trits[hash_start:hash_end]

        for k in range(26):
          sponge = Curl()
          sponge.absorb(buffer)
          sponge.squeeze(buffer)

        key_fragment[hash_start:hash_end] = buffer

      sponge = Curl()
      sponge.absorb(key_fragment)
      sponge.squeeze(buffer)

      digest[block_start:block_end] = buffer

    return digest


class KeyGenerator(object):
  """
  Generates signing keys for messages.
  """
  def __init__(self, seed):
    # type: (TrytesCompatible) -> None
    super(KeyGenerator, self).__init__()

    self.seed = Seed(seed).as_trits()

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
