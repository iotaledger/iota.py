from typing import Iterable, List

import filters as f

from iota import Transaction, TransactionHash
from iota.commands.core import GetTrytesCommand
from iota.commands import FilterCommand, RequestFilter
from iota.filters import StringifiedTrytesArray

__all__ = [
    'GetTransactionObjectsCommand',
]


class GetTransactionObjectsCommand(FilterCommand):
    """
    Executes `GetTransactionObjectsCommand` command.

    See :py:meth:`iota.api.Iota.get_transaction_objects`.
    """
    command = 'getTransactionObjects'

    def get_request_filter(self):
        return GetTransactionObjectsRequestFilter()

    def get_response_filter(self):
        pass

    async def _execute(self, request: dict) -> dict:
        hashes: Iterable[TransactionHash] = request\
            .get('hashes')

        transactions = []
        if hashes:
            gt_response = await GetTrytesCommand(adapter=self.adapter)(hashes=hashes)

            transactions: List[Transaction] = list(map(
                Transaction.from_tryte_string,
                gt_response.get('trytes') or [],
            ))

        return {
            'transactions': transactions,
        }


class GetTransactionObjectsRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(GetTransactionObjectsRequestFilter, self).__init__({
            'hashes':
                StringifiedTrytesArray(TransactionHash) | f.Required
        })
