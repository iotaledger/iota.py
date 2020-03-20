import filters as f

from iota import TransactionTrytes
from iota.commands import FilterCommand, RequestFilter
from iota.filters import StringifiedTrytesArray

__all__ = [
    'BroadcastTransactionsCommand',
]


class BroadcastTransactionsCommand(FilterCommand):
    """
    Executes `broadcastTransactions` command.

    See :py:meth:`iota.api.StrictIota.broadcast_transactions`.
    """
    command = 'broadcastTransactions'

    def get_request_filter(self):
        return BroadcastTransactionsRequestFilter()

    def get_response_filter(self):
        pass


class BroadcastTransactionsRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(BroadcastTransactionsRequestFilter, self).__init__({
            'trytes': StringifiedTrytesArray(TransactionTrytes) | f.Required,
        })
