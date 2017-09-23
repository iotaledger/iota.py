# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Dict, Iterable, Optional, Text

from iota import AdapterSpec, Address, ProposedTransaction, Tag, \
  TransactionHash, TransactionTrytes, TryteString, TrytesCompatible
from iota.adapter import BaseAdapter, resolve_adapter
from iota.commands import BaseCommand, CustomCommand, core, \
  discover_commands, extended
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed
from six import with_metaclass

__all__ = [
  'InvalidCommand',
  'Iota',
  'StrictIota',
]


class InvalidCommand(ValueError):
  """
  Indicates that an invalid command name was specified.
  """
  pass


class ApiMeta(type):
  """
  Manages command registries for IOTA API base classes.
  """
  def __init__(cls, name, bases=None, attrs=None):
    super(ApiMeta, cls).__init__(name, bases, attrs)

    if not hasattr(cls, 'commands'):
      cls.commands = {}

    # Copy command registry from base class to derived class, but
    # in the event of a conflict, preserve the derived class'
    # commands.
    commands = {}
    for base in bases:
      if isinstance(base, ApiMeta):
          commands.update(base.commands)

    if commands:
        commands.update(cls.commands)
        cls.commands = commands


class StrictIota(with_metaclass(ApiMeta)):
  """
  API to send HTTP requests for communicating with an IOTA node.

  This implementation only exposes the "core" API methods.  For a more
  feature-complete implementation, use :py:class:`Iota` instead.

  References:
    - https://iota.readme.io/docs/getting-started
  """
  commands = discover_commands('iota.commands.core')

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
    # type: (Text) -> BaseCommand
    """
    Creates a pre-configured command instance.

    This method will only return commands supported by the API class.

    If you want to execute an arbitrary API command, use
    :py:meth:`create_command`.

    :param command:
      The name of the command to create.

    References:
      - https://iota.readme.io/docs/making-requests
    """
    # Fix an error when invoking :py:func:`help`.
    # https://github.com/iotaledger/iota.lib.py/issues/41
    if command == '__name__':
      # noinspection PyTypeChecker
      return None

    try:
      command_class = self.commands[command]
    except KeyError:
      raise InvalidCommand(
        '{cls} does not support {command!r} command.'.format(
          cls     = type(self).__name__,
          command = command,
        ),
      )

    return command_class(self.adapter)

  def create_command(self, command):
    # type: (Text) -> CustomCommand
    """
    Creates a pre-configured CustomCommand instance.

    This method is useful for invoking undocumented or experimental
    methods, or if you just want to troll your node for awhile.

    :param command:
      The name of the command to create.
    """
    return CustomCommand(self.adapter, command)

  @property
  def default_min_weight_magnitude(self):
    # type: () -> int
    """
    Returns the default ``min_weight_magnitude`` value to use for API
    requests.
    """
    return 9 if self.testnet else 14

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
    return core.AddNeighborsCommand(self.adapter)(uris=uris)

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

    return core.AttachToTangleCommand(self.adapter)(
      trunkTransaction    = trunk_transaction,
      branchTransaction   = branch_transaction,
      minWeightMagnitude  = min_weight_magnitude,
      trytes              = trytes,
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
    return core.BroadcastTransactionsCommand(self.adapter)(trytes=trytes)

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
    return core.FindTransactionsCommand(self.adapter)(
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
    return core.GetBalancesCommand(self.adapter)(
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
    return core.GetInclusionStatesCommand(self.adapter)(
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
    return core.GetNeighborsCommand(self.adapter)()

  def get_node_info(self):
    # type: () -> dict
    """
    Returns information about the node.

    References:
      - https://iota.readme.io/docs/getnodeinfo
    """
    return core.GetNodeInfoCommand(self.adapter)()

  def get_tips(self):
    # type: () -> dict
    """
    Returns the list of tips (transactions which have no other
    transactions referencing them).

    References:
      - https://iota.readme.io/docs/gettips
      - https://iota.readme.io/docs/glossary#iota-terms
    """
    return core.GetTipsCommand(self.adapter)()

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
    return core.GetTransactionsToApproveCommand(self.adapter)(depth=depth)

  def get_trytes(self, hashes):
    # type: (Iterable[TransactionHash]) -> dict
    """
    Returns the raw transaction data (trytes) of one or more
    transactions.

    References:
      - https://iota.readme.io/docs/gettrytes
    """
    return core.GetTrytesCommand(self.adapter)(hashes=hashes)

  def interrupt_attaching_to_tangle(self):
    # type: () -> dict
    """
    Interrupts and completely aborts the :py:meth:`attach_to_tangle`
    process.

    References:
      - https://iota.readme.io/docs/interruptattachingtotangle
    """
    return core.InterruptAttachingToTangleCommand(self.adapter)()

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
    return core.RemoveNeighborsCommand(self.adapter)(uris=uris)

  def store_transactions(self, trytes):
    # type: (Iterable[TryteString]) -> dict
    """
    Store transactions into local storage.

    The input trytes for this call are provided by
    :py:meth:`attach_to_tangle`.

    References:
      - https://iota.readme.io/docs/storetransactions
    """
    return core.StoreTransactionsCommand(self.adapter)(trytes=trytes)


class Iota(StrictIota):
  """
  Implements the core API, plus additional wrapper methods for common
  operations.

  References:
    - https://iota.readme.io/docs/getting-started
    - https://github.com/iotaledger/wiki/blob/master/api-proposal.md
  """
  commands = discover_commands('iota.commands.extended')

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
    # type: (Iterable[TransactionTrytes]) -> dict
    """
    Broadcasts and stores a set of transaction trytes.

    :return:
      Dict with the following structure::

         {
           'trytes': List[TransactionTrytes],
             List of TransactionTrytes that were broadcast.
             Same as the input ``trytes``.
         }

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#broadcastandstore
    """
    return extended.BroadcastAndStoreCommand(self.adapter)(trytes=trytes)

  def get_account_data(self, start=0, stop=None, inclusion_states=False):
    # type± (int, Optional[int], bool) -> dict
    """
    More comprehensive version of :py:meth:`get_transfers` that returns
    addresses and account balance in addition to bundles.

    This function is useful in getting all the relevant information of
    your account.

    :param start:
      Starting key index.

    :param stop:
      Stop before this index.
      Note that this parameter behaves like the ``stop`` attribute in a
      :py:class:`slice` object; the stop index is *not* included in the
      result.

      If ``None`` (default), then this method will check every address
      until it finds one without any transfers.

    :param inclusion_states:
      Whether to also fetch the inclusion states of the transfers.

      This requires an additional API call to the node, so it is
      disabled by default.

    :return:
      Dict containing the following values::

         {
           'addresses': List[Address],
             List of generated addresses.
             Note that this list may include unused addresses.

           'balance': int,
             Total account balance.  Might be 0.

           'bundles': List[Bundles],
             List of bundles with transactions to/from this account.
         }
    """
    return extended.GetAccountDataCommand(self.adapter)(
      seed            = self.seed,
      start           = start,
      stop            = stop,
      inclusionStates = inclusion_states,
    )

  def get_bundles(self, transaction):
    # type: (TransactionHash) -> dict
    """
    Returns the bundle(s) associated with the specified transaction
    hash.

    :param transaction:
      Transaction hash.  Must be a tail transaction.

    :return:
      Dict with the following structure::

         {
           'bundles': List[Bundle],
             List of matching bundles.  Note that this value is always
             a list, even if only one bundle was found.
         }

    :raise:
      - :py:class:`iota.adapter.BadApiResponse` if any of the
        bundles fails validation.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getbundle
    """
    return extended.GetBundlesCommand(self.adapter)(transaction=transaction)

  def get_inputs(self, start=0, stop=None, threshold=None):
    # type: (int, Optional[int], Optional[int]) -> dict
    """
    Gets all possible inputs of a seed and returns them with the total
    balance.

    This is either done deterministically (by generating all addresses
    until :py:meth:`find_transactions` returns an empty result), or by
    providing a key range to search.

    :param start:
      Starting key index.
      Defaults to 0.

    :param stop:
      Stop before this index.
      Note that this parameter behaves like the ``stop`` attribute in a
      :py:class:`slice` object; the stop index is *not* included in the
      result.

      If ``None`` (default), then this method will not stop until it
      finds an unused address.

    :param threshold:
      If set, determines the minimum threshold for a successful result:

      - As soon as this threshold is reached, iteration will stop.
      - If the command runs out of addresses before the threshold is
        reached, an exception is raised.

      Note that this method does not attempt to "optimize" the result
      (e.g., smallest number of inputs, get as close to ``threshold``
      as possible, etc.); it simply accumulates inputs in order until
      the threshold is met.

      If ``threshold`` is 0, the first address in the key range with
      a non-zero balance will be returned (if it exists).

      If ``threshold`` is ``None`` (default), this method will return
      **all** inputs in the specified key range.

    :return:
      Dict with the following structure::

         {
           'inputs': List[Address],
             Addresses with nonzero balances that can be used as
             inputs.

           'totalBalance': int,
             Aggregate balance from all matching addresses.
         }

      Note that each Address in the result has its ``balance``
      attribute set.

      Example::

         response = iota.get_inputs(...)

         input0 = response['inputs'][0] # type: Address
         input0.balance # 42

    :raise:
      - :py:class:`iota.adapter.BadApiResponse` if ``threshold`` is not
        met.  Not applicable if ``threshold`` is ``None``.

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getinputs
    """
    return extended.GetInputsCommand(self.adapter)(
      seed      = self.seed,
      start     = start,
      stop      = stop,
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
      Dict with one boolean per transaction hash in ``hashes``::

         {
           <TransactionHash>: <bool>,
           ...
         }
    """
    return extended.GetLatestInclusionCommand(self.adapter)(hashes=hashes)

  def get_new_addresses(
      self,
      index = 0,
      count = 1,
      security_level = AddressGenerator.DEFAULT_SECURITY_LEVEL,
  ):
    # type: (int, Optional[int], int) -> dict
    """
    Generates one or more new addresses from the seed.

    :param index:
      Specify the index of the new address (must be >= 1).

    :param count:
      Number of addresses to generate (must be >= 1).

      Note: This is more efficient than calling ``get_new_address``
      inside a loop.

      If ``None``, this method will scan the Tangle to find the next
      available unused address and return that.

    :param security_level:
      Number of iterations to use when generating new addresses.

      Larger values take longer, but the resulting signatures are more
      secure.

      This value must be between 1 and 3, inclusive.

    :return:
      Dict with the following items::

         {
           'addresses': List[Address],
             Always a list, even if only one address was generated.
         }

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getnewaddress
    """
    return extended.GetNewAddressesCommand(self.adapter)(
      count         = count,
      index         = index,
      securityLevel = security_level,
      seed          = self.seed,
    )

  def get_transfers(self, start=0, stop=None, inclusion_states=False):
    # type: (int, Optional[int], bool) -> dict
    """
    Returns all transfers associated with the seed.

    :param start:
      Starting key index.

    :param stop:
      Stop before this index.
      Note that this parameter behaves like the ``stop`` attribute in a
      :py:class:`slice` object; the stop index is *not* included in the
      result.

      If ``None`` (default), then this method will check every address
      until it finds one without any transfers.

    :param inclusion_states:
      Whether to also fetch the inclusion states of the transfers.

      This requires an additional API call to the node, so it is
      disabled by default.

    :return:
      Dict containing the following values::

         {
           'bundles': List[Bundle],
             Matching bundles, sorted by tail transaction timestamp.
         }

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#gettransfers
    """
    return extended.GetTransfersCommand(self.adapter)(
      seed            = self.seed,
      start           = start,
      stop            = stop,
      inclusionStates = inclusion_states,
    )

  def prepare_transfer(self, transfers, inputs=None, change_address=None):
    # type: (Iterable[ProposedTransaction], Optional[Iterable[Address]], Optional[Address]) -> dict
    """
    Prepares transactions to be broadcast to the Tangle, by generating
    the correct bundle, as well as choosing and signing the inputs (for
    value transfers).

    :param transfers:
      Transaction objects to prepare.

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
           'trytes': List[TransactionTrytes],
             Raw trytes for the transactions in the bundle, ready to
             be provided to :py:meth:`send_trytes`.
         }

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#preparetransfers
    """
    return extended.PrepareTransferCommand(self.adapter)(
      seed          = self.seed,
      transfers     = transfers,
      inputs        = inputs,
      changeAddress = change_address,
    )

  def replay_bundle(
      self,
      transaction,
      depth,
      min_weight_magnitude = None,
  ):
    # type: (TransactionHash, int, Optional[int]) -> dict
    """
    Takes a tail transaction hash as input, gets the bundle associated
    with the transaction and then replays the bundle by attaching it to
    the Tangle.

    :param transaction:
      Transaction hash.  Must be a tail.

    :param depth:
      Depth at which to attach the bundle.

    :param min_weight_magnitude:
      Min weight magnitude, used by the node to calibrate Proof of
      Work.

      If not provided, a default value will be used.

    :return:
      Dict containing the following values::

         {
           'trytes': List[TransactionTrytes],
             Raw trytes that were published to the Tangle.
         }

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#replaytransfer
    """
    if min_weight_magnitude is None:
      min_weight_magnitude = self.default_min_weight_magnitude

    return extended.ReplayBundleCommand(self.adapter)(
      transaction         = transaction,
      depth               = depth,
      minWeightMagnitude  = min_weight_magnitude,
    )

  def send_transfer(
      self,
      depth,
      transfers,
      inputs                = None,
      change_address        = None,
      min_weight_magnitude  = None,
  ):
    # type: (int, Iterable[ProposedTransaction], Optional[Iterable[Address]], Optional[Address], Optional[int]) -> dict
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
      Dict containing the following values::

         {
           'bundle': Bundle,
             The newly-published bundle.
         }

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#sendtransfer
    """
    if min_weight_magnitude is None:
      min_weight_magnitude = self.default_min_weight_magnitude

    return extended.SendTransferCommand(self.adapter)(
      seed                = self.seed,
      depth               = depth,
      transfers           = transfers,
      inputs              = inputs,
      changeAddress       = change_address,
      minWeightMagnitude  = min_weight_magnitude,
    )

  def send_trytes(self, trytes, depth, min_weight_magnitude=None):
    # type: (Iterable[TransactionTrytes], int, Optional[int]) -> dict
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

      If not provided, a default value will be used.

    :return:
      Dict containing the following values::

         {
           'trytes': List[TransactionTrytes],
             Raw trytes that were published to the Tangle.
         }

    References:
      - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#sendtrytes
    """
    if min_weight_magnitude is None:
      min_weight_magnitude = self.default_min_weight_magnitude

    return extended.SendTrytesCommand(self.adapter)(
      trytes              = trytes,
      depth               = depth,
      minWeightMagnitude  = min_weight_magnitude,
    )
