Core API
========

The Core API includes all of the core API calls that are made
available by the current `IOTA Reference
Implementation <https://github.com/iotaledger/iri>`__.

These methods are "low level" and generally do not need to be called
directly.

For the full documentation of all the Core API calls, please refer
to the `official documentation <https://iota.readme.io/>`__.

Extended API
============

The Extended API includes a number of "high level" commands to perform
tasks such as sending and receiving transfers.

``broadcast_and_store``
-----------------------

Broadcasts and stores a set of transaction trytes.

Parameters
~~~~~~~~~~

-  ``trytes: Iterable[TransactionTrytes]``: Transaction trytes.

Return
~~~~~~

This method returns a ``dict`` with the following items:

-  ``trytes: List[TransactionTrytes]``: Transaction trytes that were
   broadcast/stored. Should be the same as the value of the ``trytes``
   parameter.

``get_account_data``
--------------------

More comprehensive version of ``get_transfers`` that returns addresses
and account balance in addition to bundles.

This function is useful in getting all the relevant information of your
account.

Parameters
~~~~~~~~~~

-  ``start: int``: Starting key index.

-  ``stop: Optional[int]``: Stop before this index. Note that this
   parameter behaves like the ``stop`` attribute in a ``slice`` object;
   the stop index is *not* included in the result.

-  If ``None`` (default), then this method will check every address
   until it finds one without any transfers.

-  ``inclusion_states: bool`` Whether to also fetch the inclusion states
   of the transfers. This requires an additional API call to the node,
   so it is disabled by default.

Return
~~~~~~

This method returns a dict with the following items:

-  ``addresses: List[Address]``: List of generated addresses. Note that
   this list may include unused addresses.

-  ``balance: int``: Total account balance. Might be 0.

-  ``bundles: List[Bundles]``: List of bundles with transactions to/from
   this account.

``get_bundles``
---------------

Given a ``TransactionHash``, returns the bundle(s) associated with it.

Parameters
~~~~~~~~~~

-  ``transaction: TransactionHash``: Hash of a tail transaction.

Return
~~~~~~

This method returns a ``dict`` with the following items:

-  ``bundles: List[Bundle]``: List of matching bundles. Note that this
   value is always a list, even if only one bundle was found.

``get_inputs``
--------------

Gets all possible inputs of a seed and returns them with the total
balance.

This is either done deterministically (by generating all addresses until
``find_transactions`` returns an empty result), or by providing a key
range to search.

Parameters
~~~~~~~~~~

-  ``start: int``: Starting key index. Defaults to 0.
-  ``stop: Optional[int]``: Stop before this index.
-  Note that this parameter behaves like the ``stop`` attribute in a
   ``slice`` object; the stop index is *not* included in the result.
-  If ``None`` (default), then this method will not stop until it finds
   an unused address.
-  ``threshold: Optional[int]``: If set, determines the minimum
   threshold for a successful result:
-  As soon as this threshold is reached, iteration will stop.
-  If the command runs out of addresses before the threshold is reached,
   an exception is raised.
-  If ``threshold`` is 0, the first address in the key range with a
   non-zero balance will be returned (if it exists).
-  If ``threshold`` is ``None`` (default), this method will return
   **all** inputs in the specified key range.

Note that this method does not attempt to "optimize" the result (e.g.,
smallest number of inputs, get as close to ``threshold`` as possible,
etc.); it simply accumulates inputs in order until the threshold is met.

Return
~~~~~~

This method returns a ``dict`` with the following items:

-  ``inputs: List[Address]``: Addresses with nonzero balances that can
   be used as inputs.
-  ``totalBalance: int``: Aggregate balance of all inputs found.

``get_latest_inclusion``
------------------------

Fetches the inclusion state for the specified transaction hashes, as of
the latest milestone that the node has processed.

Parameters
~~~~~~~~~~

-  ``hashes: Iterable[TransactionHash]``: Iterable of transaction
   hashes.

Return
~~~~~~

This method returns a ``dict`` with the following items:

-  ``<TransactionHash>: bool``: Inclusion state for a single
   transaction.

There will be one item per transaction hash in the ``hashes`` parameter.

``get_new_addresses``
---------------------

Generates one or more new addresses from the seed.

Parameters
~~~~~~~~~~

-  ``index: int``: Specify the index of the new address (must be >= 1).
-  ``count: Optional[int]``: Number of addresses to generate (must be >=
   1).
-  If ``None``, this method will scan the Tangle to find the next
   available unused address and return that.
-  ``security_level: int``: Number of iterations to use when generating
   new addresses. Lower values generate addresses faster, higher values
   result in more secure signatures in transactions.

Return
~~~~~~

This method returns a ``dict`` with the following items:

-  ``addresses: List[Address]``: The generated address(es). Note that
   this value is always a list, even if only one address was generated.

``get_transfers``
-----------------

Returns all transfers associated with the seed.

Parameters
~~~~~~~~~~

-  ``start: int``: Starting key index.
-  ``stop: Optional[int]``: Stop before this index.
-  Note that this parameter behaves like the ``stop`` attribute in a
   ``slice`` object; the stop index is *not* included in the result.
-  If ``None`` (default), then this method will check every address
   until it finds one without any transfers.

Return
~~~~~~

This method returns a ``dict`` with the following items:

-  ``bundles: List[Bundle]``: Matching bundles, sorted by tail
   transaction timestamp.

``is_reattachable``
-------------------

This API function helps you to determine whether you should replay a
transaction or make a new one (either with the same input, or a
different one).

This method takes one or more input addresses (i.e. from spent
transactions) as input and then checks whether any transactions with a
value transferred are confirmed.

If yes, it means that this input address has already been successfully
used in a different transaction, and as such you should no longer replay
the transaction.

Parameters
~~~~~~~~~~

- ``address: Iterable[Address]``: List of addresses.

Return
~~~~~~

This method returns a ``dict`` with the following items:

- ``reattachable: List[Bool]``: Always a list, even if only one address
  was queried.

``prepare_transfer``
--------------------

Prepares transactions to be broadcast to the Tangle, by generating the
correct bundle, as well as choosing and signing the inputs (for value
transfers).

Parameters
~~~~~~~~~~

-  ``transfers: Iterable[ProposedTransaction]``: Transaction objects to
   prepare.
-  ``inputs: Optional[Iterable[Address]]``: List of addresses used to
   fund the transfer. Ignored for zero-value transfers.
-  If not provided, addresses will be selected automatically by scanning
   the Tangle for unspent inputs.
-  ``change_address: Optional[Address]``: If inputs are provided, any
   unspent amount will be sent to this address.
-  If not specified, a change address will be generated automatically.

Return
~~~~~~

This method returns a ``dict`` with the following items:

-  ``trytes: List[TransactionTrytes]``: Raw trytes for the transactions
   in the bundle, ready to be provided to ``send_trytes``.

``promote_transaction``
-----------------------

Promotes a transaction by adding spam on top of it.

-  ``transaction: TransactionHash``: Transaction hash. Must be a tail.
-  ``depth: int``: Depth at which to attach the bundle.
-  ``min_weight_magnitude: Optional[int]``: Min weight magnitude, used
   by the node to calibrate Proof of Work.
-  If not provided, a default value will be used.

Return
~~~~~~

This method returns a ``dict`` with the following items:

-  ``bundle: Bundle``: The newly-published bundle.

``replay_bundle``
-----------------

Takes a tail transaction hash as input, gets the bundle associated with
the transaction and then replays the bundle by attaching it to the
Tangle.

Parameters
~~~~~~~~~~

-  ``transaction: TransactionHash``: Transaction hash. Must be a tail.
-  ``depth: int``: Depth at which to attach the bundle.
-  ``min_weight_magnitude: Optional[int]``: Min weight magnitude, used
   by the node to calibrate Proof of Work.
-  If not provided, a default value will be used.

Return
~~~~~~

This method returns a ``dict`` with the following items:

-  ``trytes: List[TransactionTrytes]``: Raw trytes that were published
   to the Tangle.

``send_transfer``
-----------------

Prepares a set of transfers and creates the bundle, then attaches the
bundle to the Tangle, and broadcasts and stores the transactions.

Parameters
~~~~~~~~~~

-  ``depth: int``: Depth at which to attach the bundle.
-  ``transfers: Iterable[ProposedTransaction]``: Transaction objects to
   prepare.
-  ``inputs: Optional[Iterable[Address]]``: List of addresses used to
   fund the transfer. Ignored for zero-value transfers.
-  If not provided, addresses will be selected automatically by scanning
   the Tangle for unspent inputs.
-  ``change_address: Optional[Address]``: If inputs are provided, any
   unspent amount will be sent to this address.
-  If not specified, a change address will be generated automatically.
-  ``min_weight_magnitude: Optional[int]``: Min weight magnitude, used
   by the node to calibrate Proof of Work.
-  If not provided, a default value will be used.

Return
~~~~~~

This method returns a ``dict`` with the following items:

-  ``bundle: Bundle``: The newly-published bundle.

``send_trytes``
---------------

Attaches transaction trytes to the Tangle, then broadcasts and stores
them.

Parameters
~~~~~~~~~~

-  ``trytes: Iterable[TransactionTrytes]``: Transaction trytes to
   publish.
-  ``depth: int``: Depth at which to attach the bundle.
-  ``min_weight_magnitude: Optional[int]``: Min weight magnitude, used
   by the node to calibrate Proof of Work.
-  If not provided, a default value will be used.

Return
~~~~~~

This method returns a ``dict`` with the following items:

-  ``trytes: List[TransactionTrytes]``: Raw trytes that were published
   to the Tangle.
