from typing import List

import filters as f

from iota.commands import FilterCommand, RequestFilter
from iota.crypto.types import Digest
from iota.filters import Trytes
from iota.multisig.crypto.addresses import MultisigAddressBuilder

__all__ = [
    'CreateMultisigAddressCommand',
]


class CreateMultisigAddressCommand(FilterCommand):
    """
    Implements `create_multisig_address` multisig command.

    References:

    - :py:meth:`iota.multisig.api.MultisigIota.create_multisig_address`
    """
    command = 'createMultisigAddress'

    def get_request_filter(self) -> 'CreateMultisigAddressRequestFilter':
        return CreateMultisigAddressRequestFilter()

    def get_response_filter(self):
        pass

    # There is no async operation going on here, but the base class is async,
    # so from the outside, we have to act like we are doing async.
    async def _execute(self, request: dict) -> dict:
        digests: List[Digest] = request['digests']

        builder = MultisigAddressBuilder()

        for d in digests:
            builder.add_digest(d)

        return {
            'address': builder.get_address(),
        }


class CreateMultisigAddressRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(CreateMultisigAddressRequestFilter, self).__init__({
            'digests':
                f.Required | f.Array | f.FilterRepeater(
                    f.Required | Trytes(Digest),
                ),
        })
