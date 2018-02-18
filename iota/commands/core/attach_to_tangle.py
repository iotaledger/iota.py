# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import filters as flt
from iota import TransactionHash, TransactionTrytes
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes

__all__ = [
    'AttachToTangleCommand',
]


class AttachToTangleCommand(FilterCommand):
    """
    Executes ``attachToTangle`` command.

    See :py:meth:`iota.api.StrictIota.attach_to_tangle` for more info.
    """
    command = 'attachToTangle'

    def get_request_filter(self):
        return AttachToTangleRequestFilter()

    def get_response_filter(self):
        return AttachToTangleResponseFilter()


class AttachToTangleRequestFilter(RequestFilter):
    def __init__(self):
        super(AttachToTangleRequestFilter, self).__init__({
            'branchTransaction':
                flt.Required
                | Trytes(result_type=TransactionHash),
            'trunkTransaction':
                flt.Required
                | Trytes(result_type=TransactionHash),
            'trytes':
                flt.Required
                | flt.Array
                | flt.FilterRepeater(
                    flt.Required
                    | Trytes(result_type=TransactionTrytes)),
            # Loosely-validated; testnet nodes require a different value than
            # mainnet.
            'minWeightMagnitude':
                flt.Required
                | flt.Type(int)
                | flt.Min(1)
        })


class AttachToTangleResponseFilter(ResponseFilter):
    def __init__(self):
        super(AttachToTangleResponseFilter, self).__init__({
            'trytes':
                flt.FilterRepeater(
                    flt.ByteString(encoding='ascii')
                    | Trytes(result_type=TransactionTrytes))
                })
