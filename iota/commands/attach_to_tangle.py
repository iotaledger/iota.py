# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes
from iota.types import TransactionId

__all__ = [
  'AttachToTangleCommand',
]


class AttachToTangleCommand(FilterCommand):
  """
  Executes `attachToTangle` command.

  See :py:method:`iota.api.StrictIota.attach_to_tangle`.
  """
  command = 'attachToTangle'

  def get_request_filter(self):
    return AttachToTangleRequestFilter()

  def get_response_filter(self):
    return AttachToTangleResponseFilter()


class AttachToTangleRequestFilter(RequestFilter):
  def __init__(self):
    super(AttachToTangleRequestFilter, self).__init__(
      {
        'trunk_transaction':  f.Required | Trytes(result_type=TransactionId),
        'branch_transaction': f.Required | Trytes(result_type=TransactionId),

        'min_weight_magnitude': f.Type(int) | f.Min(18) | f.Optional(18),

        'trytes': f.Required | f.Array | f.FilterRepeater(f.Required | Trytes),
      },

      allow_missing_keys = {
        'min_weight_magnitude',
      },
    )


class AttachToTangleResponseFilter(ResponseFilter):
  def __init__(self):
    super(AttachToTangleResponseFilter, self).__init__({
      'trytes': f.FilterRepeater(f.ByteString(encoding='ascii') | Trytes),
    })
