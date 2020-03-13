from typing import List, Optional

from iota.crypto import HASH_LENGTH
from iota.crypto.kerl import Kerl
from iota.crypto.types import Digest
from iota.multisig.types import MultisigAddress

__all__ = [
    'MultisigAddressBuilder',
]


class MultisigAddressBuilder(object):
    """
    Creates multisig addresses.

    Note that this class generates a single address from multiple
    inputs (digests), unlike
    :py:class:`iota.crypto.addresses.AddressGenerator` which generates
    multiple addresses from a single input (seed).
    """

    def __init__(self) -> None:
        super(MultisigAddressBuilder, self).__init__()

        self._digests: List[Digest] = []
        """
        Keeps track of digests that were added, so that we can attach
        them to the final :py:class:`MultisigAddress` object.
        """

        self._address: Optional[MultisigAddress] = None
        """
        Caches the generated address.

        Generating the address modifies the internal state of the curl
        sponge, so each :py:class:`MultisigAddressBuilder` instance can
        only generate a single address.
        """

        self._sponge = Kerl()

    def add_digest(self, digest: Digest) -> None:
        """
        Absorbs a digest into the sponge.

        .. important::
            Keep track of the order that digests are added!

            To spend inputs from a multisig address, you must provide
            the private keys in the same order!

        References:

        - https://github.com/iotaledger/wiki/blob/master/multisigs.md#spending-inputs
        """
        if self._address:
            raise ValueError('Cannot add digests once an address is extracted.')

        self._sponge.absorb(digest.as_trits())
        self._digests.append(digest)

    def get_address(self) -> MultisigAddress:
        """
        Returns the new multisig address.

        Note that you can continue to add digests after extracting an
        address; the next address will use *all* of the digests that
        have been added so far.
        """
        if not self._digests:
            raise ValueError(
                'Must call ``add_digest`` at least once '
                'before calling ``get_address``.',
            )

        if not self._address:
            address_trits = [0] * HASH_LENGTH
            self._sponge.squeeze(address_trits)

            self._address = MultisigAddress.from_trits(
                address_trits,
                digests=self._digests[:],
            )

        return self._address
