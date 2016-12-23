# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from math import ceil
from os import urandom
from typing import Callable, List, Optional

from iota import Hash, TRITS_PER_TRYTE, TryteString, TrytesCompatible
from iota.crypto import HASH_LENGTH, Curl
from iota.exceptions import with_context
from six import binary_type

__all__ = [
  'PrivateKey',
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
  BLOCK_LEN = 2187
  """
  Similar to RSA keys, SigningKeys must have a length that is divisible
  by a certain number of trytes.
  """

  def __init__(self, trytes, key_index=None):
    # type: (TrytesCompatible, Optional[int]) -> None
    super(PrivateKey, self).__init__(trytes)

    if len(self._trytes) % self.BLOCK_LEN:
      raise with_context(
        exc = ValueError(
          'Length of {cls} values must be a multiple of {len} trytes.'.format(
            cls = type(self).__name__,
            len = self.BLOCK_LEN
          ),
        ),

        context = {
          'trytes': trytes,
        },
      )

    self.key_index = key_index

  @property
  def block_count(self):
    # type: () -> int
    """
    Returns the length of this key, expressed in blocks.
    """
    return len(self) // self.BLOCK_LEN

  def create_signature(self, trytes, blocks=None):
    # type: (TryteString, Optional[int]) -> TryteString
    """
    Creates a signature for the specified trytes.

    :param trytes:
      The trytes to use to build the signature.

    :param blocks:
      Max length of the resulting signature, expressed in blocks.

      See :py:attr:`BLOCK_LEN` for more info.
    """
    signature = self.as_trits()
    if blocks is not None:
      signature = signature[:self.BLOCK_LEN*blocks*TRITS_PER_TRYTE]

    hash_count = int(ceil(len(signature) / HASH_LENGTH))

    source = trytes.as_trits()
    source += [0] * max(0, hash_count - len(source))

    sponge = Curl()

    # Build signature, one hash at a time.
    for i in range(hash_count):
      start = i * HASH_LENGTH
      stop  = start + HASH_LENGTH

      fragment = signature[start:stop]

      # Use value from the source trits to make the signature
      # deterministic.
      for j in range(13 - source[i]):
        sponge.reset()
        sponge.absorb(fragment)
        sponge.squeeze(fragment)

      # Copy the signature fragment to the final signature.
      signature[start:stop] = fragment

    return signature

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
    block_size  = self.BLOCK_LEN * TRITS_PER_TRYTE
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
