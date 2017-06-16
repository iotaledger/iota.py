# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Optional

import filters as f
from iota import BadApiResponse
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.get_balances import GetBalancesCommand
from iota.commands.extended.utils import iter_used_addresses
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed
from iota.exceptions import with_context
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
    stop      = request['stop'] # type: Optional[int]
    seed      = request['seed'] # type: Seed
    start     = request['start'] # type: int
    threshold = request['threshold'] # type: Optional[int]

    # Determine the addresses we will be scanning.
    if stop is None:
      addresses =\
        [addy for addy, _ in iter_used_addresses(self.adapter, seed, start)]
    else:
      addresses = AddressGenerator(seed).get_addresses(start, stop)

    if addresses:
      # Load balances for the addresses that we generated.
      gb_response = GetBalancesCommand(self.adapter)(addresses=addresses)
    else:
      gb_response = {'balances': []}

    result = {
      'inputs': [],
      'totalBalance': 0,
    }

    threshold_met = threshold is None

    for i, balance in enumerate(gb_response['balances']):
      addresses[i].balance = balance

      if balance:
        result['inputs'].append(addresses[i])
        result['totalBalance'] += balance

        if (threshold is not None) and (result['totalBalance'] >= threshold):
          threshold_met = True
          break

    if threshold_met:
      return result
    else:
      # This is an exception case, but note that we attach the result
      # to the exception context so that it can be used for
      # troubleshooting.
      raise with_context(
        exc = BadApiResponse(
          'Accumulated balance {balance} is less than threshold {threshold} '
          '(``exc.context`` contains more information).'.format(
            threshold = threshold,
            balance   = result['totalBalance'],
          ),
        ),

        context = {
          'inputs':         result['inputs'],
          'request':        request,
          'total_balance':  result['totalBalance'],
        },
      )


class GetInputsRequestFilter(RequestFilter):
  MAX_INTERVAL = 500

  CODE_INTERVAL_INVALID = 'interval_invalid'
  CODE_INTERVAL_TOO_BIG = 'interval_too_big'

  templates = {
    CODE_INTERVAL_INVALID: '``start`` must be <= ``stop``',
    CODE_INTERVAL_TOO_BIG: '``stop`` - ``start`` must be <= {max_interval}',
  }

  def __init__(self):
    super(GetInputsRequestFilter, self).__init__(
      {
        # These arguments are optional.
        'stop':       f.Type(int) | f.Min(0),
        'start':      f.Type(int) | f.Min(0) | f.Optional(0),
        'threshold':  f.Type(int) | f.Min(0),

        # These arguments are required.
        'seed': f.Required | Trytes(result_type=Seed),
      },

      allow_missing_keys = {
        'stop',
        'start',
        'threshold',
      }
    )

  def _apply(self, value):
    # noinspection PyProtectedMember
    filtered = super(GetInputsRequestFilter, self)._apply(value)

    if self._has_errors:
      return filtered

    if filtered['stop'] is not None:
      if filtered['start'] > filtered['stop']:
        filtered['start'] = self._invalid_value(
          value   = filtered['start'],
          reason  = self.CODE_INTERVAL_INVALID,
          sub_key = 'start',

          context = {
            'start':  filtered['start'],
            'stop':   filtered['stop'],
          },
        )
      elif (filtered['stop'] - filtered['start']) > self.MAX_INTERVAL:
        filtered['stop'] = self._invalid_value(
          value   = filtered['stop'],
          reason  = self.CODE_INTERVAL_TOO_BIG,
          sub_key = 'stop',

          context = {
            'start':  filtered['start'],
            'stop':    filtered['stop'],
          },

          template_vars = {
            'max_interval': self.MAX_INTERVAL,
          },
        )

    return filtered
