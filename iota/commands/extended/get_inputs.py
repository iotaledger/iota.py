# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import List, Optional

import filters as f
from iota import Address, BadApiResponse
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.find_transactions import FindTransactionsCommand
from iota.commands.core.get_balances import GetBalancesCommand
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
    end       = request['end'] # type: Optional[int]
    seed      = request['seed'] # type: Seed
    start     = request['start'] # type: int
    threshold = request['threshold'] # type: Optional[int]

    generator = AddressGenerator(seed)

    # Determine the addresses we will be scanning.
    if end is None:
      # This is similar to the ``getNewAddresses`` command, except it
      # is interested in all the addresses that `getNewAddresses`
      # skips.
      addresses = [] # type: List[Address]
      for addy in generator.create_generator(start):
        ft_response = FindTransactionsCommand(self.adapter)(addresses=[addy])

        if ft_response.get('hashes'):
          addresses.append(addy)
        else:
          break
    else:
      addresses = generator.get_addresses(start, end - start)

    # Load balances for the addresses that we generated.
    gb_response = GetBalancesCommand(self.adapter)(addresses=addresses)

    result = {
      'inputs': [],
      'totalBalance': 0,
    }

    threshold_met = threshold is None

    for i, balance in enumerate(gb_response['balances']):
      addresses[i].balance = balance

      if balance:
        result['inputs'].append({
          'address':  addresses[i],
          'balance':  balance,
          'keyIndex': addresses[i].key_index,
        })

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
    CODE_INTERVAL_INVALID: '``start`` must be <= ``end``',
    CODE_INTERVAL_TOO_BIG: '``end`` - ``start`` must be <= {max_interval}',
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
