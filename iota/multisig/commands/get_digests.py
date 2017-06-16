# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota.commands import FilterCommand, RequestFilter
from iota.crypto.types import Seed
from iota.filters import Trytes
from iota.multisig.commands.get_private_keys import GetPrivateKeysCommand
from typing import Optional

__all__ = [
  'GetDigestsCommand',
]


class GetDigestsCommand(FilterCommand):
  """
  Implements `getDigests` multisig API command.

  References:
    - :py:meth:`iota.multisig.api.MultisigIota.get_digests`
  """
  command = 'getDigests'

  def get_request_filter(self):
    return GetDigestsRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    count = request['count'] # type: Optional[int]
    index = request['index'] # type: int
    seed  = request['seed'] # type: Seed

    gpk_result = GetPrivateKeysCommand(self.adapter)(
      seed  = seed,
      count = count,
      index = index,
    )

    return {
      'digests': [key.get_digest() for key in gpk_result['keys']],
    }


class GetDigestsRequestFilter(RequestFilter):
  def __init__(self):
    super(GetDigestsRequestFilter, self).__init__(
      {
        # ``count`` and ``index`` are optional.
        'count':  f.Type(int) | f.Min(1) | f.Optional(default=1),
        'index':  f.Type(int) | f.Min(0) | f.Optional(default=0),

        'seed':   f.Required | Trytes(result_type=Seed),
      },

      allow_missing_keys = {
        'count',
        'index',
      },
    )
