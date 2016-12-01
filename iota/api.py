# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from abc import ABCMeta
from inspect import isabstract as is_abstract
from typing import Dict, Iterable, Optional, Text, Union

from six import with_metaclass

from iota.adapter import BaseAdapter, resolve_adapter
from iota.types import TransactionId, TryteString

__all__ = [
  'IotaApi',
]


command_registry = {} # type: Dict[Text, CommandMeta]
"""Registry of commands, indexed by command name."""

class CommandMeta(ABCMeta):
  """Automatically register new commands."""
  # noinspection PyShadowingBuiltins
  def __init__(cls, what, bases=None, dict=None):
    super(CommandMeta, cls).__init__(what, bases, dict)

    if not is_abstract(cls):
      command = getattr(cls, 'command')
      if command:
        command_registry[command] = cls


class BaseCommand(with_metaclass(CommandMeta)):
  """An API command ready to send to the node."""
  command = None # Text

  def __init__(self, adapter):
    # type: (BaseAdapter) -> None
    self.adapter = adapter
    self.response = None # type: dict

  def __call__(self, **kwargs):
    # type: (dict) -> dict
    """Sends the command to the node."""
    if self.called:
      raise ValueError('Command has already been called.')

    self.response = self.adapter.send_request(self._prepare_request(kwargs))

    replacement = self._prepare_response(self.response)
    if replacement is not None:
      self.response = replacement

    return self.response

  @property
  def called(self):
    # type: () -> bool
    """Returns whether this command has been called."""
    return self.response is not None

  def _prepare_request(self, params):
    # type: (dict) -> dict
    """Returns the actual payload to be sent to the node."""
    payload = {'command': self.command}
    payload.update(params)
    return payload

  def _prepare_response(self, response):
    # type: (dict) -> Optional[dict]
    """
    Modifies the response from the node.

    If this method returns a dict, it will replace the response
      entirely.
    """
    pass


class CustomCommand(BaseCommand):
  """Used to execute experimental/undocumented commands."""
  def __init__(self, adapter, command):
    # type: (BaseAdapter, Text) -> None
    super(CustomCommand, self).__init__(adapter)

    self.command = command


# Populate the command registry.
# noinspection PyUnresolvedReferences
from iota.commands import *


class IotaApi(object):
  """
  API to send HTTP requests for communicating with an IOTA node.

  :see: https://iota.readme.io/docs/getting-started
  """
  def __init__(self, adapter):
    # type: (Union[Text, BaseAdapter]) -> None
    """
    :param adapter: URI string or BaseAdapter instance.
    """
    super(IotaApi, self).__init__()

    if not isinstance(adapter, BaseAdapter):
      adapter = resolve_adapter(adapter)

    self.adapter = adapter # type: BaseAdapter

  def __getattr__(self, command):
    # type: (Text, dict) -> CustomCommand
    """
    Sends an arbitrary API command to the node.

    This method is useful for invoking unsupported or experimental
      methods, or if you just want to troll your node for awhile.

    :param command: The name of the command to send.
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

    :param uris: Use format `udp://<ip address>:<port>`.
      Example: `add_neighbors(['udp://example.com:14265'])`

    :see: https://iota.readme.io/docs/addneighors
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
      input into `broadcast_transactions` and `store_transactions`.

    :see: https://iota.readme.io/docs/attachtotangle
    """
    if not isinstance(trunk_transaction, TransactionId):
      raise TypeError(
        'trunk_transaction has wrong type '
        '(expected TransactionID, actual {type}).'.format(
          type = type(trunk_transaction).__name__,
        ),
      )

    if not isinstance(branch_transaction, TransactionId):
      raise TypeError(
        'branch_transaction has wrong type '
        '(expected TransactionID, actual {type}).'.format(
          type = type(branch_transaction).__name__,
        ),
      )

    if type(min_weight_magnitude) is not int:
      raise TypeError(
        'min_weight_magnitude has wrong type '
        '(expected int, actual {type}).'.format(
          type = type(min_weight_magnitude).__name__,
        ),
      )

    if min_weight_magnitude < 18:
      raise ValueError(
        'min_weight_magnitude is too small '
        '(expected >= 18, actual {value}).'.format(
          value = min_weight_magnitude,
        ),
      )

    if not isinstance(trytes, Iterable):
      raise TypeError(
        'trytes has wrong type (expected Iterable, actual {type}).'.format(
          type = type(trytes).__name__,
        ),
      )

    if not trytes:
      raise ValueError('trytes must not be empty.')

    for i, t in enumerate(trytes):
      if not isinstance(t, TryteString):
        raise TypeError(
          'trytes[{i}] has wrong type '
          '(expected TryteString, actual {type}).'.format(
            i     = i,
            type  = type(t).__name__,
          ),
        )

    response = self.attachToTangle(
      trunkTransaction    = trunk_transaction.trytes,
      branchTransaction   = branch_transaction.trytes,
      minWeightMagnitude  = min_weight_magnitude,
      trytes              = [t.trytes for t in trytes],
    )

    trytes = response.get('trytes')
    if trytes:
      response['trytes'] = [TryteString(t.encode('ascii')) for t in trytes]

    return response

  def broadcast_transactions(self, trytes):
    # type: (Iterable[Text]) -> dict
    """
    Broadcast a list of transactions to all neighbors.

    The input trytes for this call are provided by `attach_to_tangle`.

    :see: https://iota.readme.io/docs/broadcasttransactions
    """
    raise NotImplementedError('Not implemented yet.')

  def find_transactions(
      self,
      bundles   = None,
      addresses = None,
      tags      = None,
      approvees = None,
  ):
    # type: (Optional[Iterable[Text]], Optional[Iterable[Text]], Optional[Iterable[Text]], Optional[Iterable[Text]]) -> dict
    """
    Find the transactions which match the specified input and return.

    All input values are lists, for which a list of return values
      (transaction hashes), in the same order, is returned for all
      individual elements.

    Using multiple of these input fields returns the intersection of
      the values.

    :param bundles: List of bundle hashes.  The hashes will be extended
      to 81 trytes if necessary.
    :param addresses: List of addresses.
    :param tags: List of tags. Each tag must be 27 trytes.
    :param approvees: List of approvee transaction hashes.

    :see: https://iota.readme.io/docs/findtransactions
    """
    raise NotImplementedError('Not implemented yet.')

  def get_balances(self, addresses, threshold=100):
    # type: (Iterable[Text], int) -> dict
    """
    Similar to `get_inclusion_states`. Returns the confirmed balance
      which a list of addresses have at the latest confirmed milestone.

    In addition to the balances, it also returns the milestone as well
      as the index with which the confirmed balance was determined.
      The balances are returned as a list in the same order as the
      addresses were provided as input.

    :param addresses: List of addresses to get the confirmed balance
      for.
    :param threshold: Confirmation threshold.

    :see: https://iota.readme.io/docs/getbalances
    """
    raise NotImplementedError('Not implemented yet.')

  def get_inclusion_states(self, transactions, tips):
    # type: (Iterable[Text], Iterable[Text]) -> dict
    """
    Get the inclusion states of a set of transactions. This is for
      determining if a transaction was accepted and confirmed by the
      network or not. You can search for multiple tips (and thus,
      milestones) to get past inclusion states of transactions.

    :param transactions: List of transactions you want to get the
      inclusion state for.
    :param tips: List of tips (including milestones) you want to search
      for the inclusion state.

    :see: https://iota.readme.io/docs/getinclusionstates
    """
    raise NotImplementedError('Not implemented yet.')

  def get_neighbors(self):
    # type: () -> dict
    """
    Returns the set of neighbors the node is connected with, as well as
      their activity count.

    The activity counter is reset after restarting IRI.

    :see: https://iota.readme.io/docs/getneighborsactivity
    """
    return self.getNeighbors()

  def get_node_info(self):
    # type: () -> dict
    """
    Returns information about the node.

    :see: https://iota.readme.io/docs/getnodeinfo
    """
    return self.getNodeInfo()

  def get_tips(self):
    # type: () -> dict
    """
    Returns the list of tips (transactions which have no other
      transactions referencing them).

    :see: https://iota.readme.io/docs/gettips
    :see: https://iota.readme.io/docs/glossary#iota-terms
    """
    return self.getTips()

  def get_transactions_to_approve(self, depth):
    # type: (int) -> dict
    """
    Tip selection which returns `trunkTransaction` and
      `branchTransaction`.

    :param depth: Determines how many bundles to go back to when
      finding the transactions to approve.

      The higher the depth value, the more "babysitting" the node will
        perform for the network (as it will confirm more transactions
        that way).

    :see: https://iota.readme.io/docs/gettransactionstoapprove
    """
    return self.getTransactionsToApprove(depth=depth)

  def get_trytes(self, hashes):
    # type: (Iterable[Text]) -> dict
    """
    Returns the raw transaction data (trytes) of a specific
      transaction.

    :see: https://iota.readme.io/docs/gettrytes
    """
    raise NotImplementedError('Not implemented yet.')

  def interrupt_attaching_to_tangle(self):
    # type: () -> dict
    """
    Interrupts and completely aborts the `attach_to_tangle` process.

    :see: https://iota.readme.io/docs/interruptattachingtotangle
    """
    return self.interruptAttachingToTangle()

  def remove_neighbors(self, uris):
    # type: (Iterable[Text]) -> dict
    """
    Removes one or more neighbors from the node.  Lasts until the node
      is restarted.

    :param uris: Use format `udp://<ip address>:<port>`.
      Example: `remove_neighbors(['udp://example.com:14265'])`

    :see: https://iota.readme.io/docs/removeneighors
    """
    return self.removeNeighbors(uris=uris)

  def store_transactions(self, trytes):
    # type: (Iterable[Text]) -> dict
    """
    Store transactions into local storage.

    The input trytes for this call are provided by `attach_to_tangle`.

    :see: https://iota.readme.io/docs/storetransactions
    """
    raise NotImplementedError('Not implemented yet.')
