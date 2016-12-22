# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota import Address, Transaction, TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.crypto.types import Seed
from iota.filters import Trytes

__all__ = [
  'PrepareTransfersCommand',
]


class PrepareTransfersCommand(FilterCommand):
  """
  Executes ``prepareTransfers`` extended API command.

  See :py:meth:`iota.api.Iota.prepare_transfers` for more info.
  """
  command = 'prepareTransfers'

  def get_request_filter(self):
    return PrepareTransfersRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class PrepareTransfersRequestFilter(RequestFilter):
  def __init__(self):
    super(PrepareTransfersRequestFilter, self).__init__(
      {
        # Required parameters.
        'seed': f.Required | Trytes(result_type=Seed),

        'transfers':
          f.Required | f.Array | f.FilterRepeater(f.Type(Transaction)),

        # Optional parameters.
        'change_address': Trytes(result_type=Address),

        'inputs':
          f.Array | f.FilterRepeater(Trytes(result_type=TransactionHash)),
      },

      allow_missing_keys = {
        'change_address',
        'inputs',
      },
    )
