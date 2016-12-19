# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.commands import FilterCommand
from iota.commands.core.broadcast_transactions import \
  BroadcastTransactionsCommand
from iota.commands.core.store_transactions import StoreTransactionsCommand

__all__ = [
  'BroadcastAndStoreCommand',
]


class BroadcastAndStoreCommand(FilterCommand):
  """
  Executes `broadcastAndStore` extended API command.

  See :py:meth:`iota.api.IotaApi.broadcast_and_store` for more info.
  """
  command = 'broadcastAndStore'

  def get_request_filter(self):
    pass

  def get_response_filter(self):
    pass

  def _send_request(self, request):
    bt_command = BroadcastTransactionsCommand(
      adapter         = self.adapter,
      prepare_request = self.prepare_request,
    )
    bt_command(**request)

    # `storeTransactions` accepts the exact same request object as
    # `broadcastTransactions`, so it's safe to bypass request
    # validation here.
    return \
      StoreTransactionsCommand(self.adapter, prepare_request=False)(**request)
