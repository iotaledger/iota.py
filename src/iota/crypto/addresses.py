# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import hashlib
from abc import ABCMeta, abstractmethod as abstract_method
from typing import Dict, Generator, Iterable, List, MutableSequence, Optional

from iota import Address, TRITS_PER_TRYTE, TrytesCompatible
from iota.crypto import Curl
from iota.crypto.signing import KeyGenerator, KeyIterator
from iota.crypto.types import PrivateKey, Seed
from iota.exceptions import with_context
from six import binary_type, with_metaclass

__all__ = [
  'AddressGenerator',
  'MemoryAddressCache',
]


class BaseAddressCache(with_metaclass(ABCMeta)):
  """
  Base functionality for classes that cache generated addresses.
  """
  @abstract_method
  def get(self, seed, index):
    # type: (Seed, int) -> Optional[Address]
    """
    Retrieves an address from the cache.
    Returns ``None`` if the address hasn't been cached yet.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )

  @abstract_method
  def set(self, seed, index, address):
    # type: (Seed, int, Address) -> None
    """
    Adds an address to the cache, overwriting the existing address if
    set.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class MemoryAddressCache(BaseAddressCache):
  """
  Caches addresses in memory.
  """
  def __init__(self):
    super(MemoryAddressCache, self).__init__()

    self.cache = {} # type: Dict[binary_type, Address]

  def get(self, seed, index):
    # type: (Seed, int) -> Optional[Address]
    return self.cache.get(self._gen_cache_key(seed, index))

  def set(self, seed, index, address):
    # type: (Seed, int, Address) -> None
    self.cache[self._gen_cache_key(seed, index)] = address

  @staticmethod
  def _gen_cache_key(seed, index):
    # type: (Seed, int) -> binary_type
    """
    Generates an obfuscated cache key so that we're not storing seeds
    in cleartext.
    """
    h = hashlib.new('sha256')
    h.update(binary_type(seed) + b':' + binary_type(index))
    return h.digest()


class AddressGenerator(Iterable[Address]):
  """
  Generates new addresses using a standard algorithm.

  Note: This class does not check if addresses have already been used;
  if you want to exclude used addresses, invoke
  :py:meth:`iota.api.IotaApi.get_new_addresses` instead.

  Note also that :py:meth:`iota.api.IotaApi.get_new_addresses` uses
  ``AddressGenerator`` internally, so you get the best of both worlds
  when you use the API (:
  """
  DIGEST_ITERATIONS = 2
  """
  Number of iterations to use when creating digests, used to create
  addresses.

  Note: this also impacts a few other things like length of transaction
  signatures.

  References:
    - :py:meth:`iota.transaction.ProposedBundle.sign_inputs`
    - :py:class:`iota.transaction.BundleValidator`
  """

  cache = None # type: BaseAddressCache
  """
  Set a the instance or class level to inject a cache into the address
  generation process.
  """

  def __init__(self, seed):
    # type: (TrytesCompatible) -> None
    super(AddressGenerator, self).__init__()

    self.seed = Seed(seed)

  def __iter__(self):
    # type: () -> Generator[Address]
    """
    Returns a generator for creating new addresses, starting at index
    0 and potentially continuing on forever.
    """
    return self.create_iterator()

  def get_addresses(self, start, count=1, step=1):
    # type: (int, int, int) -> List[Address]
    """
    Generates and returns one or more addresses at the specified
    index(es).

    This is a one-time operation; if you want to create lots of
    addresses across multiple contexts, consider invoking
    :py:meth:`create_iterator` and sharing the resulting generator
    object instead.

    Warning: This method may take awhile to run if the starting index
    and/or the number of requested addresses is a large number!

    :param start:
      Starting index.
      Must be >= 0.

    :param count:
      Number of addresses to generate.
      Must be > 0.

    :param step:
      Number of indexes to advance after each address.
      This may be any non-zero (positive or negative) integer.

    :return:
      Always returns a list, even if only one address is generated.

      The returned list will contain ``count`` addresses, except when
      ``step * count < start`` (only applies when ``step`` is
      negative).
    """
    if count < 1:
      raise with_context(
        exc = ValueError('``count`` must be positive.'),

        context = {
          'start':  start,
          'count':  count,
          'step':   step,
        },
      )

    if not step:
      raise with_context(
        exc = ValueError('``step`` must not be zero.'),

        context = {
          'start':  start,
          'count':  count,
          'step':   step,
        },
      )

    generator = self.create_iterator(start, step)

    addresses = []
    for _ in range(count):
      try:
        next_key = next(generator)
      except StopIteration:
        break
      else:
        addresses.append(next_key)

    return addresses

  def create_iterator(self, start=0, step=1):
    # type: (int, int) -> Generator[Address]
    """
    Creates an iterator that can be used to progressively generate new
    addresses.

    :param start:
      Starting index.

      Warning: This method may take awhile to reset if ``start``
      is a large number!

    :param step:
      Number of indexes to advance after each address.

      Warning: The generator may take awhile to advance between
      iterations if ``step`` is a large number!
    """
    key_iterator = (
      KeyGenerator(self.seed)
        .create_iterator(start, step, iterations=self.DIGEST_ITERATIONS)
    )

    while True:
      if self.cache:
        address = self.cache.get(self.seed, key_iterator.current)

        if not address:
          address = self._generate_address(key_iterator)
          self.cache.set(self.seed, address.key_index, address)
      else:
        address = self._generate_address(key_iterator)

      yield address

  @staticmethod
  def address_from_digest(digest_trits, key_index):
    # type: (List[int], int) -> Address
    """
    Generates an address from a private key digest.
    """
    address_trits = [0] * (Address.LEN * TRITS_PER_TRYTE) # type: MutableSequence[int]

    sponge = Curl()
    sponge.absorb(digest_trits)
    sponge.squeeze(address_trits)

    address = Address.from_trits(address_trits)
    address.key_index = key_index

    return address

  def _generate_address(self, key_iterator):
    # type: (KeyIterator) -> Address
    """
    Generates a new address.

    Used in the event of a cache miss.
    """
    return self.address_from_digest(*self._get_digest_params(key_iterator))

  @staticmethod
  def _get_digest_params(key_iterator):
    # type: (KeyIterator) -> Tuple[List[int], int]
    """
    Extracts parameters for :py:meth:`address_from_digest`.

    Split into a separate method so that it can be mocked during unit
    tests.
    """
    private_key = next(key_iterator) # type: PrivateKey
    return private_key.get_digest_trits(), private_key.key_index
