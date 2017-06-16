# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota import TransactionTrytes
from iota.commands import FilterCommand, RequestFilter
from iota.filters import Trytes

__all__ = [
  'BroadcastTransactionsCommand',
]


class BroadcastTransactionsCommand(FilterCommand):
  """
  Executes `broadcastTransactions` command.

  See :py:meth:`iota.api.StrictIota.broadcast_transactions`.
  """
  command = 'broadcastTransactions'

  def get_request_filter(self):
    return BroadcastTransactionsRequestFilter()

  def get_response_filter(self):
    pass


class BroadcastTransactionsRequestFilter(RequestFilter):
  def __init__(self):
    super(BroadcastTransactionsRequestFilter, self).__init__({
      'trytes':
          f.Required
        | f.Array
        | f.FilterRepeater(
              f.Required
            | Trytes(result_type=TransactionTrytes)
            | f.Unicode(encoding='ascii', normalize=False)
          ),
    })
