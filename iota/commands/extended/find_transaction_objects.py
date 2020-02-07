# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from typing import Iterable, List, Optional

from iota import Address, BundleHash, Tag, Transaction, TransactionHash
from iota.commands.core import GetTrytesCommand, FindTransactionsCommand

__all__ = [
    'FindTransactionObjectsCommand',
]


class FindTransactionObjectsCommand(FindTransactionsCommand):
    """
    Executes `FindTransactionObjects` command.

    See :py:meth:`iota.api.StrictIota.find_transaction_objects`.
    """
    command = 'findTransactionObjects'

    def get_response_filter(self):
        pass

    async def _execute(self, request):
        bundles = request\
            .get('bundles')  # type: Optional[Iterable[BundleHash]]
        addresses = request\
            .get('addresses')  # type: Optional[Iterable[Address]]
        tags = request\
            .get('tags')  # type: Optional[Iterable[Tag]]
        approvees = request\
            .get('approvees')  # type: Optional[Iterable[TransactionHash]]

        ft_response = await FindTransactionsCommand(adapter=self.adapter)(
            bundles=bundles,
            addresses=addresses,
            tags=tags,
            approvees=approvees,
        )

        hashes = ft_response['hashes']
        transactions = []
        if hashes:
            gt_response = await GetTrytesCommand(adapter=self.adapter)(hashes=hashes)

            transactions = list(map(
                Transaction.from_tryte_string,
                gt_response.get('trytes') or [],
            ))  # type: List[Transaction]

        return {
            'transactions': transactions,
        }
