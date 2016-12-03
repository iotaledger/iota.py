# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota.commands import FilterCommand
from iota.filters import Trytes


class BroadcastTransactionsCommand(FilterCommand):
  """
  Executes `broadcastTransactions` command.

  :see: iota.IotaApi.broadcast_transactions
  """
  command = 'broadcastTransactions'

  def get_request_filter(self):
    return f.FilterMapper(
      {
        'trytes': f.Required | f.Array | f.FilterRepeater(f.Required | Trytes),
      },

      allow_extra_keys    = False,
      allow_missing_keys  = False,
    )

  def get_response_filter(self):
    pass
