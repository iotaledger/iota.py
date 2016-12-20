# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, Iterable, List, MutableSequence, Optional, Union

from iota import Address, TryteString, TrytesCompatible
from iota.crypto import Curl
from iota.crypto.signing import KeyGenerator, SigningKey

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

  def __init__(self, seed):
    # type: (TrytesCompatible) -> None
    super(AddressGenerator, self).__init__()

    self.seed = TryteString(seed)

  def __getitem__(self, slice_):
    # type: (Union[int, slice]) -> Union[Address, List[Address]]
    """
    Generates and returns one or more addresses at the specified
    index(es).

    :param slice_:
      Index of address to generate, or a slice.

      Warning: This method may take awhile to run if the requested
      index(es) is a large number!

    :return:
      Behavior matches slicing behavior of other collections:

      - If an int is provided, a single address will be returned.
      - If a slice is provided, a list of addresses will be returned.
    """
    return (
      self.get_addresses(slice_.start, slice_.stop, slice_.step)
        if isinstance(slice_, slice)
        else self.get_addresses(slice_)[0]
    )

  def __iter__(self):
    # type: () -> Generator[Address]
    """
    Returns a generator for creating new addresses, starting at index
    0 and potentially continuing on forever.
    """
    return self.create_generator(0)

  def get_addresses(self, start, stop=None, step=1):
    # type: (int, Optional[int], int) -> List[Address]
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

    :param stop:
      Stop before this index.  This value must be positive.
      If ``None`` (default), only generate a single address.

    :param step:
      Number of indexes to advance after each address.

    :return:
      Always returns a list, even if only one address is generated.
    """
    generator = self.create_generator(start, step)
    interval  = range(start, start+1 if stop is None else stop, step)

    addresses = []
    for _ in interval:
      try:
        next_key = next(generator)
      except StopIteration:
        break
      else:
        addresses.append(next_key)

    return addresses

  def create_generator(self, start, step=1):
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
    key_generator = (
      KeyGenerator(self.seed)
        .create_generator(start, step, iterations=self.DIGEST_ITERATIONS)
    )

    while True:
      signing_key = next(key_generator) # type: SigningKey
      digest      = signing_key.get_digest_trits()

      # Multiply by 3 to convert from trits to trytes.
      address_trits = [0] * (Address.LEN * 3) # type: MutableSequence[int]

      sponge = Curl()
      sponge.absorb(digest)
      sponge.squeeze(address_trits)

      yield Address.from_trits(address_trits)
