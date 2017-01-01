# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Dict, Iterable, List, Optional, Text

from iota import AdapterSpec, Address, Bundle, ProposedTransaction, Tag, \
  TransactionHash, TryteString, TrytesCompatible
from iota.adapter import BaseAdapter, resolve_adapter
from iota.commands import CustomCommand, command_registry
from iota.crypto.types import Seed

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
  def __init__(self, adapter, testnet=False):
    # type: (AdapterSpec, bool) -> None
    """
    :param adapter:
      URI string or BaseAdapter instance.

    :param testnet:
      Whether to use testnet settings for this instance.
    """
    super(StrictIota, self).__init__()

    if not isinstance(adapter, BaseAdapter):
      adapter = resolve_adapter(adapter)

    self.adapter  = adapter # type: BaseAdapter
    self.testnet = testnet

  def __getattr__(self, command):
    # type: (Text, dict) -> CustomCommand
    """
    Sends an arbitrary API command to the node.

    This method is useful for invoking undocumented or experimental
    methods, or if you just want to troll your node for awhile.

    :param command:
      The name of the command to send.

    References:
      - https://iota.readme.io/docs/making-requests
    """
    try:
      return command_registry[command](self.adapter)
    except KeyError:
      return CustomCommand(self.adapter, command)

  @property
  def default_min_weight_magnitude(self):
    # type: () -> int
    """
    Returns the default ``min_weight_magnitude`` value to use for API
    requests.
    """
    return 13 if self.testnet else 18

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
      min_weight_magnitude = None,
  ):
    # type: (TransactionHash, TransactionHash, Iterable[TryteString], int) -> dict
    """
    Attaches the specified transactions (trytes) to the Tangle by doing
    Proof of Work. You need to supply branchTransaction as well as
    trunkTransaction (basically the tips which you're going to
    validate and reference with this transaction) - both of which
    you'll get through the getTransactionsToApprove API call.

    The returned value is a different set of tryte values which you can
    input into :py:meth:`broadcast_transactions` and
    :py:meth:`store_transactions`.

    References:
      - https://iota.readme.io/docs/attachtotangle
    """
    if min_weight_magnitude is None:
      min_weight_magnitude = self.default_min_weight_magnitude

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
    :py:meth:`attach_to_tangle`.

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
    # type: (Optional[Iterable[TransactionHash]], Optional[Iterable[Address]], Optional[Iterable[Tag]], Optional[Iterable[TransactionHash]]) -> dict
    """
    Find the transactions which match the specified input and return.

    All input values are lists, for which a list of return values
    (transaction hashes), in the same order, is returned for all
    individual elements.

    Using multiple of these input fields returns the intersection of
    the values.

    :param bundles:
      List of transaction IDs.

    :param addresses:
      List of addresses.

    :param tags:
      List of tags.

    :param approvees:
      List of approvee transaction IDs.

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
    Similar to :py:meth:`get_inclusion_states`. Returns the confirmed
    balance which a list of addresses have at the latest confirmed
    milestone.

    In addition to the balances, it also returns the milestone as well
    as the index with which the confirmed balance was determined.
    The balances are returned as a list in the same order as the
    addresses were provided as input.

    :param addresses:
      List of addresses to get the confirmed balance for.

    :param threshold:
      Confirmation threshold.

    References:
      - https://iota.readme.io/docs/getbalances
    """
    return self.getBalances(
      addresses = addresses,
      threshold = threshold,
    )

  def get_inclusion_states(self, transactions, tips):
    # type: (Iterable[TransactionHash], Iterable[TransactionHash]) -> dict
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
    # type: (Iterable[TransactionHash]) -> dict
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
    Interrupts and completely aborts the :py:meth:`attach_to_tangle`
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
    :py:meth:`attach_to_tangle`.

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
  def __init__(self, adapter, seed=None, testnet=False):
    # type: (AdapterSpec, Optional[TrytesCompatible], bool) -> None
    """
    :param seed:
      Seed used to generate new addresses.
      If not provided, a random one will be generated.

      Note: This value is never transferred to the node/network.
    """
    super(Iota, self).__init__(adapter, testnet)

    self.seed = Seed(seed) if seed else Seed.random()

  def broadcast_and_store(self, trytes):
    # type: (Iterable[TryteString]) -> List[TryteString]
    """
    Broadcasts and stores a set of transaction trytes.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#broadcastandstore
    """
    return self.broadcastAndStore(trytes=trytes)

  def get_bundles(self, transaction):
    # type: (TransactionHash) -> dict
    """
    Returns the bundle(s) associated with the specified transaction
    hash.

    :param transaction:
      Transaction hash.  Can be any type of transaction (tail or non-
      tail).

    :return:
      Dict with the following structure::

         {
           'bundles': List[Bundle]
             List of matching bundles.  Note that this value is always
             a list, even if only one bundle was found.
         }

    :raise:
      - :py:class:`iota.adapter.BadApiResponse` if any of the
        bundles fails validation.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getbundle
    """
    return self.getBundles(transaction=transaction)

  def get_inputs(self, start=None, end=None, threshold=None):
    # type: (Optional[int], Optional[int], Optional[int]) -> dict
    """
    Gets all possible inputs of a seed and returns them with the total
    balance.

    This is either done deterministically (by generating all addresses
    until :py:meth:`find_transactions` returns an empty
    result and then doing :py:meth:`get_balances`), or by providing a
    key range to search.

    :param start:
      Starting key index.

    :param end:
      Stop before this index.
      Note that this parameter behaves like the ``stop`` attribute in a
      :py:class:`slice` object; the end index is _not_ included in the
      result.

      If not specified, then this method will not stop until it finds
      an unused address.

    :param threshold:
      Determines the minimum threshold for a successful result.

      - As soon as this threshold is reached, iteration will stop.
      - If the command runs out of addresses before the threshold is
        reached, an exception is raised.

    :return:
      Dict with the following structure::

         {
           'inputs': [
              {
                'address':  <Address object>,
                'balance':  <address balance>,
                'keyIndex`: <index of the address>,
              },
              ... <one object per input found>
           ]

           'totalBalance':  <aggregate balance of all inputs>,
         }

    :raise:
      - :py:class:`iota.adapter.BadApiResponse` if ``threshold`` is not
        met.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getinputs
    """
    return self.getInputs(
      seed      = self.seed,
      start     = start,
      end       = end,
      threshold = threshold,
    )

  def get_latest_inclusion(self, hashes):
    # type: (Iterable[TransactionHash]) -> Dict[TransactionHash, bool]
    """
    Fetches the inclusion state for the specified transaction hashes,
    as of the latest milestone that the node has processed.

    Effectively, this is ``getNodeInfo`` + ``getInclusionStates``.

    :param hashes:
      Iterable of transaction hashes.

    :return:
      {<TransactionHash>: <bool>}
    """
    return self.getLatestInclusion(hashes=hashes)

  def get_new_addresses(self, index=None, count=1):
    # type: (Optional[int], Optional[int]) -> List[Address]
    """
    Generates one or more new addresses from the seed.

    :param index:
      Specify the index of the new address (must be >= 1).

      If not provided, the address will be generated deterministically.

    :param count:
      Number of addresses to generate (must be >= 1).

      Note: This is more efficient than calling ``get_new_address``
      inside a loop.

    :return:
      List of generated addresses.

      Note that this method always returns a list, even if only one
      address is generated.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getnewaddress
    """
    return self.getNewAddresses(seed=self.seed, index=index, count=count)

  def get_transfers(self, start=0, end=None, inclusion_states=False):
    # type: (int, Optional[int], bool) -> dict
    """
    Returns all transfers associated with the seed.

    :param start:
      Starting key index.

    :param end:
      Stop before this index.
      Note that this parameter behaves like the ``stop`` attribute in a
      :py:class:`slice` object; the end index is _not_ included in the
      result.

      If not specified, then this method will not stop until it finds
      an unused address.

    :param inclusion_states:
      Whether to also fetch the inclusion states of the transfers.

      This requires an additional API call to the node, so it is
      disabled by default.

    :return:
      Dict containing the following values::

         {
           'bundles': List[Bundle]
             Matching bundles, sorted by tail transaction timestamp.
         }

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#gettransfers
    """
    return self.getTransfers(
      seed              = self.seed,
      start             = start,
      end               = end,
      inclusion_states  = inclusion_states,
    )

  def prepare_transfer(self, transfers, inputs=None, change_address=None):
    # type: (Iterable[ProposedTransaction], Optional[Iterable[Address]], Optional[Address]) -> dict
    """
    Prepares transactions to be broadcast to the Tangle, by generating
    the correct bundle, as well as choosing and signing the inputs (for
    value transfers).

    :param transfers: Transaction objects to prepare.

    :param inputs:
      List of addresses used to fund the transfer.
      Ignored for zero-value transfers.

      If not provided, addresses will be selected automatically by
      scanning the Tangle for unspent inputs.  Note: this could take
      awhile to complete.

    :param change_address:
      If inputs are provided, any unspent amount will be sent to this
      address.

      If not specified, a change address will be generated
      automatically.

    :return:
      Dict containing the following values::

         {
           'trytes': List[TryteString]
             Raw trytes for the transactions in the bundle, ready to
             be provided to :py:meth:`send_trytes`.
         }

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#preparetransfers
    """
    return self.prepareTransfer(
      seed            = self.seed,
      transfers       = transfers,
      inputs          = inputs,
      change_address  = change_address,
    )

  def replay_bundle(
      self,
      transaction,
      depth,
      min_weight_magnitude = None,
  ):
    # type: (TransactionHash, int, Optional[int]) -> Bundle
    """
    Takes a tail transaction hash as input, gets the bundle associated
    with the transaction and then replays the bundle by attaching it to
    the tangle.

    :param transaction:
      Transaction hash.  Must be a tail.

    :param depth:
      Depth at which to attach the bundle.

    :param min_weight_magnitude:
      Min weight magnitude, used by the node to calibrate Proof of
      Work.

      If not provided, a default value will be used.

    :return:
      The bundle containing the replayed transfer.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#replaytransfer
    """
    if min_weight_magnitude is None:
      min_weight_magnitude = self.default_min_weight_magnitude

    return self.replayBundle(
      transaction           = transaction,
      depth                 = depth,
      min_weight_magnitude  = min_weight_magnitude,
    )

  def send_transfer(
      self,
      depth,
      transfers,
      inputs                = None,
      change_address        = None,
      min_weight_magnitude  = None,
  ):
    # type: (int, Iterable[ProposedTransaction], Optional[Iterable[Address]], Optional[Address], Optional[int]) -> Bundle
    """
    Prepares a set of transfers and creates the bundle, then attaches
    the bundle to the Tangle, and broadcasts and stores the
    transactions.

    :param depth:
      Depth at which to attach the bundle.

    :param transfers:
      Transfers to include in the bundle.

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

      If not provided, a default value will be used.

    :return:
      The newly-attached bundle.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#sendtransfer
    """
    if min_weight_magnitude is None:
      min_weight_magnitude = self.default_min_weight_magnitude

    return self.sendTransfer(
      seed                  = self.seed,
      depth                 = depth,
      transfers             = transfers,
      inputs                = inputs,
      change_address        = change_address,
      min_weight_magnitude  = min_weight_magnitude,
    )

  def send_trytes(self, trytes, depth, min_weight_magnitude=18):
    # type: (Iterable[TryteString], int, int) -> List[TryteString]
    """
    Attaches transaction trytes to the Tangle, then broadcasts and
    stores them.

    :param trytes:
      Transaction encoded as a tryte sequence.

    :param depth:
      Depth at which to attach the bundle.

    :param min_weight_magnitude:
      Min weight magnitude, used by the node to calibrate Proof of
      Work.

    :return:
      The trytes that were attached to the Tangle.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#sendtrytes
    """
    return self.sendTrytes(
      trytes                = trytes,
      depth                 = depth,
      min_weight_magnitude  = min_weight_magnitude,
    )
