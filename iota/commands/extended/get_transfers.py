# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota.commands import FilterCommand, RequestFilter
from iota.crypto.types import Seed
from iota.filters import Trytes

__all__ = [
  'GetTransfersCommand',
]


class GetTransfersCommand(FilterCommand):
  """
  Executes ``getTransfers`` extended API command.

  See :py:meth:`iota.api.Iota.get_transfers` for more info.
  """
  command = 'getTransfers'

  def get_request_filter(self):
    return GetTransfersRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class GetTransfersRequestFilter(RequestFilter):
  MAX_INTERVAL = 500

  CODE_INTERVAL_INVALID = 'interval_invalid'
  CODE_INTERVAL_TOO_BIG = 'interval_too_big'

  templates = {
    CODE_INTERVAL_INVALID: '``start`` must be <= ``end``',
    CODE_INTERVAL_TOO_BIG: '``end`` - ``start`` must be <= {max_interval}',
  }

  def __init__(self):
    super(GetTransfersRequestFilter, self).__init__(
      {
        # These arguments are optional.
        'end':    f.Type(int) | f.Min(0),
        'start':  f.Type(int) | f.Min(0) | f.Optional(0),

        'inclusion_states': f.Type(bool) | f.Optional(False),

        # These arguments are required.
        'seed': f.Required | Trytes(result_type=Seed),
      },

      allow_missing_keys = {
        'end',
        'inclusion_states',
        'start',
      },
    )

  def _apply(self, value):
    # noinspection PyProtectedMember
    filtered = super(GetTransfersRequestFilter, self)._apply(value)

    if self._has_errors:
      return filtered

    if filtered['end'] is not None:
      if filtered['start'] > filtered['end']:
        filtered['start'] = self._invalid_value(
          value   = filtered['start'],
          reason  = self.CODE_INTERVAL_INVALID,
          sub_key = 'start',

          context = {
            'start':  filtered['start'],
            'end':    filtered['end'],
          },
        )
      elif (filtered['end'] - filtered['start']) > self.MAX_INTERVAL:
        filtered['end'] = self._invalid_value(
          value   = filtered['end'],
          reason  = self.CODE_INTERVAL_TOO_BIG,
          sub_key = 'end',

          context = {
            'start':  filtered['start'],
            'end':    filtered['end'],
          },

          template_vars = {
            'max_interval': self.MAX_INTERVAL,
          },
        )

    return filtered
