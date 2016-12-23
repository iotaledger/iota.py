# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota import Address, ProposedTransaction
from iota.commands import FilterCommand, RequestFilter
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
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class SendTransferRequestFilter(RequestFilter):
  def __init__(self):
    super(SendTransferRequestFilter, self).__init__(
      {
        # Required parameters.
        'seed': f.Required | Trytes(result_type=Seed),

        'transfers':
          f.Required | f.Array | f.FilterRepeater(f.Type(ProposedTransaction)),

        # Optional parameters.
        'change_address': Trytes(result_type=Address),
        'depth': f.Type(int) | f.Min(1),
        'min_weight_magnitude': f.Type(int) | f.Min(18) | f.Optional(18),

        'inputs':
          f.Array | f.FilterRepeater(Trytes(result_type=Address)),

      },

      allow_missing_keys = {
        'change_address',
        'depth',
        'inputs',
        'min_weight_magnitude',
      },
    )
