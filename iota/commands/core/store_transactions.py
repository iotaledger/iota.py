# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota import TransactionTrytes
from iota.commands import FilterCommand, RequestFilter
from iota.filters import Trytes

__all__ = [
  'StoreTransactionsCommand',
]


class StoreTransactionsCommand(FilterCommand):
  """
  Executes ``storeTransactions`` command.

  See :py:meth:`iota.api.StrictIota.store_transactions`.
  """
  command = 'storeTransactions'

  def get_request_filter(self):
    return StoreTransactionsRequestFilter()

  def get_response_filter(self):
    pass


class StoreTransactionsRequestFilter(RequestFilter):
  def __init__(self):
    super(StoreTransactionsRequestFilter, self).__init__({
      'trytes':
          f.Required
        | f.Array
        | f.FilterRepeater(
              f.Required
            | Trytes(result_type=TransactionTrytes)
            | f.Unicode(encoding='ascii', normalize=False)
          ),
    })
