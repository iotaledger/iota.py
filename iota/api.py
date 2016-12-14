# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Iterable, List, Optional, Text, Union

from iota.adapter import BaseAdapter, resolve_adapter
from iota.commands import CustomCommand, command_registry
from iota.types import Address, Bundle, Tag, TransactionId, Transfer, \
  TryteString

__all__ = [
  'Iota',
  'StrictIota',
]


class StrictIota(object):
  """
  API to send HTTP requests for communicating with an IOTA node.

  This implementation only exposes the "core" API methods.  For a more
  feature-complete implementation, use :py:class:`Iota` instead.

  References:
    - https://iota.readme.io/docs/getting-started
  """
  def __init__(self, adapter):
    # type: (Union[Text, BaseAdapter]) -> None
    """
    :param adapter: URI string or BaseAdapter instance.
    """
    super(StrictIota, self).__init__()

    if not isinstance(adapter, BaseAdapter):
      adapter = resolve_adapter(adapter)

    self.adapter = adapter # type: BaseAdapter

  def __getattr__(self, command):
    # type: (Text, dict) -> CustomCommand
    """
    Sends an arbitrary API command to the node.

    This method is useful for invoking undocumented or experimental
    methods, or if you just want to troll your node for awhile.

    :param command: The name of the command to send.

    References:
      - https://iota.readme.io/docs/making-requests
    """
    try:
      return command_registry[command](self.adapter)
    except KeyError:
      return CustomCommand(self.adapter, command)

  def add_neighbors(self, uris):
    # type: (Iterable[Text]) -> dict
    """
    Add one or more neighbors to the node.  Lasts until the node is
    restarted.

    :param uris:
      Use format ``udp://<ip address>:<port>``.
      Example: ``add_neighbors(['udp://example.com:14265'])``

    References:
      - https://iota.readme.io/docs/addneighors
    """
    return self.addNeighbors(uris=uris)

  def attach_to_tangle(
      self,
      trunk_transaction,
      branch_transaction,
      trytes,
      min_weight_magnitude = 18,
  ):
    # type: (TransactionId, TransactionId, Iterable[TryteString], int) -> dict
    """
    Attaches the specified transactions (trytes) to the Tangle by doing
    Proof of Work. You need to supply branchTransaction as well as
    trunkTransaction (basically the tips which you're going to
    validate and reference with this transaction) - both of which
    you'll get through the getTransactionsToApprove API call.

    The returned value is a different set of tryte values which you can
    input into :py:method:`broadcast_transactions` and
    :py:method:`store_transactions`.

    References:
      - https://iota.readme.io/docs/attachtotangle
    """
    return self.attachToTangle(
      trunk_transaction     = trunk_transaction,
      branch_transaction    = branch_transaction,
      min_weight_magnitude  = min_weight_magnitude,
      trytes                = trytes,
    )

  def broadcast_transactions(self, trytes):
    # type: (Iterable[TryteString]) -> dict
    """
    Broadcast a list of transactions to all neighbors.

    The input trytes for this call are provided by
    :py:method:`attach_to_tangle`.

    References:
      - https://iota.readme.io/docs/broadcasttransactions
    """
    return self.broadcastTransactions(trytes=trytes)

  def find_transactions(
      self,
      bundles   = None,
      addresses = None,
      tags      = None,
      approvees = None,
  ):
    # type: (Optional[Iterable[TransactionId]], Optional[Iterable[Address]], Optional[Iterable[Tag]], Optional[Iterable[TransactionId]]) -> dict
    """
    Find the transactions which match the specified input and return.

    All input values are lists, for which a list of return values
    (transaction hashes), in the same order, is returned for all
    individual elements.

    Using multiple of these input fields returns the intersection of
    the values.

    :param bundles: List of transaction IDs.
    :param addresses: List of addresses.
    :param tags: List of tags. Each tag must be 27 trytes.
    :param approvees: List of approvee transaction IDs.

    References:
      - https://iota.readme.io/docs/findtransactions
    """
    return self.findTransactions(
      bundles   = bundles,
      addresses = addresses,
      tags      = tags,
      approvees = approvees,
    )

  def get_balances(self, addresses, threshold=100):
    # type: (Iterable[Address], int) -> dict
    """
    Similar to `get_inclusion_states`. Returns the confirmed balance
    which a list of addresses have at the latest confirmed milestone.

    In addition to the balances, it also returns the milestone as well
    as the index with which the confirmed balance was determined.
    The balances are returned as a list in the same order as the
    addresses were provided as input.

    :param addresses:
      List of addresses to get the confirmed balance for.

    :param threshold: Confirmation threshold.

    References:
      - https://iota.readme.io/docs/getbalances
    """
    return self.getBalances(
      addresses = addresses,
      threshold = threshold,
    )

  def get_inclusion_states(self, transactions, tips):
    # type: (Iterable[TransactionId], Iterable[TransactionId]) -> dict
    """
    Get the inclusion states of a set of transactions. This is for
    determining if a transaction was accepted and confirmed by the
    network or not. You can search for multiple tips (and thus,
    milestones) to get past inclusion states of transactions.

    :param transactions:
      List of transactions you want to get the inclusion state for.

    :param tips:
      List of tips (including milestones) you want to search for the
      inclusion state.

    References:
      - https://iota.readme.io/docs/getinclusionstates
    """
    return self.getInclusionStates(
      transactions  = transactions,
      tips          = tips,
    )

  def get_neighbors(self):
    # type: () -> dict
    """
    Returns the set of neighbors the node is connected with, as well as
    their activity count.

    The activity counter is reset after restarting IRI.

    References:
      - https://iota.readme.io/docs/getneighborsactivity
    """
    return self.getNeighbors()

  def get_node_info(self):
    # type: () -> dict
    """
    Returns information about the node.

    References:
      - https://iota.readme.io/docs/getnodeinfo
    """
    return self.getNodeInfo()

  def get_tips(self):
    # type: () -> dict
    """
    Returns the list of tips (transactions which have no other
    transactions referencing them).

    References:
      - https://iota.readme.io/docs/gettips
      - https://iota.readme.io/docs/glossary#iota-terms
    """
    return self.getTips()

  def get_transactions_to_approve(self, depth):
    # type: (int) -> dict
    """
    Tip selection which returns ``trunkTransaction`` and
    ``branchTransaction``.

    :param depth:
      Determines how many bundles to go back to when finding the
      transactions to approve.

      The higher the depth value, the more "babysitting" the node will
      perform for the network (as it will confirm more transactions
      that way).

    References:
      - https://iota.readme.io/docs/gettransactionstoapprove
    """
    return self.getTransactionsToApprove(depth=depth)

  def get_trytes(self, hashes):
    # type: (Iterable[TransactionId]) -> dict
    """
    Returns the raw transaction data (trytes) of one or more
    transactions.

    References:
      - https://iota.readme.io/docs/gettrytes
    """
    return self.getTrytes(hashes=hashes)

  def interrupt_attaching_to_tangle(self):
    # type: () -> dict
    """
    Interrupts and completely aborts the :py:method:`attach_to_tangle`
    process.

    References:
      - https://iota.readme.io/docs/interruptattachingtotangle
    """
    return self.interruptAttachingToTangle()

  def remove_neighbors(self, uris):
    # type: (Iterable[Text]) -> dict
    """
    Removes one or more neighbors from the node.  Lasts until the node
    is restarted.

    :param uris:
      Use format ``udp://<ip address>:<port>``.
      Example: `remove_neighbors(['udp://example.com:14265'])`

    References:
      - https://iota.readme.io/docs/removeneighors
    """
    return self.removeNeighbors(uris=uris)

  def store_transactions(self, trytes):
    # type: (Iterable[TryteString]) -> dict
    """
    Store transactions into local storage.

    The input trytes for this call are provided by
    :py:method:`attach_to_tangle`.

    References:
      - https://iota.readme.io/docs/storetransactions
    """
    return self.storeTransactions(trytes=trytes)


class Iota(StrictIota):
  """
  Implements the core API, plus additional wrapper methods for common
  operations.

  References:
    - https://iota.readme.io/docs/getting-started
    - https://github.com/iotaledger/wiki/blob/master/api-proposal.md
  """
  def __init__(self, adapter, seed=None):
    # type: (Union[Text, BaseAdapter], Optional[TryteString]) -> None
    """
    :param seed:
      Seed used to generate new addresses.
      If not provided, a random one will be generated.

      Note: This value is never transferred to the node/network.
    """
    super(Iota, self).__init__(adapter)

    self.seed = seed

  def get_inputs(self, start=None, end=None, threshold=None):
    # type: (Optional[int], Optional[int], Optional[int]) -> dict
    """
    Gets all possible inputs of a seed and returns them with the total
    balance.

    This is either done deterministically (by generating all addresses
    until :py:method:`find_transactions` returns an empty
    result and then doing :py:method:`get_balances`), or by providing a
    key range to search.

    :param start:     Starting key index.
    :param end:       Starting key index.
    :param threshold: Minimum required balance of accumulated inputs.

    :return:
      Dict with the following keys::

         {
           'inputs':        <list of Input objects>,
           'totalBalance':  <aggregate balance of all inputs>,
         }

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getinputs
    """
    raise NotImplementedError('Not implemented yet.')

  def prepare_transfers(self, transfers, inputs=None, change_address=None):
    # type: (Iterable[Transfer], Optional[Iterable[TransactionId]], Optional[Address]) -> List[TryteString]
    """
    Prepares transactions to be broadcast to the Tangle, by generating
    the correct bundle, as well as choosing and signing the inputs (for
    value transfers).

    :param transfers: Transfer objects to prepare.

    :param inputs:
      List of inputs used to fund the transfer.
      Not needed for zero-value transfers.

    :param change_address:
      If inputs are provided, any unspent amount will be sent to this
      address.

      If not specified, a change address will be generated
      automatically.

    :return:
      Array containing the trytes of the new bundle.
      This value can be provided to :py:method:`broadcastTransaction`
      and/or :py:method:`storeTransaction`.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#preparetransfers
    """
    raise NotImplementedError('Not implemented yet.')

  def get_new_address(self, index=None, count=1):
    # type: (Optional[int], Optional[int]) -> List[Address]
    """
    Generates one or more new addresses from a seed.

    Note that this method always returns a list of addresses, even if
    only one address is generated.

    :param index:
      Specify the index of the new address.
      If not provided, the address will generated deterministically.

    :param count:
      Number of addresses to generate.
      This is more efficient than calling :py:method:`get_new_address`
      inside a loop.

    :return: List of generated addresses.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getnewaddress
    """
    raise NotImplementedError('Not implemented yet.')

  def get_bundle(self, transaction):
    # type: (TransactionId) -> List[Bundle]
    """
    Returns the bundle associated with the specified transaction hash.

    :param transaction:
      Transaction hash.  Can be any type of transaction (tail or non-
      tail).

    :return:
      List of bundles associated with the transaction.
      If there are multiple bundles (e.g., because of a replay), all
      valid matching bundles will be returned.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getbundle
    """
    raise NotImplementedError('Not implemented yet.')

  def get_transfers(self, indexes=None, inclusion_states=False):
    # type: (Optional[Iterable[int]], bool) -> List[Bundle]
    """
    Returns all transfers associated with the seed.

    :param indexes:
      If specified, use addresses at these indexes to perform the
      search.

      If not provided, _all_ transfers associated with the seed will be
      returned.

    :param inclusion_states:
      Whether to also fetch the inclusion states of the transfers.

      This requires an additional API call to the node, so it is
      disabled by default.

    :return: List of bundles.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#gettransfers
    """
    raise NotImplementedError('Not implemented yet.')

  def replay_transfer(self, transaction):
    # type: (TransactionId) -> Bundle
    """
    Takes a tail transaction hash as input, gets the bundle associated
    with the transaction and then replays the bundle by attaching it to
    the tangle.

    :param transaction: Transaction hash.  Must be a tail.

    :return: The bundle containing the replayed transfer.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#replaytransfer
    """
    raise NotImplementedError('Not implemented yet.')

  def send_transfer(
      self,
      depth,
      transfers,
      inputs                = None,
      change_address        = None,
      min_weight_magnitude  = 18,
  ):
    # type: (int, Iterable[Transfer], Optional[Iterable[TransactionId]], Optional[Address], int) -> Bundle
    """
    Prepares a set of transfers and creates the bundle, then attaches
    the bundle to the Tangle, and broadcasts and stores the
    transactions.

    :param depth: Depth at which to attach the bundle.
    :param transfers: Transfers to include in the bundle.

    :param inputs:
      List of inputs used to fund the transfer.
      Not needed for zero-value transfers.

    :param change_address:
      If inputs are provided, any unspent amount will be sent to this
      address.

      If not specified, a change address will be generated
      automatically.

    :param min_weight_magnitude:
      Min weight magnitude, used by the node to calibrate Proof of
      Work.

    :return: The newly-attached bundle.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#sendtransfer
    """
    raise NotImplementedError('Not implemented yet.')

  def send_trytes(self, trytes, depth, min_weight_magnitude=18):
    # type: (Iterable[TryteString], int, int) -> List[TryteString]
    """
    Attaches transaction trytes to the Tangle, then broadcasts and
    stores them.

    :param trytes:
      Transaction encoded as a tryte sequence.

    :param depth: Depth at which to attach the bundle.

    :param min_weight_magnitude:
      Min weight magnitude, used by the node to calibrate Proof of
      Work.

    :return: The trytes that were attached to the Tangle.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#sendtrytes
    """
    raise NotImplementedError('Not implemented yet.')

  def broadcast_and_store(self, trytes):
    # type: (Iterable[TryteString]) -> List[TryteString]
    """
    Broadcasts and stores a set of transaction trytes.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#broadcastandstore
    """
    return self.broadcastAndStore(trytes=trytes)
