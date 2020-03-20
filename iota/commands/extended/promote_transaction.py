import filters as f

from iota import Address, BadApiResponse, ProposedTransaction, TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.check_consistency import CheckConsistencyCommand
from iota.commands.extended.send_transfer import SendTransferCommand
from iota.filters import Trytes

__all__ = [
    'PromoteTransactionCommand',
]


class PromoteTransactionCommand(FilterCommand):
    """
    Executes ``promoteTransaction`` extended API command.

    See :py:meth:`iota.api.Iota.promote_transaction` for more
    information.
    """
    command = 'promoteTransaction'

    def get_request_filter(self):
        return PromoteTransactionRequestFilter()

    def get_response_filter(self):
        pass

    async def _execute(self, request: dict) -> dict:
        depth: int = request['depth']
        min_weight_magnitude: int = request['minWeightMagnitude']
        transaction: TransactionHash = request['transaction']

        cc_response = await CheckConsistencyCommand(self.adapter)(tails=[transaction])
        if cc_response['state'] is False:
            raise BadApiResponse(
                'Transaction {transaction} is not promotable. '
                'Info: {reason}'.format(transaction=transaction, reason=cc_response['info'])
            )

        spam_transfer = ProposedTransaction(
            address=Address(b''),
            value=0,
        )

        return await SendTransferCommand(self.adapter)(
            seed=spam_transfer.address,
            depth=depth,
            transfers=[spam_transfer],
            minWeightMagnitude=min_weight_magnitude,
            reference=transaction,
        )


class PromoteTransactionRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(PromoteTransactionRequestFilter, self).__init__({
            'depth': f.Required | f.Type(int) | f.Min(1),
            'transaction': f.Required | Trytes(TransactionHash),

            # Loosely-validated; devnet nodes require a different value
            # than mainnet.
            'minWeightMagnitude': f.Required | f.Type(int) | f.Min(1),
        })
