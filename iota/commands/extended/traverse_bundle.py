from typing import List, Optional

import filters as f

from iota import BadApiResponse, Transaction, \
    TransactionHash, TryteString, Bundle, TransactionTrytes
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.get_trytes import GetTrytesCommand
from iota.exceptions import with_context
from iota.filters import Trytes

__all__ = [
    'TraverseBundleCommand',
]


class TraverseBundleCommand(FilterCommand):
    """
    Executes ``traverseBundle`` extended API command.

    See :py:meth:`iota.api.Iota.traverse_bundle` for more info.
    """
    command = 'traverseBundle'

    def get_request_filter(self):
        return TraverseBundleRequestFilter()

    def get_response_filter(self):
        pass

    async def _execute(self, request: dict) -> dict:
        txn_hash: TransactionHash = request['transaction']

        bundle = Bundle(await self._traverse_bundle(txn_hash, None))

        # No bundle validation

        return {
            'bundles': [bundle]
        }

    async def _traverse_bundle(
            self,
            txn_hash: TransactionHash,
            target_bundle_hash: Optional[TransactionHash]
    ) -> List[Transaction]:
        """
        Recursively traverse the Tangle, collecting transactions until
        we hit a new bundle.

        This method is (usually) faster than ``findTransactions``, and
        it ensures we don't collect transactions from replayed bundles.
        """
        trytes: List[TryteString] = (await GetTrytesCommand(self.adapter)(
            hashes=[txn_hash])
        )['trytes']

        # If no tx was found by the node for txn_hash, it returns 9s,
        # so we check here if it returned all 9s trytes.
        if not trytes or trytes == [TransactionTrytes('')]:
            raise with_context(
                exc=BadApiResponse(
                    'Could not get trytes of bundle transaction from the Tangle. '
                    'Bundle transactions not visible.'
                    '(``exc.context`` has more info).',
                ),

                context={
                    'transaction_hash': txn_hash,
                    'target_bundle_hash': target_bundle_hash,
                },
            )

        transaction = Transaction.from_tryte_string(trytes[0])

        if (not target_bundle_hash) and transaction.current_index:
            raise with_context(
                exc=BadApiResponse(
                    '``_traverse_bundle`` started with a non-tail transaction '
                    '(``exc.context`` has more info).',
                ),

                context={
                    'transaction_object': transaction,
                    'target_bundle_hash': target_bundle_hash,
                },
            )

        if target_bundle_hash:
            if target_bundle_hash != transaction.bundle_hash:
                # We've hit a different bundle; we can stop now.
                return []
        else:
            target_bundle_hash = transaction.bundle_hash

        if transaction.current_index == transaction.last_index == 0:
            # Bundle only has one transaction.
            return [transaction]

        # Recursively follow the trunk transaction, to fetch the next
        # transaction in the bundle.
        return [transaction] + await self._traverse_bundle(
            transaction.trunk_transaction_hash,
            target_bundle_hash
        )


class TraverseBundleRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(TraverseBundleRequestFilter, self).__init__({
            'transaction': f.Required | Trytes(TransactionHash),
        })
