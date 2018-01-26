# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import filters as flt

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
    def __init__(self):
        super(GetTransactionsToApproveRequestFilter, self).__init__({
            'depth':
                flt.Required
                | flt.Type(int)
                | flt.Min(1),
            'reference':
                Trytes(result_type=TransactionHash)
            },
            allow_missing_keys={
                'reference',
            })

    def _apply(self, value):
        value = super(GetTransactionsToApproveRequestFilter, self)\
            ._apply(value)  # type: dict

        if self._has_errors:
            return value

        # Remove reference if null.
        if value['reference'] is None:
            del value['reference']

        return value


class GetTransactionsToApproveResponseFilter(ResponseFilter):
    def __init__(self):
        super(GetTransactionsToApproveResponseFilter, self).__init__({
            'branchTransaction': (
                flt.ByteString(encoding='ascii')
                | Trytes(result_type=TransactionHash)),
            'trunkTransaction': (
                flt.ByteString(encoding='ascii')
                | Trytes(result_type=TransactionHash))
            })
