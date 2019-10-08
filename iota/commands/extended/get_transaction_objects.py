# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from typing import Iterable, List, Optional

import filters as f

from iota import Transaction, TransactionHash
from iota.commands.core import GetTrytesCommand
from iota.commands import FilterCommand, RequestFilter
from iota.filters import Trytes

__all__ = [
    'GetTransactionObjectsCommand',
]


class GetTransactionObjectsCommand(FilterCommand):
    """
    Executes `GetTransactionObjectsCommand` command.

    See :py:meth:`iota.api.StrictIota.get_transaction_objects`.
    """
    command = 'getTransactionObjects'

    def get_request_filter(self):
        return GetTransactionObjectsRequestFilter()

    def get_response_filter(self):
        pass

    def _execute(self, request):
        hashes = request\
            .get('hashes') # type: Optional[Iterable[TransactionHash]]

        transactions = []
        if hashes:
            gt_response = GetTrytesCommand(adapter=self.adapter)(hashes=hashes)

            transactions = list(map(
                Transaction.from_tryte_string,
                gt_response.get('trytes') or [],
            ))  # type: List[Transaction]

        return {
            'transactions': transactions,
        }

class GetTransactionObjectsRequestFilter(RequestFilter):
    def __init__(self):
        super(GetTransactionObjectsRequestFilter, self).__init__({
            'hashes':
                f.Required | f.Array | f.FilterRepeater(
                    f.Required |
                    Trytes(TransactionHash) |
                    f.Unicode(encoding='ascii', normalize=False),
                ),
        })