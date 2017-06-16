# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from operator import attrgetter
from typing import List, Optional

import filters as f
from iota import Address, TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.find_transactions import FindTransactionsCommand
from iota.commands.core.get_balances import GetBalancesCommand
from iota.commands.extended.utils import get_bundles_from_transaction_hashes, \
  iter_used_addresses
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed
from iota.filters import Trytes

__all__ = [
  'GetAccountDataCommand',
]


class GetAccountDataCommand(FilterCommand):
  """
  Executes ``getAccountData`` extended API command.

  See :py:meth:`iota.api.Iota.get_account_data` for more info.
  """
  command = 'getAccountData'

  def get_request_filter(self):
    return GetAccountDataRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    inclusion_states  = request['inclusionStates'] # type: bool
    seed              = request['seed'] # type: Seed
    start             = request['start'] # type: int
    stop              = request['stop'] # type: Optional[int]

    if stop is None:
      my_addresses  = [] # type: List[Address]
      my_hashes     = [] # type: List[TransactionHash]

      for addy, hashes in iter_used_addresses(self.adapter, seed, start):
        my_addresses.append(addy)
        my_hashes.extend(hashes)
    else:
      ft_command = FindTransactionsCommand(self.adapter)

      my_addresses  = AddressGenerator(seed).get_addresses(start, stop - start)
      my_hashes     = ft_command(addresses=my_addresses).get('hashes') or []

    account_balance = 0
    if my_hashes:
      # Load balances for the addresses that we generated.
      gb_response = GetBalancesCommand(self.adapter)(addresses=my_addresses)

      for i, balance in enumerate(gb_response['balances']):
        my_addresses[i].balance = balance
        account_balance += balance

    return {
      'addresses':  list(sorted(my_addresses, key=attrgetter('key_index'))),
      'balance':    account_balance,

      'bundles':
        get_bundles_from_transaction_hashes(
          adapter             = self.adapter,
          transaction_hashes  = my_hashes,
          inclusion_states    = inclusion_states,
        ),
    }


class GetAccountDataRequestFilter(RequestFilter):
  MAX_INTERVAL = 500

  CODE_INTERVAL_INVALID = 'interval_invalid'
  CODE_INTERVAL_TOO_BIG = 'interval_too_big'

  templates = {
    CODE_INTERVAL_INVALID: '``start`` must be <= ``stop``',
    CODE_INTERVAL_TOO_BIG: '``stop`` - ``start`` must be <= {max_interval}',
  }

  def __init__(self):
    super(GetAccountDataRequestFilter, self).__init__(
      {
        # Required parameters.
        'seed': f.Required | Trytes(result_type=Seed),

        # Optional parameters.
        'stop':   f.Type(int) | f.Min(0),
        'start':  f.Type(int) | f.Min(0) | f.Optional(0),

        'inclusionStates': f.Type(bool) | f.Optional(False),
      },

      allow_missing_keys = {
        'stop',
        'inclusionStates',
        'start',
      },
    )

  def _apply(self, value):
    # noinspection PyProtectedMember
    filtered = super(GetAccountDataRequestFilter, self)._apply(value)

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
            'stop':   filtered['stop'],
          },

          template_vars = {
            'max_interval': self.MAX_INTERVAL,
          },
        )

    return filtered
