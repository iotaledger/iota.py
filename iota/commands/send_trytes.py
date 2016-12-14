# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota.commands import FilterCommand, RequestFilter
from iota.filters import Trytes

__all__ = [
  'SendTrytesCommand',
]


class SendTrytesCommand(FilterCommand):
  """
  Executes `sendTrytes` extended API command.

  See :py:method:`iota.api.IotaApi.send_trytes` for more info.
  """
  command = 'sendTrytes'

  def get_request_filter(self):
    return SendTrytesRequestFilter()

  def get_response_filter(self):
    pass


class SendTrytesRequestFilter(RequestFilter):
  def __init__(self):
    super(SendTrytesRequestFilter, self).__init__(
      {
        'depth': f.Type(int) | f.Min(1),

        'min_weight_magnitude': f.Type(int) | f.Min(18) | f.Optional(18),

        'trytes': f.Required | f.Array | f.FilterRepeater(f.Required | Trytes),
      },

      allow_missing_keys = {
        'min_weight_magnitude',
      },
    )
