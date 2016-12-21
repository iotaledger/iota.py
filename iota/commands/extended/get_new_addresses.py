# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota.commands import FilterCommand, RequestFilter
from iota.filters import Trytes

__all__ = [
  'GetNewAddressesCommand',
]


class GetNewAddressesCommand(FilterCommand):
  """
  Executes ``getNewAddresses`` extended API command.

  See :py:meth:`iota.api.Iota.get_new_addresses` for more info.
  """
  command = 'getNewAddresses'

  def get_request_filter(self):
    return GetNewAddressesRequestFilter()

  def get_response_filter(self):
    pass

  def _send_request(self, request):
    pass


class GetNewAddressesRequestFilter(RequestFilter):
  def __init__(self):
    super(GetNewAddressesRequestFilter, self).__init__(
      {
        # ``count`` and ``index`` are optional.
        'count':  f.Type(int) | f.Min(1) | f.Optional(1),
        'index':  f.Type(int) | f.Min(0),

        'seed':   f.Required | Trytes,
      },

      allow_missing_keys = {
        'count',
        'index',
      },
    )
