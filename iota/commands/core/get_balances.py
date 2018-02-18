# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import filters as flt

from iota import Address
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import AddressNoChecksum, Trytes

__all__ = [
    'GetBalancesCommand',
]


class GetBalancesCommand(FilterCommand):
    """
    Executes `getBalances` command.

    See :py:meth:`iota.api.StrictIota.get_balances`.
    """
    command = 'getBalances'

    def get_request_filter(self):
        return GetBalancesRequestFilter()

    def get_response_filter(self):
        return GetBalancesResponseFilter()


class GetBalancesRequestFilter(RequestFilter):
    def __init__(self):
        super(GetBalancesRequestFilter, self).__init__(
            {
                'addresses': (
                    flt.Required
                    | flt.Array
                    | flt.FilterRepeater(
                        flt.Required
                        | AddressNoChecksum()
                        | flt.Unicode(encoding='ascii', normalize=False))
                ),
                'threshold': (
                    flt.Type(int)
                    | flt.Min(0)
                    | flt.Max(100)
                    | flt.Optional(default=100))
            },
            allow_missing_keys={
                'threshold',
            },
        )


class GetBalancesResponseFilter(ResponseFilter):
    def __init__(self):
        super(GetBalancesResponseFilter, self).__init__({
            'balances': flt.Array | flt.FilterRepeater(flt.Int),

            'milestone':
                flt.ByteString(encoding='ascii') | Trytes(result_type=Address),
        })
