# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Iterable, Optional, Text, Union

from iota.adapter import BaseAdapter, resolve_adapter
from iota.commands import CustomCommand, command_registry
from iota.types import Address, Tag, TransactionId, TryteString

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
  pass
