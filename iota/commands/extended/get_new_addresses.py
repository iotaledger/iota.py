from typing import List, Optional

import filters as f

from iota import Address
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.find_transactions import FindTransactionsCommand
from iota.commands.core.were_addresses_spent_from import \
    WereAddressesSpentFromCommand
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed
from iota.filters import SecurityLevel, Trytes
import asyncio

__all__ = [
    'GetNewAddressesCommand',
]


class GetNewAddressesCommand(FilterCommand):
    """
    Executes ``getNewAddresses`` extended API command.

    See :py:meth:`iota.api.Iota.get_new_addresses` for more info.
    """
    command = 'getNewAddresses'

    def get_request_filter(self):
        return GetNewAddressesRequestFilter()

    def get_response_filter(self):
        pass

    async def _execute(self, request: dict) -> dict:
        checksum: bool = request['checksum']
        count: Optional[int] = request['count']
        index: int = request['index']
        security_level: int = request['securityLevel']
        seed: Seed = request['seed']

        return {
            'addresses':
                await self._find_addresses(
                    seed,
                    index,
                    count,
                    security_level,
                    checksum,
                ),
        }

    async def _find_addresses(
            self,
            seed: Seed,
            index: int,
            count: Optional[int],
            security_level: int,
            checksum: bool
    ) -> List[Address]:
        """
        Find addresses matching the command parameters.
        """
        generator = AddressGenerator(seed, security_level, checksum)

        if count is None:
            # Connect to Tangle and find the first unused address.
            for addy in generator.create_iterator(start=index):
                # We use addy.address here because the commands do
                # not work on an address with a checksum
                # Execute two checks concurrently
                responses = await asyncio.gather(
                    WereAddressesSpentFromCommand(self.adapter)(
                        addresses=[addy.address],
                    ),
                    FindTransactionsCommand(self.adapter)(
                        addresses=[addy.address],
                    ),
                )
                # responses[0] -> was it spent from?
                # responses[1] -> any transaction found?
                if responses[0]['states'][0] or responses[1].get('hashes'):
                    continue

                return [addy]

        return generator.get_addresses(start=index, count=count)


class GetNewAddressesRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(GetNewAddressesRequestFilter, self).__init__(
            {
                # Everything except ``seed`` is optional.
                'checksum': f.Type(bool) | f.Optional(default=False),
                'count': f.Type(int) | f.Min(1),
                'index': f.Type(int) | f.Min(0) | f.Optional(default=0),
                'securityLevel': SecurityLevel,

                'seed': f.Required | Trytes(Seed),
            },

            allow_missing_keys={
                'checksum',
                'count',
                'index',
                'securityLevel',
            },
        )
