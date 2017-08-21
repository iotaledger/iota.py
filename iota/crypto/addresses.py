# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, Iterable, List, MutableSequence

from iota import Address, TRITS_PER_TRYTE, TrytesCompatible
from iota.crypto.kerl import Kerl
from iota.crypto.signing import KeyGenerator, KeyIterator
from iota.crypto.types import Digest, PrivateKey, Seed
from iota.exceptions import with_context

__all__ = [
  'AddressGenerator',
]


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
  DEFAULT_SECURITY_LEVEL = 2
  """
  Default number of iterations to use when creating digests, used to create
  addresses.

  Note: this also impacts a few other things like length of transaction
  signatures.

  References:
    - :py:meth:`iota.transaction.ProposedBundle.sign_inputs`
    - :py:class:`iota.transaction.BundleValidator`
  """

  def __init__(self, seed, security_level=DEFAULT_SECURITY_LEVEL):
    # type: (TrytesCompatible, int) -> None
    super(AddressGenerator, self).__init__()

    self.security_level = security_level
    self.seed           = Seed(seed)

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
        next_addy = next(generator)
      except StopIteration:
        break
      else:
        addresses.append(next_addy)

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
        .create_iterator(start, step, self.security_level)
    )

    while True:
      yield self._generate_address(key_iterator)

  @staticmethod
  def address_from_digest(digest):
    # type: (Digest) -> Address
    """
    Generates an address from a private key digest.
    """
    address_trits = [0] * (Address.LEN * TRITS_PER_TRYTE) # type: MutableSequence[int]

    sponge = Kerl()
    sponge.absorb(digest.as_trits())
    sponge.squeeze(address_trits)

    return Address.from_trits(
      trits = address_trits,

      key_index       = digest.key_index,
      security_level  = digest.security_level,
    )

  def _generate_address(self, key_iterator):
    # type: (KeyIterator) -> Address
    """
    Generates a new address.

    Used in the event of a cache miss.
    """
    return self.address_from_digest(self._get_digest(key_iterator))

  @staticmethod
  def _get_digest(key_iterator):
    # type: (KeyIterator) -> Digest
    """
    Extracts parameters for :py:meth:`address_from_digest`.

    Split into a separate method so that it can be mocked during unit
    tests.
    """
    private_key = next(key_iterator) # type: PrivateKey
    return private_key.get_digest()
