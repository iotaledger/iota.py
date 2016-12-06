# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes
from iota.types import Address, Tag, TransactionId

__all__ = [
  'FindTransactionsCommand',
]


class FindTransactionsCommand(FilterCommand):
  """
  Executes `findTransactions` command.

  :see: iota.IotaApi.find_transactions
  """
  def get_request_filter(self):
    return FindTransactionsRequestFilter()

  def get_response_filter(self):
    return FindTransactionsResponseFilter()


class FindTransactionsRequestFilter(RequestFilter):
  def __init__(self):
    super(FindTransactionsRequestFilter, self).__init__(
      {
        'addresses': (
            f.Array
          | f.FilterRepeater(f.Required | Trytes(result_type=Address))
        ),

        'approvees': (
            f.Array
          | f.FilterRepeater(f.Required | Trytes(result_type=TransactionId))
        ),

        'bundles': (
            f.Array
          | f.FilterRepeater(f.Required | Trytes(result_type=TransactionId))
        ),

        'tags': (
            f.Array
          | f.FilterRepeater(f.Required | Trytes(result_type=Tag))
        ),
      },

      # Technically, all of the parameters for this command are
      #   optional, so long as at least one of them is present and not
      #   empty.
      allow_missing_keys = True,
    )


class FindTransactionsResponseFilter(ResponseFilter):
  def __init__(self):
    super(FindTransactionsResponseFilter, self).__init__({})
