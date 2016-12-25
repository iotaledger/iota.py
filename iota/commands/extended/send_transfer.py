# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import List, Optional

import filters as f
from iota import Address, Bundle, ProposedTransaction
from iota.commands import DEFAULT_MIN_WEIGHT_MAGNITUDE, FilterCommand, \
  RequestFilter
from iota.commands.extended.prepare_transfers import PrepareTransfersCommand
from iota.commands.extended.send_trytes import SendTrytesCommand
from iota.crypto.types import Seed
from iota.filters import Trytes

__all__ = [
  'SendTransferCommand',
]


class SendTransferCommand(FilterCommand):
  """
  Executes ``sendTransfer`` extended API command.

  See :py:meth:`iota.api.Iota.send_transfer` for more info.
  """
  command = 'sendTransfer'

  def get_request_filter(self):
    return SendTransferRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    change_address        = request['change_address'] # type: Optional[Address]
    depth                 = request['depth'] # type: int
    inputs                = request['inputs'] or [] # type: List[Address]
    min_weight_magnitude  = request['min_weight_magnitude'] # type: int
    seed                  = request['seed'] # type: Seed
    transfers             = request['transfers'] # type: List[ProposedTransaction]

    prepared_trytes = PrepareTransfersCommand(self.adapter)(
      change_address  = change_address,
      inputs          = inputs,
      seed            = seed,
      transfers       = transfers,
    )

    sent_trytes = SendTrytesCommand(self.adapter)(
      depth                 = depth,
      min_weight_magnitude  = min_weight_magnitude,
      trytes                = prepared_trytes,
    )

    return Bundle.from_tryte_strings(sent_trytes)


class SendTransferRequestFilter(RequestFilter):
  def __init__(self):
    super(SendTransferRequestFilter, self).__init__(
      {
        # Required parameters.
        'seed': f.Required | Trytes(result_type=Seed),

        'transfers':
          f.Required | f.Array | f.FilterRepeater(f.Type(ProposedTransaction)),

        # Optional parameters.
        'change_address': Trytes(result_type=Address),
        'depth': f.Type(int) | f.Min(1),

        'min_weight_magnitude': (
            f.Type(int)
          | f.Min(18)
          | f.Optional(DEFAULT_MIN_WEIGHT_MAGNITUDE)
        ),

        'inputs':
          f.Array | f.FilterRepeater(Trytes(result_type=Address)),

      },

      allow_missing_keys = {
        'change_address',
        'depth',
        'inputs',
        'min_weight_magnitude',
      },
    )
