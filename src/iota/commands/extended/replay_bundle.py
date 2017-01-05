# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import List

import filters as f
from iota import Bundle
from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.commands.extended.get_bundles import GetBundlesCommand
from iota.commands.extended.send_trytes import SendTrytesCommand
from iota.filters import Trytes

__all__ = [
  'ReplayBundleCommand',
]


class ReplayBundleCommand(FilterCommand):
  """
  Executes ``replayBundle`` extended API command.

  See :py:meth:`iota.api.Iota.replay_bundle` for more information.
  """
  command = 'replayBundle'

  def get_request_filter(self):
    return ReplayBundleRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    depth                 = request['depth'] # type: int
    min_weight_magnitude  = request['min_weight_magnitude'] # type: int
    transaction           = request['transaction'] # type: TransactionHash

    bundles = GetBundlesCommand(self.adapter)(transaction=transaction) # type: List[Bundle]

    return SendTrytesCommand(self.adapter)(
      depth                 = depth,
      min_weight_magnitude  = min_weight_magnitude,

      trytes = list(reversed(b.as_tryte_string() for b in bundles)),
    )



class ReplayBundleRequestFilter(RequestFilter):
  def __init__(self):
    super(ReplayBundleRequestFilter, self).__init__({
      'depth':        f.Required | f.Type(int) | f.Min(1),
      'transaction':  f.Required | Trytes(result_type=TransactionHash),

      # Loosely-validated; testnet nodes require a different value than
      # mainnet.
      'min_weight_magnitude': f.Required | f.Type(int) | f.Min(1),
    })
