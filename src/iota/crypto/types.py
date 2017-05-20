# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import MutableSequence, Optional, Tuple

from six import itervalues

from iota import Hash, TryteString, TrytesCodec, TrytesCompatible
from iota.crypto import Curl, FRAGMENT_LENGTH, HASH_LENGTH
from iota.exceptions import with_context

try:
  # New in Python 3.6; even ``six`` doesn't know about it yet.
  # noinspection PyCompatibility
  from secrets import SystemRandom
except ImportError:
  from random import SystemRandom

__all__ = [
  'Digest',
  'PrivateKey',
  'Seed',
]


class Digest(TryteString):
  """
  A private key digest.  Basically the same thing as a regular
  :py:class:`TryteString`, except that it (usually) has a key index
  associated with it.

  Note: in a few cases (e.g., generating multisig addresses), a key
  index is not necessary/available.
  """
  def __init__(self, trytes, key_index=None):
    # type: (TrytesCompatible, Optional[int]) -> None
    super(Digest, self).__init__(trytes)

    # A digest is a series of hashes; its length should reflect that.
    if len(self) % Hash.LEN:
      raise with_context(
        exc = ValueError(
          'Length of {cls} values must be a multiple of {len} trytes.'.format(
            cls = type(self).__name__,
            len = Hash.LEN,
          ),
        ),

        context = {
          'trytes': trytes,
        },
      )

    self.key_index = key_index

  @property
  def security_level(self):
    # type: () -> int
    """
    Returns the number of iterations that were used to generate this
    digest (also known as "security level").
    """
    return len(self) // Hash.LEN

  def as_json_compatible(self):
    # type: () -> dict
    return {
      'trytes':     self._trytes.decode('ascii'),
      'key_index':  self.key_index,
    }


class Seed(TryteString):
  """
  A TryteString that acts as a seed for crypto functions.
  """
  @classmethod
  def random(cls, length=Hash.LEN):
    # type: (int) -> Seed
    """
    Generates a new random seed.

    :param length:
      Minimum number of trytes to generate.
      This should be at least 81 (one hash).

      Note: Seeds longer that 81 trytes do not increase security.

    References:
      - https://forum.iota.org/t/why-arent-seeds-longer-than-81-trytes-more-secure/1278
    """
    alphabet  = list(itervalues(TrytesCodec.alphabet))
    generator = SystemRandom()

    # :py:meth:`SystemRandom.choices` wasn't added until Python 3.6;
    # for compatibility, we will continue to use ``choice`` in a loop.
    # https://docs.python.org/3/library/random.html#random.choices
    return cls(
      ''.join(chr(generator.choice(alphabet)) for _ in range(length))
        .encode('ascii')
    )


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
            len = FRAGMENT_LENGTH,
          ),
        ),

        context = {
          'trytes': self._trytes,
        },
      )

    self.key_index = key_index

  def as_json_compatible(self):
    # type: () -> dict
    return {
      'trytes':     self._trytes.decode('ascii'),
      'key_index':  self.key_index,
    }

  def get_digest(self):
    # type: () -> Digest
    """
    Generates the digest used to do the actual signing.

    Signing keys can have variable length and tend to be quite long,
    which makes them not-well-suited for use in crypto algorithms.

    The digest is essentially the result of running the signing key
    through a PBKDF, yielding a constant-length hash that can be used
    for crypto.
    """
    hashes_per_fragment = FRAGMENT_LENGTH // Hash.LEN

    key_fragments = self.iter_chunks(FRAGMENT_LENGTH)

    # The digest will contain one hash per key fragment.
    digest = [0] * HASH_LENGTH * len(key_fragments)

    # Iterate over each fragment in the key.
    for (i, fragment) in enumerate(key_fragments): # type: Tuple[int, TryteString]
      fragment_trits = fragment.as_trits()

      key_fragment  = [0] * FRAGMENT_LENGTH
      hash_trits    = []

      # Within each fragment, iterate over one hash at a time.
      for j in range(hashes_per_fragment):
        hash_start  = j * HASH_LENGTH
        hash_end    = hash_start + HASH_LENGTH
        hash_trits  = fragment_trits[hash_start:hash_end] # type: MutableSequence[int]

        for k in range(26):
          sponge = Curl()
          sponge.absorb(hash_trits)
          sponge.squeeze(hash_trits)

        key_fragment[hash_start:hash_end] = hash_trits

      #
      # After processing all of the hashes in the fragment, generate a
      # final hash and append it to the digest.
      #
      # Note that we will do this once per fragment in the key, so the
      # longer the key is, the longer the digest will be.
      #
      sponge = Curl()
      sponge.absorb(key_fragment)
      sponge.squeeze(hash_trits)

      fragment_start  = i * FRAGMENT_LENGTH
      fragment_end    = fragment_start + FRAGMENT_LENGTH

      digest[fragment_start:fragment_end] = hash_trits

    return Digest(TryteString.from_trits(digest), self.key_index)
