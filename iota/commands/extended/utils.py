from typing import Iterable, List, Optional, Tuple

from iota import Address, Bundle, Transaction, \
    TransactionHash, TransactionTrytes, BadApiResponse
from iota.adapter import BaseAdapter
from iota.exceptions import with_context
from iota.commands.core.find_transactions import FindTransactionsCommand
from iota.commands.core.get_trytes import GetTrytesCommand
from iota.commands.core.were_addresses_spent_from import \
    WereAddressesSpentFromCommand
from iota.commands.extended import FindTransactionObjectsCommand
from iota.commands.extended.get_bundles import GetBundlesCommand
from iota.commands.extended.get_latest_inclusion import \
    GetLatestInclusionCommand
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed


async def iter_used_addresses(
        adapter: BaseAdapter,
        seed: Seed,
        start: int,
        security_level: Optional[int] = None,
        # 'typing' only supports AsyncGenerator from python 3.6.1, so put it
        # as string literal here.
) -> 'AsyncGenerator[Tuple[Address, List[TransactionHash]], None]':
    """
    Scans the Tangle for used addresses. A used address is an address that
    was spent from or has a transaction.

    This is basically the opposite of invoking ``getNewAddresses`` with
    ``count=None``.

    .. important::
        This is an async generator!

    """
    if security_level is None:
        security_level = AddressGenerator.DEFAULT_SECURITY_LEVEL

    ft_command = FindTransactionsCommand(adapter)
    wasf_command = WereAddressesSpentFromCommand(adapter)

    for addy in AddressGenerator(seed, security_level).create_iterator(start):
        ft_response = await ft_command(addresses=[addy])

        if ft_response['hashes']:
            yield addy, ft_response['hashes']
        else:
            wasf_response = await wasf_command(addresses=[addy])
            if wasf_response['states'][0]:
                yield addy, []
            else:
                break

        # Reset the commands so that we can call them again.
        ft_command.reset()
        wasf_command.reset()


async def get_bundles_from_transaction_hashes(
        adapter: BaseAdapter,
        transaction_hashes: Iterable[TransactionHash],
        inclusion_states: bool,
) -> List[Bundle]:
    """
    Given a set of transaction hashes, returns the corresponding bundles,
    sorted by tail transaction timestamp.
    """
    transaction_hashes = list(transaction_hashes)
    if not transaction_hashes:
        return []

    # Sort transactions into tail and non-tail.
    tail_transaction_hashes = set()
    non_tail_bundle_hashes = set()

    gt_response = await GetTrytesCommand(adapter)(hashes=transaction_hashes)
    for tx_hash, tx_trytes in zip(transaction_hashes, gt_response['trytes']):
        # If no tx was found by the node for tx_hash, it returns 9s,
        # so we check here if it returned all 9s trytes.
        if tx_trytes == TransactionTrytes(''):
            raise with_context(
                    exc=BadApiResponse(
                            'Could not get trytes of transaction {hash} from the Tangle. '
                            '(``exc.context`` has more info).'.format(hash=tx_hash),
                    ),

                    context={
                        'transaction_hash': tx_hash,
                        'returned_transaction_trytes': tx_trytes,
                    },
            )
    all_transactions: List[Transaction] = list(map(
        Transaction.from_tryte_string,
        gt_response['trytes'],
    ))

    for txn in all_transactions:
        if txn.is_tail:
            tail_transaction_hashes.add(txn.hash)
        else:
            # Capture the bundle ID instead of the transaction hash so
            # that we can query the node to find the tail transaction
            # for that bundle.
            non_tail_bundle_hashes.add(txn.bundle_hash)

    if non_tail_bundle_hashes:
        for txn in (await FindTransactionObjectsCommand(adapter=adapter)(
                bundles=list(non_tail_bundle_hashes),
        ))['transactions']:
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
        gli_response = await GetLatestInclusionCommand(adapter)(
            hashes=list(tail_transaction_hashes),
        )

        for txn in tail_transactions:
            txn.is_confirmed = gli_response['states'].get(txn.hash)

    # Find the bundles for each transaction.
    txn_bundles: List[Bundle] = (await GetBundlesCommand(adapter)(
        transactions=[txn.hash for txn in tail_transactions]
    ))['bundles']

    if inclusion_states:
        for bundle, txn in zip(txn_bundles, tail_transactions):
            bundle.is_confirmed = txn.is_confirmed

    return list(sorted(
        txn_bundles,
        key=lambda bundle_: bundle_.tail_transaction.timestamp,
    ))
