# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Optional

import filters as f

from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.find_transactions import FindTransactionsCommand
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed
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

  def _execute(self, request):
    count = request['count'] # type: Optional[int]
    index = request['index'] # type: int
    seed  = request['seed'] # type: Seed

    return {
      'addresses': self._find_addresses(seed, index, count),
    }

  def _find_addresses(self, seed, index, count):
    """
    Find addresses matching the command parameters.
    """
    # type: (Seed, int, Optional[int]) -> List[Address]
    generator = AddressGenerator(seed)

    if count is None:
      # Connect to Tangle and find the first address without any
      # transactions.
      for addy in generator.create_iterator(start=index):
        response = FindTransactionsCommand(self.adapter)(addresses=[addy])

        if not response.get('hashes'):
          return [addy]

    return generator.get_addresses(start=index, count=count)


class GetNewAddressesRequestFilter(RequestFilter):
  def __init__(self):
    super(GetNewAddressesRequestFilter, self).__init__(
      {
        # ``count`` and ``index`` are optional.
        'count':  f.Type(int) | f.Min(1),
        'index':  f.Type(int) | f.Min(0) | f.Optional(default=0),

        'seed':   f.Required | Trytes(result_type=Seed),
      },

      allow_missing_keys = {
        'count',
        'index',
      },
    )
