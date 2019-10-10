# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from typing import List, Optional

import filters as f

from iota import Address
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.find_transactions import FindTransactionsCommand
from iota.commands.core.get_balances import GetBalancesCommand
from iota.commands.core.were_addresses_spent_from import \
    WereAddressesSpentFromCommand
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed
from iota.filters import SecurityLevel, Trytes

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

    def _execute(self, request):
        checksum = request['checksum']  # type: bool
        count = request['count']  # type: Optional[int]
        index = request['index']  # type: int
        security_level = request['securityLevel']  # type: int
        seed = request['seed']  # type: Seed

        return {
            'addresses':
                self._find_addresses(
                    seed,
                    index,
                    count,
                    security_level,
                    checksum,
                ),
        }

    def _find_addresses(self, seed, index, count, security_level, checksum):
        # type: (Seed, int, Optional[int], int, bool) -> List[Address]
        """
        Find addresses matching the command parameters.
        """
        generator = AddressGenerator(seed, security_level, checksum)

        if count is None:
            # Connect to Tangle and find the first unused address.
            for addy in generator.create_iterator(start=index):
                # We use addy.address here because the commands do
                # not work on an address with a checksum
                response = WereAddressesSpentFromCommand(self.adapter)(
                    addresses=[addy.address],
                )
                if response['states'][0]:
                    continue

                response = GetBalancesCommand(self.adapter)(
                    addresses=[addy.address],
                )
                if response['balances'][0] != 0:
                    continue

                response = FindTransactionsCommand(self.adapter)(
                    addresses=[addy.address],
                )
                if response.get('hashes'):
                    continue

                return [addy]

        return generator.get_addresses(start=index, count=count)


class GetNewAddressesRequestFilter(RequestFilter):
    def __init__(self):
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
