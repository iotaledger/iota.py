# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.crypto import Curl, HASH_LENGTH
from iota.crypto.types import Digest
from iota.multisig.types import MultisigAddress

__all__ = [
  'MultisigAddressBuilder',
]


class MultisigAddressBuilder(object):
  """
  Creates multisig addresses.

  Note that this class generates a single address from multiple inputs,
  (digests) unlike :py:class:`iota.crypto.addresses.AddressGenerator`
  which generates multiple addresses from a single input (seed).
  """
  def __init__(self):
    super(MultisigAddressBuilder, self).__init__()

    self.sponge = Curl()
    self.digests = []

  def add_digest(self, digest):
    # type: (Digest) -> None
    """
    Absorbs a digest into the sponge.

    IMPORTANT: Keep track of the order that digests are added!
    To spend inputs from a multisig address, you must provide the
    private keys in the same order!

    References:
      - https://github.com/iotaledger/wiki/blob/master/multisigs.md#spending-inputs
    """
    self.sponge.absorb(digest.as_trits())
    self.digests.append(digest)

  def get_address(self):
    # type: () -> MultisigAddress
    """
    Returns the new multisig address.

    Note that you can continue to add digests after extracting an
    address; the next address will use *all* of the digests that have
    been added so far.
    """
    if not self.digests:
      raise ValueError(
        'Must call ``add_digest`` at least once '
        'before calling ``get_address``.',
      )

    address_trits = [0] * HASH_LENGTH
    self.sponge.squeeze(address_trits)
    return MultisigAddress.from_trits(address_trits, digests=self.digests[:])
