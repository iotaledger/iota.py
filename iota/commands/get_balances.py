# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes
from iota.types import Address

__all__ = [
  'GetBalancesCommand',
]


class GetBalancesCommand(FilterCommand):
  """
  Executes `getBalances` command.

  See :py:method:`iota.api.IotaApi.get_balances`.
  """
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
          | f.FilterRepeater(f.Required | Trytes(result_type=Address))
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

    })
