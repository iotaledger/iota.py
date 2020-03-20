import filters as f

from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes
from iota.transaction.types import TransactionHash

__all__ = [
    'GetTipsCommand',
]


class GetTipsCommand(FilterCommand):
    """
    Executes ``getTips`` command.

    See :py:meth:`iota.api.StrictIota.get_tips`.
    """
    command = 'getTips'

    def get_request_filter(self):
        return GetTipsRequestFilter()

    def get_response_filter(self):
        return GetTipsResponseFilter()


class GetTipsRequestFilter(RequestFilter):
    def __init__(self) -> None:
        # ``getTips`` doesn't accept any parameters.
        # Using a filter here just to enforce that the request is empty.
        super(GetTipsRequestFilter, self).__init__({})


class GetTipsResponseFilter(ResponseFilter):
    def __init__(self) -> None:
        super(GetTipsResponseFilter, self).__init__({
            'hashes':
                f.Array | f.FilterRepeater(
                    f.ByteString(encoding='ascii') | Trytes(TransactionHash),
                ),
        })
