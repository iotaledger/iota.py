# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import filters as f
from iota.filters import Trytes

from iota import TransactionTrytes, TransactionHash
from iota.commands.core import \
    BroadcastTransactionsCommand
from iota.commands.extended.get_bundles import GetBundlesCommand
from iota.commands import FilterCommand, RequestFilter

__all__ = [
    'BroadcastBundleCommand',
]


class BroadcastBundleCommand(FilterCommand):
    """
    Executes ``broadcastBundle`` extended API command.

    See :py:meth:`iota.api.Iota.broadcast_bundle` for more info.
    """
    command = 'broadcastBundle'

    def get_request_filter(self):
        return BroadcastBundleRequestFilter()

    def get_response_filter(self):
        # Return value is filtered before hitting us.
        pass

    async def _execute(self, request):
        # Given tail hash, fetches the bundle from the tangle
        # and validates it.
        # Returns List[List[TransactionTrytes]]
        # (outer list has one item in current implementation)
        bundle = await GetBundlesCommand(self.adapter)(transactions=[request['tail_hash']])
        await BroadcastTransactionsCommand(self.adapter)(trytes=bundle[0])
        return {
            'trytes': bundle[0],
        }

class BroadcastBundleRequestFilter(RequestFilter):
    def __init__(self):
        super(BroadcastBundleRequestFilter, self).__init__({
            'tail_hash': f.Required | Trytes(TransactionHash),
        })