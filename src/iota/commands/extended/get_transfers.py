# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import List, Optional

import filters as f
from iota import Bundle, Transaction
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.find_transactions import FindTransactionsCommand
from iota.commands.core.get_trytes import GetTrytesCommand
from iota.commands.extended.get_bundles import GetBundlesCommand
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
    stop              = request['stop'] # type: Optional[int]
    inclusion_states  = request['inclusionStates'] # type: bool
    seed              = request['seed'] # type: Seed
    start             = request['start'] # type: int

    generator   = AddressGenerator(seed)
    ft_command  = FindTransactionsCommand(self.adapter)

    # Determine the addresses we will be scanning, and pull their
    # transaction hashes.
    if stop is None:
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

        # Reset the command so that we can call it again.
        ft_command.reset()
    else:
      ft_response =\
        ft_command(addresses=generator.get_addresses(start, stop - start))

      hashes = ft_response.get('hashes') or []

    all_bundles = [] # type: List[Bundle]

    if hashes:
      # Sort transactions into tail and non-tail.
      tail_transaction_hashes = set()
      non_tail_bundle_hashes  = set()

      gt_response = GetTrytesCommand(self.adapter)(hashes=hashes)
      all_transactions = list(map(
        Transaction.from_tryte_string,
        gt_response['trytes'],
      )) # type: List[Transaction]

      for txn in all_transactions:
        if txn.is_tail:
          tail_transaction_hashes.add(txn.hash)
        else:
          # Capture the bundle ID instead of the transaction hash so that
          # we can query the node to find the tail transaction for that
          # bundle.
          non_tail_bundle_hashes.add(txn.bundle_hash)

      if non_tail_bundle_hashes:
        for txn in self._find_transactions(bundles=list(non_tail_bundle_hashes)):
          if txn.is_tail:
            if txn.hash not in tail_transaction_hashes:
              all_transactions.append(txn)
              tail_transaction_hashes.add(txn.hash)

      # Filter out all non-tail transactions.
      tail_transactions = [
        txn
          for txn in all_transactions
          if txn.hash in tail_transaction_hashes
      ]

      # Attach inclusion states, if requested.
      if inclusion_states:
        gli_response = GetLatestInclusionCommand(self.adapter)(
          hashes = list(tail_transaction_hashes),
        )

        for txn in tail_transactions:
          txn.is_confirmed = gli_response['states'].get(txn.hash)

      # Find the bundles for each transaction.
      for txn in tail_transactions:
        gb_response = GetBundlesCommand(self.adapter)(transaction=txn.hash)
        txn_bundles = gb_response['bundles'] # type: List[Bundle]

        if inclusion_states:
          for bundle in txn_bundles:
            bundle.is_confirmed = txn.is_confirmed

        all_bundles.extend(txn_bundles)

    return {
      # Sort bundles by tail transaction timestamp.
      'bundles': list(sorted(
        all_bundles,
        key = lambda bundle_: bundle_.tail_transaction.timestamp,
      )),
    }


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
    CODE_INTERVAL_INVALID: '``start`` must be <= ``stop``',
    CODE_INTERVAL_TOO_BIG: '``stop`` - ``start`` must be <= {max_interval}',
  }

  def __init__(self):
    super(GetTransfersRequestFilter, self).__init__(
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
    filtered = super(GetTransfersRequestFilter, self)._apply(value)

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
