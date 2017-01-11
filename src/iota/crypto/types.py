# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from math import ceil
from os import urandom
from typing import Callable, List, MutableSequence, Optional, Tuple

from six import binary_type

from iota import Hash, TryteString, TrytesCompatible
from iota.crypto import Curl, FRAGMENT_LENGTH, HASH_LENGTH
from iota.exceptions import with_context

__all__ = [
  'PrivateKey',
  'Seed',
]


class Seed(TryteString):
  """
  A TryteString that acts as a seed for crypto functions.
  """
  @classmethod
  def random(cls, length=Hash.LEN, source=urandom):
    # type: (int, Optional[Callable[[int], binary_type]]) -> Seed
    """
    Generates a new random seed.

    :param length:
      Minimum number of trytes to generate.
      This should be at least 81 (one hash).

    :param source:
      CSPRNG function or method to use to generate randomness.

      Note:  This parameter must be a function/method that accepts an
      int and returns random bytes.

      Example::

         from Crypto import Random
         new_seed = Seed.random(source=Random.new().read)
    """
    # Encoding bytes -> trytes yields 2 trytes per byte.
    # Note: int cast for compatibility with Python 2.
    return cls.from_bytes(source(int(ceil(length / 2))))


class PrivateKey(TryteString):
  """
  A TryteString that acts as a private key, e.g., for generating
  message signatures, new addresses, etc.
  """
  def __init__(self, trytes, key_index=None):
    # type: (TrytesCompatible, Optional[int]) -> None
    super(PrivateKey, self).__init__(trytes)

    if len(self._trytes) % FRAGMENT_LENGTH:
      raise with_context(
        exc = ValueError(
          'Length of {cls} values must be a multiple of {len} trytes.'.format(
            cls = type(self).__name__,
            len = FRAGMENT_LENGTH
          ),
        ),

        context = {
          'trytes': trytes,
        },
      )

    self.key_index = key_index

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
    hashes_per_fragment = FRAGMENT_LENGTH // Hash.LEN

    key_chunks = self.iter_chunks(FRAGMENT_LENGTH)

    # The digest will contain one hash per key fragment.
    digest = [0] * HASH_LENGTH * len(key_chunks)

    for (i, fragment) in enumerate(key_chunks): # type: Tuple[int, TryteString]
      fragment_trits = fragment.as_trits()

      key_fragment  = [0] * FRAGMENT_LENGTH
      hash_trits    = []

      for j in range(hashes_per_fragment):
        hash_start  = j * HASH_LENGTH
        hash_end    = hash_start + HASH_LENGTH
        hash_trits  = fragment_trits[hash_start:hash_end] # type: MutableSequence[int]

        for k in range(26):
          sponge = Curl()
          sponge.absorb(hash_trits)
          sponge.squeeze(hash_trits)

        key_fragment[hash_start:hash_end] = hash_trits

      sponge = Curl()
      sponge.absorb(key_fragment)
      sponge.squeeze(hash_trits)

      fragment_start  = i * FRAGMENT_LENGTH
      fragment_end    = fragment_start + FRAGMENT_LENGTH

      digest[fragment_start:fragment_end] = hash_trits

    return digest
