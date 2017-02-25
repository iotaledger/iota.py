# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, Iterable, List, Tuple

from iota import Address, Bundle, Transaction, \
  TransactionHash
from iota.adapter import BaseAdapter
from iota.commands.core.find_transactions import FindTransactionsCommand
from iota.commands.core.get_trytes import GetTrytesCommand
from iota.commands.extended.get_bundles import GetBundlesCommand
from iota.commands.extended.get_latest_inclusion import \
  GetLatestInclusionCommand
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed


def find_transaction_objects(adapter, **kwargs):
    # type: (BaseAdapter, dict) -> List[Transaction]
    """
    Finds transactions matching the specified criteria, fetches the
    corresponding trytes and converts them into Transaction objects.
    """
    ft_response = FindTransactionsCommand(adapter)(**kwargs)

    hashes = ft_response['hashes']

    if hashes:
      gt_response = GetTrytesCommand(adapter)(hashes=hashes)

      return list(map(
        Transaction.from_tryte_string,
        gt_response.get('trytes') or [],
      )) # type: List[Transaction]

    return []


def iter_used_addresses(adapter, seed, start):
  # type: (BaseAdapter, Seed, int) -> Generator[Tuple[Address, List[TransactionHash]]]
  """
  Scans the Tangle for used addresses.

  This is basically the opposite of invoking ``getNewAddresses`` with
  ``stop=None``.
  """
  ft_command = FindTransactionsCommand(adapter)

  for addy in AddressGenerator(seed).create_iterator(start):
    ft_response = ft_command(addresses=[addy])

    if ft_response['hashes']:
      yield addy, ft_response['hashes']
    else:
      break

    # Reset the command so that we can call it again.
    ft_command.reset()


def get_bundles_from_transaction_hashes(
    adapter,
    transaction_hashes,
    inclusion_states,
):
  # type: (BaseAdapter, Iterable[TransactionHash], bool) -> List[Bundle]
  """
  Given a set of transaction hashes, returns the corresponding bundles,
  sorted by tail transaction timestamp.
  """
  transaction_hashes = list(transaction_hashes)
  if not transaction_hashes:
    return []

  my_bundles = [] # type: List[Bundle]

  # Sort transactions into tail and non-tail.
  tail_transaction_hashes = set()
  non_tail_bundle_hashes  = set()

  gt_response = GetTrytesCommand(adapter)(hashes=transaction_hashes)
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
    for txn in find_transaction_objects(
        adapter = adapter,
        bundles = list(non_tail_bundle_hashes)
    ):
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
    gli_response = GetLatestInclusionCommand(adapter)(
      hashes = list(tail_transaction_hashes),
    )

    for txn in tail_transactions:
      txn.is_confirmed = gli_response['states'].get(txn.hash)

  # Find the bundles for each transaction.
  for txn in tail_transactions:
    gb_response = GetBundlesCommand(adapter)(transaction=txn.hash)
    txn_bundles = gb_response['bundles'] # type: List[Bundle]

    if inclusion_states:
      for bundle in txn_bundles:
        bundle.is_confirmed = txn.is_confirmed

    my_bundles.extend(txn_bundles)

  return list(sorted(
    my_bundles,
      key = lambda bundle_: bundle_.tail_transaction.timestamp,
  ))
