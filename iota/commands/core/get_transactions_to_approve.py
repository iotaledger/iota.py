import filters as f

from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes

__all__ = [
    'GetTransactionsToApproveCommand',
]


class GetTransactionsToApproveCommand(FilterCommand):
    """
    Executes ``getTransactionsToApprove`` command.

    See :py:meth:`iota.api.StrictIota.get_transactions_to_approve`.
    """
    command = 'getTransactionsToApprove'

    def get_request_filter(self):
        return GetTransactionsToApproveRequestFilter()

    def get_response_filter(self):
        return GetTransactionsToApproveResponseFilter()


class GetTransactionsToApproveRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(GetTransactionsToApproveRequestFilter, self).__init__(
            {
                'depth': f.Required | f.Type(int) | f.Min(1),

                'reference': Trytes(result_type=TransactionHash),
            },

            allow_missing_keys={
                'reference',
            })

    def _apply(self, value):
        value: dict = super(GetTransactionsToApproveRequestFilter, self)._apply(
            value,
        )

        if self._has_errors:
            return value

        # Remove reference if null.
        if value['reference'] is None:
            del value['reference']

        return value


class GetTransactionsToApproveResponseFilter(ResponseFilter):
    def __init__(self) -> None:
        super(GetTransactionsToApproveResponseFilter, self).__init__({
            'branchTransaction':
                f.ByteString(encoding='ascii') | Trytes(TransactionHash),

            'trunkTransaction':
                f.ByteString(encoding='ascii') | Trytes(TransactionHash),
        })
