from typing import Optional

from iota.commands import FilterCommand, RequestFilter
from iota.commands.core import CheckConsistencyCommand, GetTrytesCommand
from iota.transaction import Transaction
from iota import TransactionHash
import filters as f
from iota.filters import Trytes
import time

__all__ = [
    'IsPromotableCommand',
]

MILESTONE_INTERVAL = 2 * 60 * 1000
"""
Approximate interval in which a milestone is issued.
Unit is in milliseconds, so it is roughly 2 minutes.
"""

ONE_WAY_DELAY = 1 * 60 * 1000
"""
Propagation delay of the network (ms). (really-really worst case scenario)
The time needed for the message to propegate from client to edges of
majority network.
"""

DEPTH = 6
"""
The number of milestones issued since `attachmentTimestamp`.
"""

get_current_ms = lambda : int(round(time.time() * 1000))
"""
Calculate current time in milliseconds.
"""


class IsPromotableCommand(FilterCommand):
    """
    Determines if a tail transaction is promotable.

    See :py:meth:`iota.api.Iota.is_promotable` for more info.
    """
    command = 'isPromotable'

    def get_request_filter(self):
        return IsPromotableRequestFilter()

    def get_response_filter(self):
        pass

    async def _execute(self, request: dict) -> dict:
        tails: TransactionHash = request['tails']

        # First, check consistency
        # A transaction is consistent, if:
        #  - The node isn't missing the transaction's branch or trunk transactions
        #  - The transaction's bundle is valid
        #  - The transaction's branch and trunk transactions are valid
        cc_response = await CheckConsistencyCommand(self.adapter)(
            tails=tails,
        )

        if not cc_response['state']:
            # One or more transactions are inconsistent
            return {
                'promotable': False,
                'info': cc_response['info'],
            }
      
        transactions = [
            Transaction.from_tryte_string(x) for x in
            (await GetTrytesCommand(self.adapter)(hashes=tails))['trytes']
        ]

        response = {
            'promotable': True,
            'info': [],
        }

        # Check timestamps
        now = get_current_ms()
        for tx in transactions:
            is_within = is_within_depth(tx.attachment_timestamp, now)
            if not is_within:
                # Inform the user about what went wrong.
                response['info'].append('Transaction {tx_hash} is above max depth.'.format(
                    tx_hash=tx.hash
                ))
            # If one tx fails, response is false
            response['promotable'] = response['promotable'] and is_within

        # If there are no problems, we don't need 'info' field
        # Delete info field to make it consistent with check_consistency response.
        if response['promotable']:
            del response['info']

        return response


class IsPromotableRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(IsPromotableRequestFilter, self).__init__({
            'tails':
                f.Required |
                f.Array |
                f.FilterRepeater(f.Required | Trytes(TransactionHash)),
        })


def is_within_depth(
        attachment_timestamp: int,
        now: int,
        depth: Optional[int] = DEPTH
):
    """
    Checks if `attachment_timestamp` is within limits of `depth`.
    """
    return attachment_timestamp < now and \
        now - attachment_timestamp < depth * MILESTONE_INTERVAL - ONE_WAY_DELAY
