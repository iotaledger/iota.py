from operator import attrgetter
from typing import Iterable, Optional

from iota import Address, TrytesCompatible
from iota.crypto.types import Digest

__all__ = [
    'MultisigAddress',
]


class MultisigAddress(Address):
    """
    An address that was generated using digests from multiple private
    keys.

    In order to spend inputs from a multisig address, the same private
    keys must be used, in the same order that the corresponding digests
    were used to generate the address.

    .. note::
        Usually, you don't have to create a MultisigAddress manually. Use
        :py:meth:`~iota.multisig.MultisigIota.create_multisig_address` to
        derive an address from a list of digests.

    :py:class:`MultisigAddress` is a subclass of
    :py:class:`iota.Address`, so you can use all the regular
    :py:class:`iota.Address` methods on a :py:class:`MultisigAddress`
    object.

    :param TrytesCompatible trytes:
        Address trytes (81 trytes long).

    :param Iterable[Digest] digests:
        List of digests that were used to create the address.
        Order is important!

    :param Optional[int] balance:
        Available balance of the address.

    :return:
        :py:class:`MultisigAddress` object.
    """

    def __init__(
            self,
            trytes: TrytesCompatible,
            digests: Iterable[Digest],
            balance: Optional[int] = None
    ) -> None:
        # Key index is meaningless for multisig addresses.
        super(MultisigAddress, self).__init__(trytes, balance, key_index=None)

        self.digests = digests

        self.security_level = sum(
            map(attrgetter('security_level'), self.digests)
        )

    def as_json_compatible(self) -> dict:
        """
        Get a JSON represenation of the :py:class:`MultisigAddress` object.

        :return:
            ``dict`` with the following structure::

                {
                    'trytes': str,
                        String representation of the address trytes.
                    'balance': int,
                        Balance of the address.
                    'digests': Iterable[Digest]
                        Digests that were used to create the address.
                }

        """
        return {
            'trytes': self._trytes.decode('ascii'),
            'balance': self.balance,
            'digests': self.digests,
        }
