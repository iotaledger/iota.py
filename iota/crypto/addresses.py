# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, Iterable, List, MutableSequence

from iota import Address, TRITS_PER_TRYTE, TryteString, TrytesCompatible
from iota.crypto import Curl
from iota.crypto.signing import KeyGenerator
from iota.crypto.types import PrivateKey
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

  def __init__(self, seed):
    # type: (TrytesCompatible) -> None
    super(AddressGenerator, self).__init__()

    self.seed = TryteString(seed)

  def __iter__(self):
    # type: () -> Generator[Address]
    """
    Returns a generator for creating new addresses, starting at index
    0 and potentially continuing on forever.
    """
    return self.create_generator()

  def get_addresses(self, start, count=1, step=1):
    # type: (int, int, int) -> List[Address]
    """
    Generates and returns one or more addresses at the specified
    index(es).

    This is a one-time operation; if you want to create lots of
    addresses across multiple contexts, consider invoking
    :py:meth:`create_generator` and sharing the resulting generator
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

    generator = self.create_generator(start, step)

    addresses = []
    for _ in range(count):
      try:
        next_key = next(generator)
      except StopIteration:
        break
      else:
        addresses.append(next_key)

    return addresses

  def create_generator(self, start=0, step=1):
    # type: (int, int) -> Generator[Address]
    """
    Creates a generator that can be used to progressively generate new
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
    if start < 0:
      raise with_context(
        exc = ValueError('``start`` cannot be negative.'),

        context = {
          'start':  start,
          'step':   step,
        },
      )

    digest_generator = self._create_digest_generator(start, step)

    current = start

    while current >= 0:
      yield self.address_from_digest(next(digest_generator), current)
      current += step

  @staticmethod
  def address_from_digest(digest_trits, key_index):
    # type: (Iterable[int], int) -> Address
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

  def _create_digest_generator(self, start, step):
    # type: (int, int) -> Generator[List[int]]
    """
    Initializes a generator to create PrivateKey digests.

    Implemented as a separate method so that it can be mocked during
    unit tests.
    """
    key_generator = (
      KeyGenerator(self.seed)
        .create_generator(start, step, iterations=self.DIGEST_ITERATIONS)
    )

    while True:
      signing_key = next(key_generator) # type: PrivateKey
      yield signing_key.get_digest_trits()
