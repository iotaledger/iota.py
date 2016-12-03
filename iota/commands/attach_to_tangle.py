# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota.commands import FilterCommand
from iota.filters import Trytes
from iota.types import TransactionId

__all__ = [
  'AttachToTangleCommand',
]


class AttachToTangleCommand(FilterCommand):
  """
  Executes `attachToTangle` command.

  :see: iota.IotaApi.attach_to_tangle
  """
  command = 'attachToTangle'

  def get_request_filter(self):
    return f.FilterMapper(
      {
        'trunk_transaction':  f.Required | Trytes(result_type=TransactionId),
        'branch_transaction': f.Required | Trytes(result_type=TransactionId),

        'min_weight_magnitude': f.Type(int) | f.Min(18) | f.Optional(18),

        'trytes': f.Required | f.Array | f.FilterRepeater(f.Required | Trytes),
      },

      allow_extra_keys = False,

      allow_missing_keys = {
        'min_weight_magnitude',
      },
    )

  def get_response_filter(self):
    return f.FilterMapper(
      {
        'trytes': f.FilterRepeater(f.ByteString(encoding='ascii') | Trytes),
      },

      allow_extra_keys    = True,
      allow_missing_keys  = True,
    )
