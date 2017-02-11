# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Iterator, List, MutableSequence, Sequence, Tuple

from six import PY2

from iota import TRITS_PER_TRYTE, TryteString, TrytesCompatible, Hash
from iota.crypto import Curl, FRAGMENT_LENGTH, HASH_LENGTH
from iota.crypto.types import PrivateKey, Seed
from iota.exceptions import with_context

__all__ = [
  'KeyGenerator',
  'SignatureFragmentGenerator',
  'validate_signature_fragments',
]


def normalize(hash_):
  # type: (Hash) -> List[List[int]]
  """
  "Normalizes" a hash, converting it into a sequence of integers
  (not trits!) suitable for use in signature generation/validation.

  The hash is divided up into 3 parts, each of which is "balanced" (sum
  of all the values is equal to zero).
  """
  normalized  = []
  source      = hash_.as_integers()

  chunk_size = 27

  for i in range(Hash.LEN // chunk_size):
    start = i * chunk_size
    stop  = start + chunk_size

    chunk     = source[start:stop]
    chunk_sum = sum(chunk)

    while chunk_sum > 0:
      chunk_sum -= 1
      for j in range(chunk_size):
        if chunk[j] > -13:
          chunk[j] -= 1
          break


    while chunk_sum < 0:
      chunk_sum += 1
      for j in range(chunk_size):
        if chunk[j] < 13:
          chunk[j] += 1
          break

    normalized.append(chunk)

  return normalized


class KeyGenerator(object):
  """
  Generates signing keys for messages.
  """
  def __init__(self, seed):
    # type: (TrytesCompatible) -> None
    super(KeyGenerator, self).__init__()

    self.seed = Seed(seed)

  def get_keys(self, start, count=1, step=1, iterations=1):
    # type: (int, int, int, int) -> List[PrivateKey]
    """
    Generates and returns one or more keys at the specified index(es).

    This is a one-time operation; if you want to create lots of keys
    across multiple contexts, consider invoking
    :py:meth:`create_iterator` and sharing the resulting generator
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

    iterator = self.create_iterator(start, step, iterations)

    keys = []
    for _ in range(count):
      try:
        next_key = next(iterator)
      except StopIteration:
        break
      else:
        keys.append(next_key)

    return keys

  def create_iterator(self, start=0, step=1, iterations=1):
    # type: (int, int) -> KeyIterator
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
    return KeyIterator(self.seed, start, step, iterations)


class KeyIterator(Iterator[PrivateKey]):
  """
  Creates PrivateKeys from a set of iteration parameters.
  """
  def __init__(self, seed, start, step, iterations):
    # type: (Seed, int, int, int) -> None
    super(KeyIterator, self).__init__()

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

    self.seed       = seed
    self.start      = start
    self.step       = step
    self.iterations = iterations

    self.current = self.start

    self.fragment_length     = FRAGMENT_LENGTH * TRITS_PER_TRYTE
    self.hashes_per_fragment = FRAGMENT_LENGTH // Hash.LEN

  def __iter__(self):
    # type: () -> KeyIterator
    return self

  def __next__(self):
    # type: () -> PrivateKey
    while self.current >= 0:
      sponge = self._create_sponge(self.current)

      key     = [0] * (self.fragment_length * self.iterations)
      buffer  = [0] * HASH_LENGTH # type: MutableSequence[int]

      for fragment_seq in range(self.iterations):
        # Squeeze trits from the buffer and append them to the key, one
        # hash at a time.
        for hash_seq in range(self.hashes_per_fragment):
          sponge.squeeze(buffer)

          key_start =\
            (fragment_seq * self.fragment_length) + (hash_seq * HASH_LENGTH)

          key_stop = key_start + HASH_LENGTH

          key[key_start:key_stop] = buffer

      private_key = PrivateKey.from_trits(key)
      private_key.key_index = self.current

      self.current += self.step

      return private_key

  if PY2:
    next = __next__

  def _create_sponge(self, index):
    # type: (int) -> Curl
    """
    Prepares the Curl sponge for the generator.
    """
    seed = self.seed.as_trits() # type: MutableSequence[int]

    for i in range(index):
      # Treat ``seed`` like a really big number and add ``index``.
      # Note that addition works a little bit differently in balanced
      # ternary.
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


class SignatureFragmentGenerator(Iterator[TryteString]):
  """
  Used to generate signature fragments progressively.

  Each instance can generate 1 signature per fragment in the private
  key.
  """
  def __init__(self, private_key, hash_):
    # type: (PrivateKey, TryteString) -> None
    super(SignatureFragmentGenerator, self).__init__()

    self._key_chunks      = private_key.iter_chunks(FRAGMENT_LENGTH)
    self._iteration       = -1
    self._normalized_hash = normalize(hash_)
    self._sponge          = Curl()

  def __iter__(self):
    # type: () -> SignatureFragmentGenerator
    return self

  def __len__(self):
    # type: () -> int
    """
    Returns the number of fragments this generator can create.

    Note: This method always returns the same result, no matter how
    many iterations have been completed.
    """
    return len(self._key_chunks)

  def __next__(self):
    # type: () -> TryteString
    """
    Returns the next signature fragment.
    """
    key_trytes = next(self._key_chunks) # type: TryteString
    self._iteration += 1

    # If the key is long enough, loop back around to the start.
    normalized_chunk =\
      self._normalized_hash[self._iteration % len(self._normalized_hash)]

    signature_fragment = key_trytes.as_trits()

    # Build the signature, one hash at a time.
    for i in range(key_trytes.count_chunks(Hash.LEN)):
      hash_start  = i * HASH_LENGTH
      hash_end    = hash_start + HASH_LENGTH

      buffer = signature_fragment[hash_start:hash_end] # type: MutableSequence[int]

      for _ in range(13 - normalized_chunk[i]):
        self._sponge.reset()
        self._sponge.absorb(buffer)
        self._sponge.squeeze(buffer)

      signature_fragment[hash_start:hash_end] = buffer

    return TryteString.from_trits(signature_fragment)

  if PY2:
    next = __next__


def validate_signature_fragments(fragments, hash_, public_key):
  # type: (Sequence[TryteString], Hash, TryteString) -> bool
  """
  Returns whether a sequence of signature fragments is valid.

  :param fragments:
    Sequence of signature fragments (usually
    :py:class:`iota.transaction.Fragment` instances).

  :param hash_:
    Hash used to generate the signature fragments (usually a
    :py:class:`iota.transaction.BundleHash` instance).

  :param public_key:
    The public key value used to verify the signature digest (usually a
    :py:class:`iota.types.Address` instance).
  """
  checksum        = [0] * (HASH_LENGTH * len(fragments))
  normalized_hash = normalize(hash_)

  for (i, fragment) in enumerate(fragments): # type: Tuple[int, TryteString]
    outer_sponge = Curl()

    # If there are more than 3 iterations, loop back around to the
    # start.
    normalized_chunk = normalized_hash[i % len(normalized_hash)]

    buffer = []
    for (j, hash_trytes) in enumerate(fragment.iter_chunks(Hash.LEN)): # type: Tuple[int, TryteString]
      buffer        = hash_trytes.as_trits() # type: MutableSequence[int]
      inner_sponge  = Curl()

      # Note the sign flip compared to ``SignatureFragmentGenerator``.
      for _ in range(13 + normalized_chunk[j]):
        inner_sponge.reset()
        inner_sponge.absorb(buffer)
        inner_sponge.squeeze(buffer)

      outer_sponge.absorb(buffer)

    outer_sponge.squeeze(buffer)
    checksum[i*HASH_LENGTH:(i+1)*HASH_LENGTH] = buffer

  actual_public_key = [0] * HASH_LENGTH # type: MutableSequence[int]
  addy_sponge = Curl()
  addy_sponge.absorb(checksum)
  addy_sponge.squeeze(actual_public_key)

  return actual_public_key == public_key.as_trits()
