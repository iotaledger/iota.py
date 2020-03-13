import filters as f

from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes

__all__ = [
    'GetMissingTransactionsCommand',
]


class GetMissingTransactionsCommand(FilterCommand):
    """
    Executes `getMissingTransactions` command.

    See :py:meth:`iota.api.StrictIota.get_missing_transactions`.
    """
    command = 'getMissingTransactions'

    def get_request_filter(self):
        return GetMissingTransactionsRequestFilter()

    def get_response_filter(self):
        return GetMissingTransactionsResponseFilter()


class GetMissingTransactionsRequestFilter(RequestFilter):
    def __init__(self) -> None:
        # ``getMissingTransactions`` does not accept any parameters.
        # Using a filter here just to enforce that the request is empty.
        super(GetMissingTransactionsRequestFilter, self).__init__({})


class GetMissingTransactionsResponseFilter(ResponseFilter):
    def __init__(self) -> None:
        super(GetMissingTransactionsResponseFilter, self).__init__({
            'hashes':
                f.FilterRepeater(
                    f.ByteString(encoding='ascii') |
                    Trytes(TransactionHash)
                ) |
                f.Optional(default=[]),
        })
