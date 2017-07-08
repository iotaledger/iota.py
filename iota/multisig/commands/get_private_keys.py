# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Optional

import filters as f

from iota.commands import FilterCommand, RequestFilter
from iota.crypto.addresses import AddressGenerator
from iota.crypto.signing import KeyGenerator
from iota.crypto.types import Seed
from iota.filters import Trytes

__all__ = [
  'GetPrivateKeysCommand',
]


class GetPrivateKeysCommand(FilterCommand):
  """
  Implements `get_private_keys` multisig API command.

  References:
    - :py:meth:`iota.multisig.MultisigIota.get_private_key`
    - https://github.com/iotaledger/wiki/blob/master/multisigs.md
  """
  command = 'getPrivateKeys'

  def get_request_filter(self):
    return GetPrivateKeysRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    count           = request['count'] # type: Optional[int]
    index           = request['index'] # type: int
    seed            = request['seed'] # type: Seed
    security_level  = request['securityLevel'] # type: int

    generator = KeyGenerator(seed)

    return {
      'keys':
        generator.get_keys(start=index, count=count, iterations=security_level),
    }


class GetPrivateKeysRequestFilter(RequestFilter):
  def __init__(self):
    super(GetPrivateKeysRequestFilter, self).__init__(
      {
        # Optional Parameters
        'count':
          f.Type(int) | f.Min(1) | f.Optional(default=1),

        'index':
          f.Type(int) | f.Min(0) | f.Optional(default=0),

        'securityLevel':
            f.Type(int)
          | f.Min(1)
          | f.Optional(default=AddressGenerator.DEFAULT_SECURITY_LEVEL),

        # Required Parameters
        'seed':
          f.Required | Trytes(result_type=Seed),
      },

      allow_missing_keys = {
        'count',
        'index',
        'securityLevel',
      },
    )
