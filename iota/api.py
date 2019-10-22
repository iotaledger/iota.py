# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from typing import Dict, Iterable, Optional, Text

from six import add_metaclass

from iota import AdapterSpec, Address, BundleHash, ProposedTransaction, Tag, \
    TransactionHash, TransactionTrytes, TryteString, TrytesCompatible
from iota.adapter import BaseAdapter, resolve_adapter
from iota.commands import BaseCommand, CustomCommand, core, \
    discover_commands, extended
from iota.commands.extended.helpers import Helpers
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed

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


@add_metaclass(ApiMeta)
class StrictIota(object):
    """
    API to send HTTP requests for communicating with an IOTA node.

    This implementation only exposes the "core" API methods.  For a more
    feature-complete implementation, use :py:class:`Iota` instead.

    References:

    - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference
    """
    commands = discover_commands('iota.commands.core')

    def __init__(self, adapter, testnet=False, local_pow=False):
        # type: (AdapterSpec, bool, bool) -> None
        """
        :param adapter:
            URI string or BaseAdapter instance.

        :param testnet:
            Whether to use testnet settings for this instance.
        """
        super(StrictIota, self).__init__()

        if not isinstance(adapter, BaseAdapter):
            adapter = resolve_adapter(adapter)

        self.adapter = adapter  # type: BaseAdapter
        # Note that the `local_pow` parameter is passed to adapter,
        # the api class has no notion about it. The reason being,
        # that this parameter is used in `AttachToTangeCommand` calls,
        # that is called from various api calls (`attach_to_tangle`,
        # `send_trytes` or `send_transfer`). Inside `AttachToTangeCommand`,
        # we no longer have access to the attributes of the API class, therefore
        # `local_pow` needs to be associated with the adapter.
        # Logically, `local_pow` will decide if the api call does pow
        # via pyota-pow extension, or sends the request to a node.
        # But technically, the parameter belongs to the adapter.
        self.adapter.set_local_pow(local_pow)
        self.testnet = testnet

    def __getattr__(self, command):
        # type: (Text) -> BaseCommand
        """
        Creates a pre-configured command instance.

        This method will only return commands supported by the API
        class.

        If you want to execute an arbitrary API command, use
        :py:meth:`create_command`.

        :param command:
            The name of the command to create.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference
        """
        # Fix an error when invoking :py:func:`help`.
        # https://github.com/iotaledger/iota.py/issues/41
        if command == '__name__':
            # noinspection PyTypeChecker
            return None

        # Fix an error when invoking dunder methods.
        # https://github.com/iotaledger/iota.py/issues/206
        if command.startswith("__"):
            # noinspection PyUnresolvedReferences
            return super(StrictIota, self).__getattr__(command)

        try:
            command_class = self.commands[command]
        except KeyError:
            raise InvalidCommand(
                '{cls} does not support {command!r} command.'.format(
                    cls=type(self).__name__,
                    command=command,
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

    def set_local_pow(self, local_pow):
        # type: (bool) -> None
        """
        Sets the local_pow attribute of the adapter of the api instance.
        If it is true, attach_to_tangle command calls external interface
        to perform pow, instead of sending the request to a node.
        By default, it is set to false.
        This particular method is needed if one wants to change
        local_pow behavior dynamically.
        """
        self.adapter.set_local_pow(local_pow)

    @property
    def default_min_weight_magnitude(self):
        # type: () -> int
        """
        Returns the default ``min_weight_magnitude`` value to use for
        API requests.
        """
        return 9 if self.testnet else 14

    def add_neighbors(self, uris):
        # type: (Iterable[Text]) -> dict
        """
        Add one or more neighbors to the node.  Lasts until the node is
        restarted.

        :param uris:
            Use format ``<protocol>://<ip address>:<port>``.
            Example: ``add_neighbors(['udp://example.com:14265'])``

            .. note::
                These URIs are for node-to-node communication (e.g.,
                weird things will happen if you specify a node's HTTP
                API URI here).

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#addneighbors
        """
        return core.AddNeighborsCommand(self.adapter)(uris=uris)

    def attach_to_tangle(
            self,
            trunk_transaction,  # type: TransactionHash
            branch_transaction,  # type: TransactionHash
            trytes,  # type: Iterable[TryteString]
            min_weight_magnitude=None,  # type: Optional[int]
    ):
        # type: (...) -> dict
        """
        Attaches the specified transactions (trytes) to the Tangle by
        doing Proof of Work. You need to supply branchTransaction as
        well as trunkTransaction (basically the tips which you're going
        to validate and reference with this transaction) - both of which
        you'll get through the getTransactionsToApprove API call.

        The returned value is a different set of tryte values which you
        can input into :py:meth:`broadcast_transactions` and
        :py:meth:`store_transactions`.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#attachtotangle
        """
        if min_weight_magnitude is None:
            min_weight_magnitude = self.default_min_weight_magnitude

        return core.AttachToTangleCommand(self.adapter)(
            trunkTransaction=trunk_transaction,
            branchTransaction=branch_transaction,
            minWeightMagnitude=min_weight_magnitude,
            trytes=trytes,
        )

    def broadcast_transactions(self, trytes):
        # type: (Iterable[TryteString]) -> dict
        """
        Broadcast a list of transactions to all neighbors.

        The input trytes for this call are provided by
        :py:meth:`attach_to_tangle`.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#broadcasttransactions
        """
        return core.BroadcastTransactionsCommand(self.adapter)(trytes=trytes)

    def check_consistency(self, tails):
        # type: (Iterable[TransactionHash]) -> dict
        """
        Used to ensure tail resolves to a consistent ledger which is
        necessary to validate before attempting promotionChecks
        transaction hashes for promotability.

        This is called with a pending transaction (or more of them) and
        it will tell you if it is still possible for this transaction
        (or all the transactions simultaneously if you give more than
        one) to be confirmed, or not (because it conflicts with another
        already confirmed transaction).

        :param tails:
            Transaction hashes. Must be tail transactions.

        :return:
            Dict with the following structure::

                {
                    'state': bool,

                    'info': str,
                        This field will only exist set if ``state`` is
                        ``False``.
                }

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#checkconsistency
        """
        return core.CheckConsistencyCommand(self.adapter)(
            tails=tails,
        )

    def find_transactions(
            self,
            bundles=None,  # type: Optional[Iterable[BundleHash]]
            addresses=None,  # type: Optional[Iterable[Address]]
            tags=None,  # type: Optional[Iterable[Tag]]
            approvees=None,  # type: Optional[Iterable[TransactionHash]]
    ):
        # type: (...) -> dict
        """
        Find the transactions which match the specified input and
        return.

        All input values are lists, for which a list of return values
        (transaction hashes), in the same order, is returned for all
        individual elements.

        Using multiple of these input fields returns the intersection of
        the values.

        :param bundles:
          List of bundle IDs.

        :param addresses:
            List of addresses.

        :param tags:
            List of tags.

        :param approvees:
            List of approvee transaction IDs.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#findtransactions
        """
        return core.FindTransactionsCommand(self.adapter)(
            bundles=bundles,
            addresses=addresses,
            tags=tags,
            approvees=approvees,
        )

    def get_balances(
            self,
            addresses,  # type: Iterable[Address]
            threshold=100,  # type: int
            tips=None,  # type: Optional[Iterable[TransactionHash]]
    ):
        # type: (...) -> dict
        """
        Similar to :py:meth:`get_inclusion_states`. Returns the
        confirmed balance which a list of addresses have at the latest
        confirmed milestone.

        In addition to the balances, it also returns the milestone as
        well as the index with which the confirmed balance was
        determined.  The balances are returned as a list in the same
        order as the addresses were provided as input.

        :param addresses:
            List of addresses to get the confirmed balance for.

        :param threshold:
            Confirmation threshold between 0 and 100.

        :param tips:
            Tips whose history of transactions to traverse to find the balance.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#getbalances
        """
        return core.GetBalancesCommand(self.adapter)(
            addresses=addresses,
            threshold=threshold,
            tips=tips,
        )

    def get_inclusion_states(self, transactions, tips):
        # type: (Iterable[TransactionHash], Iterable[TransactionHash]) -> dict
        """
        Get the inclusion states of a set of transactions. This is for
        determining if a transaction was accepted and confirmed by the
        network or not. You can search for multiple tips (and thus,
        milestones) to get past inclusion states of transactions.

        :param transactions:
            List of transactions you want to get the inclusion state
            for.

        :param tips:
            List of tips (including milestones) you want to search for
            the inclusion state.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#getinclusionstates
        """
        return core.GetInclusionStatesCommand(self.adapter)(
            transactions=transactions,
            tips=tips,
        )

    def get_missing_transactions(self):
        # type: () -> dict
        """
        Returns all transaction hashes that a node is currently requesting
        from its neighbors.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#getmissingtransactions
        """
        return core.GetMissingTransactionsCommand(self.adapter)()

    def get_neighbors(self):
        # type: () -> dict
        """
        Returns the set of neighbors the node is connected with, as well
        as their activity count.

        The activity counter is reset after restarting IRI.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#getneighbors
        """
        return core.GetNeighborsCommand(self.adapter)()

    def get_node_api_configuration(self):
        # type: () -> dict
        """
        Returns a node's API configuration settings.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#getnodeapiconfiguration
        """
        return core.GetNodeAPIConfigurationCommand(self.adapter)()

    def get_node_info(self):
        # type: () -> dict
        """
        Returns information about the node.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#getnodeinfo
        """
        return core.GetNodeInfoCommand(self.adapter)()

    def get_tips(self):
        # type: () -> dict
        """
        Returns the list of tips (transactions which have no other
        transactions referencing them).

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#gettips
        - https://docs.iota.org/docs/dev-essentials/0.1/references/glossary
        """
        return core.GetTipsCommand(self.adapter)()

    def get_transactions_to_approve(self, depth, reference=None):
        # type: (int, Optional[TransactionHash]) -> dict
        """
        Tip selection which returns ``trunkTransaction`` and
        ``branchTransaction``.

        :param depth:
          Determines how many bundles to go back to when finding the
          transactions to approve.

          The higher the depth value, the more "babysitting" the node
          will perform for the network (as it will confirm more
          transactions that way).

        :param reference:
          Transaction hash from which to start the weighted random walk.
          Use this parameter to make sure the returned tip transaction hashes
          approve a given reference transaction.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#gettransactionstoapprove
        """
        return core.GetTransactionsToApproveCommand(self.adapter)(
            depth=depth,
            reference=reference,
        )

    def get_trytes(self, hashes):
        # type: (Iterable[TransactionHash]) -> dict
        """
        Returns the raw transaction data (trytes) of one or more
        transactions.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#gettrytes
        """
        return core.GetTrytesCommand(self.adapter)(hashes=hashes)

    def interrupt_attaching_to_tangle(self):
        # type: () -> dict
        """
        Interrupts and completely aborts the :py:meth:`attach_to_tangle`
        process.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#interruptattachingtotangle
        """
        return core.InterruptAttachingToTangleCommand(self.adapter)()

    def remove_neighbors(self, uris):
        # type: (Iterable[Text]) -> dict
        """
        Removes one or more neighbors from the node.  Lasts until the
        node is restarted.

        :param uris:
            Use format ``<protocol>://<ip address>:<port>``.
            Example: `remove_neighbors(['udp://example.com:14265'])`

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#removeneighbors
        """
        return core.RemoveNeighborsCommand(self.adapter)(uris=uris)

    def store_transactions(self, trytes):
        # type: (Iterable[TryteString]) -> dict
        """
        Store transactions into local storage.

        The input trytes for this call are provided by
        :py:meth:`attach_to_tangle`.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#storetransactions
        """
        return core.StoreTransactionsCommand(self.adapter)(trytes=trytes)

    def were_addresses_spent_from(self, addresses):
        # type: (Iterable[Address]) -> dict
        """
        Check if a list of addresses was ever spent from, in the current
        epoch, or in previous epochs.

        :param addresses:
            List of addresses to check.

        References:

        - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference#wereaddressesspentfrom
        """
        return core.WereAddressesSpentFromCommand(self.adapter)(
            addresses=addresses,
        )


class Iota(StrictIota):
    """
    Implements the core API, plus additional wrapper methods for common
    operations.

    References:

    - https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference
    - https://github.com/iotaledger/wiki/blob/master/api-proposal.md
    """
    commands = discover_commands('iota.commands.extended')

    def __init__(self, adapter, seed=None, testnet=False, local_pow=False):
        # type: (AdapterSpec, Optional[TrytesCompatible], bool, bool) -> None
        """
        :param seed:
            Seed used to generate new addresses.
            If not provided, a random one will be generated.

            .. note::
                This value is never transferred to the node/network.
        """
        super(Iota, self).__init__(adapter, testnet, local_pow)

        self.seed = Seed(seed) if seed else Seed.random()
        self.helpers = Helpers(self)

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

    def broadcast_bundle(self, tail_transaction_hash):
        # type (TransactionHash) -> dict
        """
        Re-broadcasts all transactions in a bundle given the tail transaction hash.
        It might be useful when transactions did not properly propagate,
        particularly in the case of large bundles.

        :param tail_transaction_hash:
            Tail transaction hash of the bundle.

        :return:
            Dict with the following structure:::

                {
                    'trytes': List[TransactionTrytes],
                        List of TransactionTrytes that were broadcast.
                }

        References:

        - https://github.com/iotaledger/iota.js/blob/next/api_reference.md#module_core.broadcastBundle
        """

        return extended.BroadcastBundleCommand(self.adapter)(tail_hash=tail_transaction_hash)


    def find_transaction_objects(
            self,
            bundles=None,  # type: Optional[Iterable[BundleHash]]
            addresses=None,  # type: Optional[Iterable[Address]]
            tags=None,  # type: Optional[Iterable[Tag]]
            approvees=None,  # type: Optional[Iterable[TransactionHash]]
    ):
        # type: (...) -> dict
        """
        A more extensive version of :py:meth:`find_transactions` that
        returns transaction objects instead of hashes.

        Effectively, this is ``find_transactions`` + ``get_trytes`` +
        converting the trytes into transaction objects.

        It accepts the same parameters as :py:meth:`find_transactions`

        :param bundles:
          List of bundle IDs.

        :param addresses:
            List of addresses.

        :param tags:
            List of tags.

        :param approvees:
            List of approvee transaction IDs.

        :return:
            Dict with the following structure::

                {
                    'transactions': List[Transaction],
                        List of Transaction objects that match the input.
                }
        """
        return extended.FindTransactionObjectsCommand(self.adapter)(
            bundles=bundles,
            addresses=addresses,
            tags=tags,
            approvees=approvees,
        )

    def get_account_data(self, start=0, stop=None, inclusion_states=False, security_level=None):
        # type: (int, Optional[int], bool, Optional[int]) -> dict
        """
        More comprehensive version of :py:meth:`get_transfers` that
        returns addresses and account balance in addition to bundles.

        This function is useful in getting all the relevant information
        of your account.

        :param start:
            Starting key index.

        :param stop:
            Stop before this index.

            Note that this parameter behaves like the ``stop`` attribute
            in a :py:class:`slice` object; the stop index is *not*
            included in the result.

            If ``None`` (default), then this method will check every
            address until it finds one without any transfers.

        :param inclusion_states:
            Whether to also fetch the inclusion states of the transfers.

            This requires an additional API call to the node, so it is
            disabled by default.

        :param security_level:
            Number of iterations to use when generating new addresses
            (see :py:meth:`get_new_addresses`).

            This value must be between 1 and 3, inclusive.

            If not set, defaults to
            :py:attr:`AddressGenerator.DEFAULT_SECURITY_LEVEL`.

        :return:
            Dict with the following structure::

                {
                    'addresses': List[Address],
                        List of generated addresses.

                        Note that this list may include unused
                        addresses.

                    'balance': int,
                        Total account balance.  Might be 0.

                    'bundles': List[Bundle],
                        List of bundles with transactions to/from this
                        account.
                }
        """
        return extended.GetAccountDataCommand(self.adapter)(
            seed=self.seed,
            start=start,
            stop=stop,
            inclusionStates=inclusion_states,
            security_level=security_level
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
                    List of matching bundles.  Note that this value is
                    always a list, even if only one bundle was found.
             }

        :raise:
          - :py:class:`iota.adapter.BadApiResponse` if any of the
            bundles fails validation.

        References:

        - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getbundle
        """
        return extended.GetBundlesCommand(self.adapter)(transaction=transaction)

    def get_inputs(
            self,
            start=0,
            stop=None,
            threshold=None,
            security_level=None,
    ):
        # type: (int, Optional[int], Optional[int], Optional[int]) -> dict
        """
        Gets all possible inputs of a seed and returns them, along with
        the total balance.

        This is either done deterministically (by generating all
        addresses until :py:meth:`find_transactions` returns an empty
        result), or by providing a key range to search.

        :param start:
            Starting key index.
            Defaults to 0.

        :param stop:
            Stop before this index.

            Note that this parameter behaves like the ``stop`` attribute
            in a :py:class:`slice` object; the stop index is *not*
            included in the result.

            If ``None`` (default), then this method will not stop until
            it finds an unused address.

        :param threshold:
            If set, determines the minimum threshold for a successful
            result:

            - As soon as this threshold is reached, iteration will stop.
            - If the command runs out of addresses before the threshold
              is reached, an exception is raised.

            .. note::
                This method does not attempt to "optimize" the result
                (e.g., smallest number of inputs, get as close to
                ``threshold`` as possible, etc.); it simply accumulates
                inputs in order until the threshold is met.

            If ``threshold`` is 0, the first address in the key range
            with a non-zero balance will be returned (if it exists).

            If ``threshold`` is ``None`` (default), this method will
            return **all** inputs in the specified key range.

        :param security_level:
            Number of iterations to use when generating new addresses
            (see :py:meth:`get_new_addresses`).

            This value must be between 1 and 3, inclusive.

            If not set, defaults to
            :py:attr:`AddressGenerator.DEFAULT_SECURITY_LEVEL`.

        :return:
            Dict with the following structure::

                {
                    'inputs': List[Address],
                        Addresses with nonzero balances that can be used
                        as inputs.

                    'totalBalance': int,
                        Aggregate balance from all matching addresses.
                }

            Note that each Address in the result has its ``balance``
            attribute set.

            Example:

            .. code-block:: python

                response = iota.get_inputs(...)

                input0 = response['inputs'][0] # type: Address
                input0.balance # 42

        :raise:
            - :py:class:`iota.adapter.BadApiResponse` if ``threshold``
              is not met.  Not applicable if ``threshold`` is ``None``.

        References:

        - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getinputs
        """
        return extended.GetInputsCommand(self.adapter)(
            seed=self.seed,
            start=start,
            stop=stop,
            threshold=threshold,
            securityLevel=security_level
        )

    def get_latest_inclusion(self, hashes):
        # type: (Iterable[TransactionHash]) -> Dict[TransactionHash, bool]
        """
        Fetches the inclusion state for the specified transaction
        hashes, as of the latest milestone that the node has processed.

        Effectively, this is ``getNodeInfo`` + ``getInclusionStates``.

        :param hashes:
            Iterable of transaction hashes.

        :return:
            Dict with the following structure::

                {
                    "states": Dict[TransactionHash, bool]
                        Dict with one boolean per transaction hash in
                        ``hashes``.
                }
        """
        return extended.GetLatestInclusionCommand(self.adapter)(hashes=hashes)

    def get_new_addresses(
            self,
            index=0,
            count=1,
            security_level=AddressGenerator.DEFAULT_SECURITY_LEVEL,
            checksum=False,
    ):
        # type: (int, Optional[int], int, bool) -> dict
        """
        Generates one or more new addresses from the seed.

        :param index:
            The key index of the first new address to generate (must be
            >= 1).

        :param count:
            Number of addresses to generate (must be >= 1).

            .. tip::
                This is more efficient than calling ``get_new_address``
                inside a loop.

            If ``None``, this method will progressively generate
            addresses and scan the Tangle until it finds one that has no
            transactions referencing it.

        :param security_level:
            Number of iterations to use when generating new addresses.

            Larger values take longer, but the resulting signatures are
            more secure.

            This value must be between 1 and 3, inclusive.

        :param checksum:
            Specify whether to return the address with the checksum.
            Defaults to ``False``.

        :return:
            Dict with the following structure::

            {
                'addresses': List[Address],
                    Always a list, even if only one address was
                    generated.
            }

        References:

        - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#getnewaddress
        """
        return extended.GetNewAddressesCommand(self.adapter)(
            count=count,
            index=index,
            securityLevel=security_level,
            checksum=checksum,
            seed=self.seed,
        )

    def get_transaction_objects(
            self,
            hashes,  # type: [Iterable[TransactionHash]]
    ):
        # type: (...) -> dict
        """
        Fetches transaction objects from the Tangle given their
        transaction IDs (hashes).

        Effectively, this is ``get_trytes`` +
        converting the trytes into transaction objects.

        Similar to :py:meth:`find_transaction_objects`, but accepts
        list of trnsaction hashes as input.

        :param hashes:
          List of transaction IDs (transaction hashes).

        :return:
            Dict with the following structure::

                {
                    'transactions': List[Transaction],
                        List of Transaction objects that match the input.
                }
        """
        return extended.GetTransactionObjectsCommand(self.adapter)(
            hashes=hashes,
        )

    def get_transfers(self, start=0, stop=None, inclusion_states=False):
        # type: (int, Optional[int], bool) -> dict
        """
        Returns all transfers associated with the seed.

        :param start:
            Starting key index.

        :param stop:
            Stop before this index.

            Note that this parameter behaves like the ``stop`` attribute
            in a :py:class:`slice` object; the stop index is *not*
            included in the result.

            If ``None`` (default), then this method will check every
            address until it finds one without any transfers.

        :param inclusion_states:
            Whether to also fetch the inclusion states of the transfers.

            This requires an additional API call to the node, so it is
            disabled by default.

        :return:
            Dict with the following structure::

                {
                    'bundles': List[Bundle],
                        Matching bundles, sorted by tail transaction
                        timestamp.

                        This value is always a list, even if only one
                        bundle was found.
                }

        References:

        - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#gettransfers
        """
        return extended.GetTransfersCommand(self.adapter)(
            seed=self.seed,
            start=start,
            stop=stop,
            inclusionStates=inclusion_states,
        )

    def prepare_transfer(
            self,
            transfers,  # type: Iterable[ProposedTransaction]
            inputs=None,  # type: Optional[Iterable[Address]]
            change_address=None,  # type: Optional[Address]
            security_level=None,  # type: Optional[int]
    ):
        # type: (...) -> dict
        """
        Prepares transactions to be broadcast to the Tangle, by
        generating the correct bundle, as well as choosing and signing
        the inputs (for value transfers).

        :param transfers:
            Transaction objects to prepare.

        :param inputs:
            List of addresses used to fund the transfer.
            Ignored for zero-value transfers.

            If not provided, addresses will be selected automatically by
            scanning the Tangle for unspent inputs.  Depending on how
            many transfers you've already sent with your seed, this
            process could take awhile.

        :param change_address:
            If inputs are provided, any unspent amount will be sent to
            this address.

            If not specified, a change address will be generated
            automatically.

        :param security_level:
            Number of iterations to use when generating new addresses
            (see :py:meth:`get_new_addresses`).

            This value must be between 1 and 3, inclusive.

            If not set, defaults to
            :py:attr:`AddressGenerator.DEFAULT_SECURITY_LEVEL`.

        :return:
            Dict with the following structure::

                {
                    'trytes': List[TransactionTrytes],
                        Raw trytes for the transactions in the bundle,
                        ready to be provided to :py:meth:`send_trytes`.
                }

        References:

        - https://github.com/iotaledger/wiki/blob/master/api-proposal.md#preparetransfers
        """
        return extended.PrepareTransferCommand(self.adapter)(
            seed=self.seed,
            transfers=transfers,
            inputs=inputs,
            changeAddress=change_address,
            securityLevel=security_level,
        )

    def promote_transaction(
            self,
            transaction,
            depth=3,
            min_weight_magnitude=None,
    ):
        # type: (TransactionHash, int, Optional[int]) -> dict
        """
        Promotes a transaction by adding spam on top of it.

        :param transaction:
            Transaction hash.  Must be a tail transaction.

        :param depth:
            Depth at which to attach the bundle.
            Defaults to 3.

        :param min_weight_magnitude:
            Min weight magnitude, used by the node to calibrate Proof of
            Work.

            If not provided, a default value will be used.

        :return:
            Dict with the following structure::

                {
                    'bundle': Bundle,
                        The newly-published bundle.
                }
        """
        if min_weight_magnitude is None:
            min_weight_magnitude = self.default_min_weight_magnitude

        return extended.PromoteTransactionCommand(self.adapter)(
            transaction=transaction,
            depth=depth,
            minWeightMagnitude=min_weight_magnitude,
        )

    def replay_bundle(
            self,
            transaction,
            depth=3,
            min_weight_magnitude=None,
    ):
        # type: (TransactionHash, int, Optional[int]) -> dict
        """
        Takes a tail transaction hash as input, gets the bundle
        associated with the transaction and then replays the bundle by
        attaching it to the Tangle.

        :param transaction:
            Transaction hash.  Must be a tail.

        :param depth:
            Depth at which to attach the bundle.
            Defaults to 3.

        :param min_weight_magnitude:
            Min weight magnitude, used by the node to calibrate Proof of
            Work.

            If not provided, a default value will be used.

        :return:
            Dict with the following structure::

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
            transaction=transaction,
            depth=depth,
            minWeightMagnitude=min_weight_magnitude,
        )

    def send_transfer(
            self,
            transfers,  # type: Iterable[ProposedTransaction]
            depth=3,  # type: int
            inputs=None,  # type: Optional[Iterable[Address]]
            change_address=None,  # type: Optional[Address]
            min_weight_magnitude=None,  # type: Optional[int]
            security_level=None,  # type: Optional[int]
    ):
        # type: (...) -> dict
        """
        Prepares a set of transfers and creates the bundle, then
        attaches the bundle to the Tangle, and broadcasts and stores the
        transactions.

        :param transfers:
            Transfers to include in the bundle.

        :param depth:
            Depth at which to attach the bundle.
            Defaults to 3.

        :param inputs:
            List of inputs used to fund the transfer.
            Not needed for zero-value transfers.

        :param change_address:
            If inputs are provided, any unspent amount will be sent to
            this address.

            If not specified, a change address will be generated
            automatically.

        :param min_weight_magnitude:
            Min weight magnitude, used by the node to calibrate Proof of
            Work.

            If not provided, a default value will be used.

        :param security_level:
            Number of iterations to use when generating new addresses
            (see :py:meth:`get_new_addresses`).

            This value must be between 1 and 3, inclusive.

            If not set, defaults to
            :py:attr:`AddressGenerator.DEFAULT_SECURITY_LEVEL`.

        :return:
            Dict with the following structure::

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
            seed=self.seed,
            depth=depth,
            transfers=transfers,
            inputs=inputs,
            changeAddress=change_address,
            minWeightMagnitude=min_weight_magnitude,
            securityLevel=security_level,
        )

    def send_trytes(self, trytes, depth=3, min_weight_magnitude=None):
        # type: (Iterable[TransactionTrytes], int, Optional[int]) -> dict
        """
        Attaches transaction trytes to the Tangle, then broadcasts and
        stores them.

        :param trytes:
            Transaction encoded as a tryte sequence.

        :param depth:
            Depth at which to attach the bundle.
            Defaults to 3.

        :param min_weight_magnitude:
            Min weight magnitude, used by the node to calibrate Proof of
            Work.

            If not provided, a default value will be used.

        :return:
            Dict with the following structure::

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
            trytes=trytes,
            depth=depth,
            minWeightMagnitude=min_weight_magnitude,
        )

    def is_reattachable(self, addresses):
        # type: (Iterable[Address]) -> dict
        """
        This API function helps you to determine whether you should
        replay a transaction or make a new one (either with the same
        input, or a different one).

        This method takes one or more input addresses (i.e. from spent
        transactions) as input and then checks whether any transactions
        with a value transferred are confirmed.

        If yes, it means that this input address has already been
        successfully used in a different transaction, and as such you
        should no longer replay the transaction.

        :param addresses:
            List of addresses.

        :return:
            Dict with the following structure::

                {
                  'reattachable': List[bool],
                    Always a list, even if only one address was queried.
                }
        """
        return extended.IsReattachableCommand(self.adapter)(
            addresses=addresses
        )
