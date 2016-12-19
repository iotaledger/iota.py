# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.attach_to_tangle import AttachToTangleCommand
from iota.commands.core.get_transactions_to_approve import \
  GetTransactionsToApproveCommand
from iota.commands.extended.broadcast_and_store import BroadcastAndStoreCommand
from iota.filters import Trytes

__all__ = [
  'SendTrytesCommand',
]


class SendTrytesCommand(FilterCommand):
  """
  Executes `sendTrytes` extended API command.

  See :py:meth:`iota.api.IotaApi.send_trytes` for more info.
  """
  command = 'sendTrytes'

  def get_request_filter(self):
    return SendTrytesRequestFilter()

  def get_response_filter(self):
    pass

  def _send_request(self, request):
    # Call ``getTransactionsToApprove`` to locate trunk and branch
    # transactions so that we can attach the bundle to the Tangle.
    gta_command = GetTransactionsToApproveCommand(
      adapter         = self.adapter,
      prepare_request = self.prepare_request,
    )
    gta_response = gta_command(depth=request['depth'])

    AttachToTangleCommand(self.adapter, prepare_request=self.prepare_request)(
      branch_transaction  = gta_response.get('branchTransaction'),
      trunk_transaction   = gta_response.get('trunkTransaction'),

      min_weight_magnitude  = request['min_weight_magnitude'],
      trytes                = request['trytes'],
    )

    # By this point, ``request['trytes']`` has already been validated,
    # so we can bypass validation for `broadcastAndStore`.
    return BroadcastAndStoreCommand(self.adapter, prepare_request=False)(
      trytes = request['trytes'],
    )


class SendTrytesRequestFilter(RequestFilter):
  def __init__(self):
    super(SendTrytesRequestFilter, self).__init__(
      {
        'depth': f.Type(int) | f.Min(1),

        'min_weight_magnitude': f.Type(int) | f.Min(18) | f.Optional(18),

        'trytes': f.Required | f.Array | f.FilterRepeater(f.Required | Trytes),
      },

      allow_missing_keys = {
        'min_weight_magnitude',
      },
    )
