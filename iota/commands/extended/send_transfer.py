# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import List, Optional

import filters as f
from iota import Address, Bundle, ProposedTransaction
from iota.commands import FilterCommand, RequestFilter
from iota.commands.extended.prepare_transfer import PrepareTransferCommand
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
    change_address        = request['changeAddress'] # type: Optional[Address]
    depth                 = request['depth'] # type: int
    inputs                = request['inputs'] # type: Optional[List[Address]]
    min_weight_magnitude  = request['minWeightMagnitude'] # type: int
    seed                  = request['seed'] # type: Seed
    transfers             = request['transfers'] # type: List[ProposedTransaction]

    pt_response = PrepareTransferCommand(self.adapter)(
      changeAddress   = change_address,
      inputs          = inputs,
      seed            = seed,
      transfers       = transfers,
    )

    st_response = SendTrytesCommand(self.adapter)(
      depth               = depth,
      minWeightMagnitude  = min_weight_magnitude,
      trytes              = pt_response['trytes'],
    )

    return {
      'bundle': Bundle.from_tryte_strings(st_response['trytes']),
    }


class SendTransferRequestFilter(RequestFilter):
  def __init__(self):
    super(SendTransferRequestFilter, self).__init__(
      {
        # Required parameters.
        'depth':  f.Required | f.Type(int) | f.Min(1),
        'seed':   f.Required | Trytes(result_type=Seed),

        # Loosely-validated; testnet nodes require a different value
        # than mainnet.
        'minWeightMagnitude': f.Required | f.Type(int) | f.Min(1),

        'transfers': (
            f.Required
          | f.Array
          | f.FilterRepeater(f.Required | f.Type(ProposedTransaction))
        ),

        # Optional parameters.
        'changeAddress': Trytes(result_type=Address),


        # Note that ``inputs`` is allowed to be an empty array.
        'inputs':
          f.Array | f.FilterRepeater(f.Required | Trytes(result_type=Address)),
      },

      allow_missing_keys = {
        'changeAddress',
        'inputs',
      },
    )
