import filters as f

from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.filters import Trytes

__all__ = [
    'CheckConsistencyCommand',
]


class CheckConsistencyCommand(FilterCommand):
    """
    Executes ``checkConsistency`` extended API command.

    See :py:meth:`iota.api.Iota.check_consistency` for more info.
    """
    command = 'checkConsistency'

    def get_request_filter(self):
        return CheckConsistencyRequestFilter()

    def get_response_filter(self):
        pass


class CheckConsistencyRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(CheckConsistencyRequestFilter, self).__init__({
            'tails':
                f.Required |
                f.Array |
                f.FilterRepeater(f.Required | Trytes(TransactionHash)),
        })
