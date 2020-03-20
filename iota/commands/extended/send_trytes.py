from typing import List, Optional

import filters as f

from iota import TransactionHash, TransactionTrytes, TryteString
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.attach_to_tangle import AttachToTangleCommand
from iota.commands.core.get_transactions_to_approve import \
    GetTransactionsToApproveCommand
from iota.commands.extended.broadcast_and_store import BroadcastAndStoreCommand
from iota.filters import Trytes

__all__ = [
    'SendTrytesCommand',
]


class SendTrytesCommand(FilterCommand):
    """
    Executes `sendTrytes` extended API command.

    See :py:meth:`iota.api.IotaApi.send_trytes` for more info.
    """
    command = 'sendTrytes'

    def get_request_filter(self):
        return SendTrytesRequestFilter()

    def get_response_filter(self):
        pass

    async def _execute(self, request: dict) -> dict:
        depth: int = request['depth']
        min_weight_magnitude: int = request['minWeightMagnitude']
        trytes: List[TryteString] = request['trytes']
        reference: Optional[TransactionHash] = request['reference']

        # Call ``getTransactionsToApprove`` to locate trunk and branch
        # transactions so that we can attach the bundle to the Tangle.
        gta_response = await GetTransactionsToApproveCommand(self.adapter)(
            depth=depth,
            reference=reference,
        )

        att_response = await AttachToTangleCommand(self.adapter)(
            branchTransaction=gta_response.get('branchTransaction'),
            trunkTransaction=gta_response.get('trunkTransaction'),

            minWeightMagnitude=min_weight_magnitude,
            trytes=trytes,
        )

        # ``trytes`` now have POW!
        trytes = att_response['trytes']

        await BroadcastAndStoreCommand(self.adapter)(trytes=trytes)

        return {
            'trytes': trytes,
        }


class SendTrytesRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(SendTrytesRequestFilter, self).__init__({
            'depth': f.Required | f.Type(int) | f.Min(1),

            'trytes':
                f.Required | f.Array | f.FilterRepeater(
                    f.Required | Trytes(TransactionTrytes),
                ),

            # Loosely-validated; devnet nodes require a different value
            # than mainnet.
            'minWeightMagnitude': f.Required | f.Type(int) | f.Min(1),

            'reference': Trytes(TransactionHash),
        },

            allow_missing_keys={
                'reference',
            })
