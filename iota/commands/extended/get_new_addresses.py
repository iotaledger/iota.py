# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import List, Optional

import filters as f

from iota import Address, AddressChecksum
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
    count           = request['count'] # type: Optional[int]
    index           = request['index'] # type: int
    security_level  = request['securityLevel'] # type: int
    checksum        = request['checksum'] # type: Optional[bool]
    seed            = request['seed'] # type: Seed

    return {
      'addresses': 
         self._find_addresses(seed, index, count, security_level, checksum),
    }

  def _find_addresses(self, seed, index, count, security_level, checksum):
    # type: (Seed, int, Optional[int], int, Optional[bool]) -> List[Address]
    """
    Find addresses matching the command parameters.
    """
    # type: (Seed, int, Optional[bool]) -> List[Address]
    generator = AddressGenerator(seed, security_level, checksum)

    if count is None:
      # Connect to Tangle and find the first address without any
      # transactions.
      for addy in generator.create_iterator(start=index):
        # If we're generating addresses with checksums we need to check
        # for transactions on the address without the checksum
        if not checksum:
          response = FindTransactionsCommand(self.adapter)(addresses=[addy])
        else:
          response = FindTransactionsCommand(self.adapter)(
            addresses=[addy][:-AddressChecksum.LEN]
        )


        if not response.get('hashes'):
          return [addy]

    return generator.get_addresses(start=index, count=count)


class GetNewAddressesRequestFilter(RequestFilter):
  MAX_SECURITY_LEVEL = 3
  """
  Max allowed value for ``securityLevel``.

  Note that :py:class:`AddressGenerator` does not enforce a limit, just
  in case you are sure that you REALLY know what you are doing.
  """

  def __init__(self):
    super(GetNewAddressesRequestFilter, self).__init__(
      {
        # Everything except ``seed`` is optional.
        'count':  f.Type(int) | f.Min(1),
        'index':  f.Type(int) | f.Min(0) | f.Optional(default=0),

        'securityLevel':
              f.Type(int)
            | f.Min(1)
            | f.Max(self.MAX_SECURITY_LEVEL)
            | f.Optional(default=AddressGenerator.DEFAULT_SECURITY_LEVEL),

        'checksum':  f.Type(bool) | f.Optional(default=False),

        'seed': f.Required | Trytes(result_type=Seed),
      },

      allow_missing_keys = {
        'count',
        'index',
        'securityLevel',
        'checksum',
      },
    )
