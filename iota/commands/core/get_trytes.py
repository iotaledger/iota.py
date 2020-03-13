import filters as f

from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import StringifiedTrytesArray, Trytes

__all__ = [
    'GetTrytesCommand',
]


class GetTrytesCommand(FilterCommand):
    """
    Executes ``getTrytes`` command.

    See :py:meth:`iota.api.StrictIota.get_trytes`.
    """
    command = 'getTrytes'

    def get_request_filter(self):
        return GetTrytesRequestFilter()

    def get_response_filter(self):
        return GetTrytesResponseFilter()


class GetTrytesRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(GetTrytesRequestFilter, self).__init__({
            'hashes':
                StringifiedTrytesArray(TransactionHash) | f.Required,
        })


class GetTrytesResponseFilter(ResponseFilter):
    def __init__(self) -> None:
        super(GetTrytesResponseFilter, self).__init__({
            'trytes':
                f.Array | f.FilterRepeater(
                    f.ByteString(encoding='ascii') |
                    Trytes
                ),
        })
