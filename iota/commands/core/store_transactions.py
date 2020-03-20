import filters as f

from iota import TransactionTrytes
from iota.commands import FilterCommand, RequestFilter
from iota.filters import StringifiedTrytesArray

__all__ = [
    'StoreTransactionsCommand',
]


class StoreTransactionsCommand(FilterCommand):
    """
    Executes ``storeTransactions`` command.

    See :py:meth:`iota.api.StrictIota.store_transactions`.
    """
    command = 'storeTransactions'

    def get_request_filter(self):
        return StoreTransactionsRequestFilter()

    def get_response_filter(self):
        pass


class StoreTransactionsRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(StoreTransactionsRequestFilter, self).__init__({
            'trytes':
                StringifiedTrytesArray(TransactionTrytes) | f.Required,
        })
