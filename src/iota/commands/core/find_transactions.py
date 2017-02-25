# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota import Address, Tag, TransactionHash
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes

__all__ = [
  'FindTransactionsCommand',
]


class FindTransactionsCommand(FilterCommand):
  """
  Executes `findTransactions` command.

  See :py:meth:`iota.api.StrictIota.find_transactions`.
  """
  command = 'findTransactions'

  def get_request_filter(self):
    return FindTransactionsRequestFilter()

  def get_response_filter(self):
    return FindTransactionsResponseFilter()


class FindTransactionsRequestFilter(RequestFilter):
  CODE_NO_SEARCH_VALUES = 'no_search_values'

  templates = {
    CODE_NO_SEARCH_VALUES: 'No search values specified.',
  }

  def __init__(self):
    super(FindTransactionsRequestFilter, self).__init__(
      {
        'addresses': (
            f.Array
          | f.FilterRepeater(f.Required | Trytes(result_type=Address))
          | f.Optional(default=[])
        ),

        'approvees': (
            f.Array
          | f.FilterRepeater(f.Required | Trytes(result_type=TransactionHash))
          | f.Optional(default=[])
        ),

        'bundles': (
            f.Array
          | f.FilterRepeater(f.Required | Trytes(result_type=TransactionHash))
          | f.Optional(default=[])
        ),

        'tags': (
            f.Array
          | f.FilterRepeater(f.Required | Trytes(result_type=Tag))
          | f.Optional(default=[])
        ),
      },

      # Technically, all of the parameters for this command are
      #   optional, so long as at least one of them is present and not
      #   empty.
      allow_missing_keys = True,
    )

  def _apply(self, value):
    value = super(FindTransactionsRequestFilter, self)._apply(value) # type: dict

    if self._has_errors:
      return value

    # At least one search term is required.
    if not any((
        value['addresses'],
        value['approvees'],
        value['bundles'],
        value['tags'],
    )):
      return self._invalid_value(value, self.CODE_NO_SEARCH_VALUES)

    return value


class FindTransactionsResponseFilter(ResponseFilter):
  def __init__(self):
    super(FindTransactionsResponseFilter, self).__init__({
      'hashes':
          f.FilterRepeater(
              f.ByteString(encoding='ascii')
            | Trytes(result_type=TransactionHash)
          )
        | f.Optional(default=[]),
    })
