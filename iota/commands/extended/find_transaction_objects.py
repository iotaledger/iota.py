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

    async def _execute(self, request: dict) -> dict:
        bundles: Optional[Iterable[BundleHash]] = request\
            .get('bundles')
        addresses: Optional[Iterable[Address]] = request\
            .get('addresses')
        tags: Optional[Iterable[Tag]] = request\
            .get('tags')
        approvees: Optional[Iterable[TransactionHash]] = request\
            .get('approvees')

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

            transactions: List[Transaction] = list(map(
                Transaction.from_tryte_string,
                gt_response.get('trytes') or [],
            ))

        return {
            'transactions': transactions,
        }
