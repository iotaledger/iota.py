# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota.commands import FilterCommand, RequestFilter
from iota.crypto.types import Seed
from iota.filters import Trytes

__all__ = [
  'GetInputsCommand',
]


class GetInputsCommand(FilterCommand):
  """
  Executes ``getInputs`` extended API command.

  See :py:meth:`iota.api.Iota.get_inputs` for more info.
  """
  command = 'getInputs'

  def get_request_filter(self):
    return GetInputsRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class GetInputsRequestFilter(RequestFilter):
  CODE_INTERVAL_INVALID = 'interval_invalid'

  templates = {
    CODE_INTERVAL_INVALID: '``start`` must be <= ``end``',
  }

  def __init__(self):
    super(GetInputsRequestFilter, self).__init__(
      {
        # These arguments are optional.
        'end':        f.Type(int) | f.Min(0),
        'start':      f.Type(int) | f.Min(0) | f.Optional(0),
        'threshold':  f.Type(int) | f.Min(0),

        # These arguments are required.
        'seed': f.Required | Trytes(result_type=Seed),
      },

      allow_missing_keys = {
        'end',
        'start',
        'threshold',
      }
    )

  def _apply(self, value):
    # noinspection PyProtectedMember
    filtered = super(GetInputsRequestFilter, self)._apply(value)

    if self._has_errors:
      return None

    if (filtered['end'] is not None) and (filtered['start'] > filtered['end']):
      return self._invalid_value(
        value   = filtered['start'],
        reason  = self.CODE_INTERVAL_INVALID,
        sub_key = 'start',

        context = {
          'start':  filtered['start'],
          'end':    filtered['end'],
        },
      )

    return filtered
