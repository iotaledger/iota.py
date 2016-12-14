# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.commands.broadcast_transactions import BroadcastTransactionsCommand
from iota.commands.store_transactions import StoreTransactionsCommand
from iota.filters import Trytes

__all__ = [
  'BroadcastAndStoreCommand',
]


class BroadcastAndStoreCommand(FilterCommand):
  """
  Executes `broadcastAndStore` extended API command.

  See :py:method:`iota.api.IotaApi.broadcast_and_store` for more info.
  """
  command = 'broadcastAndStore'

  def get_request_filter(self):
    return BroadcastAndStoreRequestFilter()

  def get_response_filter(self):
    return BroadcastAndStoreResponseFilter()

  def send_request(self, request):
    BroadcastTransactionsCommand(self.adapter)(trytes=request['trytes'])
    return StoreTransactionsCommand(self.adapter)(trytes=request['trytes'])


class BroadcastAndStoreRequestFilter(RequestFilter):
  def __init__(self):
    super(BroadcastAndStoreRequestFilter, self).__init__({
      'trytes': f.Required | f.Array | f.FilterRepeater(f.Required | Trytes),
    })


class BroadcastAndStoreResponseFilter(ResponseFilter):
  def __init__(self):
    super(BroadcastAndStoreResponseFilter, self).__init__({
      'trytes': f.FilterRepeater(f.ByteString(encoding='ascii') | Trytes),
    })
