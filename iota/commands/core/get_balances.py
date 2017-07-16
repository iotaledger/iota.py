# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota import Address
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes

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
            f.Required
          | f.Array
          | f.FilterRepeater(
                f.Required
              | Trytes(result_type=Address)
              | f.Unicode(encoding='ascii', normalize=False)
            )
        ),

        'threshold': (
            f.Type(int)
          | f.Min(0)
          | f.Max(100)
          | f.Optional(default=100)
        ),
      },

      allow_missing_keys = {
        'threshold',
      },
    )


class GetBalancesResponseFilter(ResponseFilter):
  def __init__(self):
    super(GetBalancesResponseFilter, self).__init__({
      'balances': f.Array | f.FilterRepeater(f.Int),

      'milestone':
        f.ByteString(encoding='ascii') | Trytes(result_type=Address),
    })
