# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import List, Optional

import filters as f
from iota import Transaction
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.find_transactions import FindTransactionsCommand
from iota.commands.core.get_trytes import GetTrytesCommand
from iota.commands.extended.get_latest_inclusion import \
  GetLatestInclusionCommand
from iota.crypto.addresses import AddressGenerator
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
    # Optional parameters.
    end               = request.get('end') # type: Optional[int]
    inclusion_states  = request.get('inclusion_states', False) # type: bool

    # Required parameters.
    start = request['start'] # type: int
    seed  = request['seed'] # type: Seed

    generator   = AddressGenerator(seed)
    ft_command  = FindTransactionsCommand(self.adapter)

    # Determine the addresses we will be scanning, and pull their
    # transaction hashes.
    if end is None:
      # This is similar to the ``getNewAddresses`` command, except it
      # is interested in all the addresses that `getNewAddresses`
      # skips.
      hashes = []
      for addy in generator.create_generator(start):
        ft_response = ft_command(addresses=[addy])

        if ft_response.get('hashes'):
          hashes += ft_response['hashes']
        else:
          break
    else:
      ft_response =\
        ft_command(addresses=generator.get_addresses(start, end - start))

      hashes = ft_response.get('hashes') or []

    # Sort transactions into tail and non-tail.
    tails     = set()
    non_tails = set()

    transactions = self._find_transactions(hashes=hashes)

    for t in transactions:
      if t.is_tail:
        tails.add(t.hash)
      else:
        # Capture the bundle ID instead of the transaction hash so that
        # we can query the node to find the tail transaction for that
        # bundle.
        non_tails.add(t.bundle_id)

    if non_tails:
      for t in self._find_transactions(bundles=non_tails):
        if t.is_tail:
          tails.add(t.hash)

    # Attach inclusion states, if requested.
    if inclusion_states:
      gli_response = GetLatestInclusionCommand(self.adapter)(
        hashes = tails,
      )

      for t in transactions:
        t.is_confirmed = gli_response['states'].get(t.hash)

    # :todo: Invoke getBundle.
    # :todo: Sort bundles by timestamp and return.


  def _find_transactions(self, **kwargs):
    # type: (dict) -> List[Transaction]
    """
    Finds transactions matching the specified criteria, fetches the
    corresponding trytes and converts them into Transaction objects.
    """
    ft_response = FindTransactionsCommand(self.adapter)(**kwargs)

    hashes = ft_response.get('hashes') or []

    if hashes:
      gt_response = GetTrytesCommand(self.adapter)(hashes=hashes)

      return list(map(
        Transaction.from_tryte_string,
        gt_response.get('trytes') or [],
      )) # type: List[Transaction]

    return []


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
