from typing import Iterable, Iterator, List, Optional, Sequence

from iota.crypto import HASH_LENGTH
from iota.crypto.kerl import Kerl
from iota.crypto.signing import KeyGenerator, normalize
from iota.crypto.types import PrivateKey
from iota.exceptions import with_context
from iota.transaction.base import Bundle, Transaction
from iota.transaction.types import BundleHash, Fragment, Nonce, TransactionHash
from iota.transaction.utils import get_current_timestamp
from iota.trits import add_trits
from iota.types import Address, Tag, TryteString

__all__ = [
    'ProposedBundle',
    'ProposedTransaction',
    'Transfer',
]


class ProposedTransaction(Transaction):
    """
    A transaction that has not yet been attached to the Tangle.

    Proposed transactions are created locally. Note that for creation, only a
    small subset of the :py:class:`Transaction` attributes is needed.

    Provide to :py:meth:`Iota.send_transfer` to attach to tangle and
    publish/store.

    .. note::
        In order to follow naming convention of other libs, you may use the
        name ``Transfer`` interchangeably with ``ProposedTransaction``.
        See https://github.com/iotaledger/iota.py/issues/72 for more info.

    :param Address address:
        Address associated with the transaction.

    :param int value:
        Transaction value.

    :param Optional[Tag] tag:
        Optional classification tag applied to this transaction.

    :param Optional[TryteString] message:
        Message to be included in
        :py:attr:`transaction.Transaction.signature_or_message_fragment` field
        of the transaction. Should not be longer than
        :py:attr:`transaction.Fragment.LEN`.

    :param Optional[int] timestamp:
        Timestamp of transaction creation. If not supplied, the library will
        generate it.

    :return:
        :py:class:`iota.ProposedTransaction` object.

    Example usage::

        txn=\\
            ProposedTransaction(
                address =
                    Address(
                        b'TESTVALUE9DONTUSEINPRODUCTION99999XE9IVG'
                        b'EFNDOCQCMERGUATCIEGGOHPHGFIAQEZGNHQ9W99CH'
                    ),
                message = TryteString.from_unicode('thx fur cheezburgers'),
                tag     = Tag(b'KITTENS'),
                value   = 42,
            )
    """

    def __init__(
            self,
            address: Address,
            value: int,
            tag: Optional[Tag] = None,
            message: Optional[TryteString] = None,
            timestamp: Optional[int] = None,
    ) -> None:
        if not timestamp:
            timestamp = get_current_timestamp()

        super(ProposedTransaction, self).__init__(
            address=address,
            tag=Tag(b'') if tag is None else Tag(tag),
            timestamp=timestamp,
            value=value,

            # These values will be populated when the bundle is
            # finalized.
            bundle_hash=None,
            current_index=None,
            hash_=None,
            last_index=None,
            signature_message_fragment=None,
            attachment_timestamp=0,
            attachment_timestamp_lower_bound=0,
            attachment_timestamp_upper_bound=0,

            # These values start out empty; they will be populated when
            # the node does PoW.
            branch_transaction_hash=TransactionHash(b''),
            nonce=Nonce(b''),
            trunk_transaction_hash=TransactionHash(b''),
        )

        self.message = TryteString(b'') if message is None else message

    def as_tryte_string(self) -> TryteString:
        """
        Returns a TryteString representation of the transaction.

        :return:
            :py:class:`TryteString` object.

        :raises RuntimeError:
            if the transaction doesn't have a bundle hash field, meaning that
            the bundle containing the transaction hasn't been finalized yet.
        """
        if not self.bundle_hash:
            raise with_context(
                exc=RuntimeError(
                    'Cannot get TryteString representation of {cls} instance '
                    'without a bundle hash; call ``bundle.finalize()`` first '
                    '(``exc.context`` has more info).'.format(
                        cls=type(self).__name__,
                    ),
                ),

                context={
                    'transaction': self,
                },
            )

        return super(ProposedTransaction, self).as_tryte_string()

    def increment_legacy_tag(self) -> None:
        """
        Increments the transaction's legacy tag, used to fix insecure
        bundle hashes when finalizing a bundle.

        References:

        - https://github.com/iotaledger/iota.py/issues/84
        """
        self._legacy_tag = (
            Tag.from_trits(add_trits(self.legacy_tag.as_trits(), [1]))
        )


Transfer = ProposedTransaction
"""
Follow naming convention of other libs.
https://github.com/iotaledger/iota.py/issues/72
"""


class ProposedBundle(Bundle, Sequence[ProposedTransaction]):
    """
    A collection of proposed transactions, to be treated as an atomic
    unit when attached to the Tangle.

    :param  Optional[Iterable[ProposedTransaction]] transactions:
        Proposed transactions that should be put into the proposed bundle.

    :param Optional[Iterable[Address]] inputs:
        Addresses that hold iotas to fund outgoing transactions in the bundle.
        If provided, the library will create and sign withdrawing transactions
        from these addresses.

        See :py:meth:`Iota.get_inputs` for more info.

    :param Optional[Address] change_address:
        Due to the signatures scheme of IOTA, you can only spend once from an
        address. Therefore the library will always deduct the full available
        amount from an input address. The unused tokens will be sent to
        ``change_address`` if provided, or to a newly-generated and unused
        address if not.

    :return: :py:class:`ProposedBundle`
    """

    def __init__(
            self,
            transactions: Optional[Iterable[ProposedTransaction]] = None,
            inputs: Optional[Iterable[Address]] = None,
            change_address: Optional[Address] = None,
    ) -> None:
        super(ProposedBundle, self).__init__()

        self._transactions: List[ProposedTransaction] = []

        if transactions:
            for t in transactions:
                self.add_transaction(t)

        if inputs:
            self.add_inputs(inputs)

        self.change_address = change_address

    def __bool__(self) -> bool:
        """
        Returns whether this bundle has any transactions.

        :return: ``bool``
        """
        return bool(self._transactions)

    def __contains__(self, transaction: ProposedTransaction) -> bool:
        return transaction in self._transactions

    def __getitem__(self, index: int) -> ProposedTransaction:
        """
        Returns the transaction at the specified index.
        """
        return self._transactions[index]

    def __iter__(self) -> Iterator[ProposedTransaction]:
        """
        Iterates over transactions in the bundle.
        """
        return iter(self._transactions)

    def __len__(self) -> int:
        """
        Returns te number of transactions in the bundle.
        """
        return len(self._transactions)

    @property
    def balance(self) -> int:
        """
        Returns the bundle balance.
        In order for a bundle to be valid, its balance must be 0:

        - A positive balance means that there aren't enough inputs to
          cover the spent amount; add more inputs using
          :py:meth:`add_inputs`.

        - A negative balance means that there are unspent inputs; use
          :py:meth:`send_unspent_inputs_to` to send the unspent inputs
          to a "change" address.

        :return: ``bool``
        """
        return sum(t.value for t in self._transactions)

    @property
    def tag(self) -> Tag:
        """
        Determines the most relevant tag for the bundle.

        :return: :py:class:`transaction.Tag`
        """
        for txn in reversed(self):  # type: ProposedTransaction
            if txn.tag:
                return txn.tag

        return Tag(b'')

    def as_json_compatible(self) -> List[dict]:
        """
        Returns a JSON-compatible representation of the object.

        :return:
            ``List[dict]``. The ``dict`` list elements contain individual
            transactions as in :py:meth:`ProposedTransaction.as_json_compatible`.

        References:

        - :py:class:`iota.json.JsonEncoder`.
        """
        return [txn.as_json_compatible() for txn in self]

    def add_transaction(self, transaction: ProposedTransaction) -> None:
        """
        Adds a transaction to the bundle.

        If the transaction message is too long, it will be split
        automatically into multiple transactions.

        :param ProposedTransaction transaction:
            The transaction to be added.

        :raises RuntimeError: if bundle is already finalized
        :raises ValueError:
            if trying to add a spending transaction. Use :py:meth:`add_inputs`
            instead.
        """
        if self.hash:
            raise RuntimeError('Bundle is already finalized.')

        if transaction.value < 0:
            raise ValueError('Use ``add_inputs`` to add inputs to the bundle.')

        self._transactions.append(ProposedTransaction(
            address=transaction.address,
            value=transaction.value,
            tag=transaction.tag,
            message=transaction.message[:Fragment.LEN],
            timestamp=transaction.timestamp,
        ))

        # If the message is too long to fit in a single transactions,
        # it must be split up into multiple transactions so that it will
        # fit.
        fragment = transaction.message[Fragment.LEN:]
        while fragment:
            self._transactions.append(ProposedTransaction(
                address=transaction.address,
                value=0,
                tag=transaction.tag,
                message=fragment[:Fragment.LEN],
                timestamp=transaction.timestamp,
            ))

            fragment = fragment[Fragment.LEN:]

    def add_inputs(self, inputs: Iterable[Address]) -> None:
        """
        Specifies inputs that can be used to fund transactions that spend iotas.

        The :py:class:`ProposedBundle` will use these to create the necessary
        input transactions.

        Note that each input may require multiple transactions, in order
        to hold the entire signature.

        :param Iterable[Address] inputs:
            Addresses to use as the inputs for this bundle.

            .. important::
                Must have ``balance`` and ``key_index`` attributes!
                Use :py:meth:`Iota.get_inputs` to prepare inputs.

        :raises RuntimeError: if bundle is already finalized.
        :raises ValueError:
            - if input address has no ``balance``.
            - if input address has no ``key_index``.

        """
        if self.hash:
            raise RuntimeError('Bundle is already finalized.')

        for addy in inputs:
            if addy.balance is None:
                raise with_context(
                    exc=ValueError(
                        'Address {address} has null ``balance`` '
                        '(``exc.context`` has more info).'.format(
                            address=addy,
                        ),
                    ),

                    context={
                        'address': addy,
                    },
                )

            if addy.key_index is None:
                raise with_context(
                    exc=ValueError(
                        'Address {address} has null ``key_index`` '
                        '(``exc.context`` has more info).'.format(
                            address=addy,
                        ),
                    ),

                    context={
                        'address': addy,
                    },
                )

            self._create_input_transactions(addy)

    def send_unspent_inputs_to(self, address: Address) -> None:
        """
        Specifies the address that will receive unspent iotas.

        The :py:class:`ProposedBundle` will use this to create the necessary
        change transaction, if necessary.

        If the bundle has no unspent inputs, this method does nothing.

        :param Address address:
            Address to send unspent inputs to.

        :raises RuntimeError: if bundle is already finalized.
        """
        if self.hash:
            raise RuntimeError('Bundle is already finalized.')

        self.change_address = address

    def finalize(self) -> None:
        """
        Finalizes the bundle, preparing it to be attached to the Tangle.

        This operation includes checking if the bundle has zero balance,
        generating the bundle hash and updating the transactions with it,
        furthermore to initialize signature/message fragment fields.

        Once this method is invoked, no new transactions may be added to the
        bundle.

        :raises RuntimeError: if bundle is already finalized.
        :raises ValueError:
            - if bundle has no transactions.
            - if bundle has unspent inputs (there is no ``change_address``
              attribute specified.)
            - if inputs are insufficient to cover bundle spend.
        """
        if self.hash:
            raise RuntimeError('Bundle is already finalized.')

        if not self:
            raise ValueError('Bundle has no transactions.')

        # Quick validation.
        balance = self.balance

        if balance < 0:
            if self.change_address:
                self.add_transaction(ProposedTransaction(
                    address=self.change_address,
                    value=-balance,
                    tag=self.tag,
                ))
            else:
                raise ValueError(
                    'Bundle has unspent inputs (balance: {balance}); '
                    'use ``send_unspent_inputs_to`` to create '
                    'change transaction.'.format(
                        balance=balance,
                    ),
                )
        elif balance > 0:
            raise ValueError(
                'Inputs are insufficient to cover bundle spend '
                '(balance: {balance}).'.format(
                    balance=balance,
                ),
            )

        # Generate bundle hash.
        while True:
            sponge = Kerl()
            last_index = len(self) - 1

            for i, txn in enumerate(self):
                txn.current_index = i
                txn.last_index = last_index

                sponge.absorb(txn.get_bundle_essence_trytes().as_trits())

            bundle_hash_trits = [0] * HASH_LENGTH
            sponge.squeeze(bundle_hash_trits)

            bundle_hash = BundleHash.from_trits(bundle_hash_trits)

            # Check that we generated a secure bundle hash.
            # https://github.com/iotaledger/iota.py/issues/84
            if any(13 in part for part in normalize(bundle_hash)):
                # Increment the legacy tag and try again.
                tail_transaction: ProposedTransaction = (
                    self.tail_transaction
                )
                tail_transaction.increment_legacy_tag()
            else:
                break

        # Copy bundle hash to individual transactions.
        for txn in self:
            txn.bundle_hash = bundle_hash

            # Initialize signature/message fragment.
            txn.signature_message_fragment = Fragment(txn.message or b'')

    def sign_inputs(self, key_generator: KeyGenerator) -> None:
        """
        Sign inputs in a finalized bundle.

        Generates the necessary cryptographic signatures to authorize spending
        the inputs.

        .. note::
            You do not need to invoke this method if the bundle does
            not contain any transactions that spend iotas.

        :param KeyGenerator key_generator:
            Generator to create private keys for signing.

        :raises RuntimeError: if bundle is not yet finalized.
        :raises ValueError:
            - if the input transaction specifies an address that doesn't have
              ``key_index`` attribute defined.
            - if the input transaction specifies an address that doesn't have
              ``security_level`` attribute defined.
        """
        if not self.hash:
            raise RuntimeError('Cannot sign inputs until bundle is finalized.')

        # Use a counter for the loop so that we can skip ahead as we go.
        i = 0
        while i < len(self):
            txn = self[i]

            if txn.value < 0:
                # In order to sign the input, we need to know the index
                # of the private key used to generate it.
                if txn.address.key_index is None:
                    raise with_context(
                        exc=ValueError(
                            'Unable to sign input {input}; '
                            '``key_index`` is None '
                            '(``exc.context`` has more info).'.format(
                                input=txn.address,
                            ),
                        ),

                        context={
                            'transaction': txn,
                        },
                    )

                if txn.address.security_level is None:
                    raise with_context(
                        exc=ValueError(
                            'Unable to sign input {input}; '
                            '``security_level`` is None '
                            '(``exc.context`` has more info).'.format(
                                input=txn.address,
                            ),
                        ),

                        context={
                            'transaction': txn,
                        },
                    )

                self.sign_input_at(i, key_generator.get_key_for(txn.address))

                i += txn.address.security_level
            else:
                # No signature needed (nor even possible, in some
                # cases); skip this transaction.
                i += 1

    def sign_input_at(
            self,
            start_index: int,
            private_key: PrivateKey
    ) -> None:
        """
        Signs the input at the specified index.

        :param int start_index:
            The index of the first input transaction.

            If necessary, the resulting signature will be split across
            multiple transactions automatically (i.e., if an input has
            ``security_level=2``, you still only need to call
            :py:meth:`sign_input_at` once).

        :param PrivateKey private_key:
            The private key that will be used to generate the signature.

            .. important::
                Be sure that the private key was generated using the
                correct seed, or the resulting signature will be
                invalid!

        :raises RuntimeError: if bundle is not yet finalized.
        """
        if not self.hash:
            raise RuntimeError('Cannot sign inputs until bundle is finalized.')

        private_key.sign_input_transactions(self, start_index)

    def _create_input_transactions(self, addy: Address) -> None:
        """
        Creates transactions for the specified input address.

        :param Address addy:
            Input address.
        """
        self._transactions.append(ProposedTransaction(
            address=addy,
            tag=self.tag,

            # Spend the entire address balance; if necessary, we will
            # add a change transaction to the bundle.
            value=-addy.balance,
        ))

        # Signatures require additional transactions to store, due to
        # transaction length limit.
        # Subtract 1 to account for the transaction we just added.
        for _ in range(addy.security_level - 1):
            self._transactions.append(ProposedTransaction(
                address=addy,
                tag=self.tag,

                # Note zero value; this is a meta transaction.
                value=0,
            ))

    def add_signature_or_message(
            self,
            fragments: Iterable[Fragment],
            start_index: Optional[int] = 0
    ) -> None:
        """
        Adds signature/message fragments to transactions in the bundle
        starting at start_index. If a transaction already has a fragment,
        it will be overwritten.

        :param Iterable[Fragment] fragments:
            List of fragments to add.
            Use [Fragment(...),Fragment(...),...] to create this argument.
            Fragment() accepts any TryteString compatible type, or types that
            can be converted to TryteStrings (bytearray, unicode string, etc.).
            If the payload is less than :py:attr:`FRAGMENT_LENGTH`, it will pad
            it with 9s.

        :param int start_index:
            Index of transaction in bundle from where addition shoudl start.

        :raise RuntimeError: if bundle is already finalized.
        :raise ValueError:
            - if empty list is provided for ``fragments``
            - if wrong ``start_index`` is provided.
            - if ``fragments`` is too long and does't fit into the bundle.
        :raise TypeError:
            - if ``fragments`` is not an ``Iterable``
            - if ``fragments`` contains other types than :py:class:`Fragment`.
        """
        if self.hash:
            raise RuntimeError('Bundle is already finalized.')

        if not isinstance(fragments, Iterable):
            raise TypeError('Expected iterable for `fragments`, but got {type} instead.'.format(
                type=fragments.__class__.__name__
            ))

        if not all(isinstance(x, Fragment) for x in fragments):
            raise TypeError(
                'Expected `fragments` to contain only Fragment objects, but got {types} instead.'.format(
                    types=[x.__class__.__name__ for x in fragments],
                )
            )

        if not isinstance(start_index, int):
            raise TypeError('Expected int for `start_index`, but got {type} instead.'.format(
                type=start_index.__class__.__name__,
            ))

        length = len(fragments)

        if not length:
            raise ValueError('Empty list provided for `fragments`.')

        if start_index < 0 or start_index > len(self) - 1:
            raise ValueError('Wrong start_index provided: {index}'.format(
                index=start_index))

        if start_index + length > len(self):
            raise ValueError('Can\'t add {length} fragments starting from index '
                             '{start}: There are only {count} transactions in '
                             'the bundle.'.format(
                                 length=length,
                                 start=start_index,
                                 count=len(self),
                             ))

        for i in range(length):
            # Bundle is not finalized yet, therefore we should fill the message
            # field. This will be put into signature_message_fragment upon
            # finalization.
            self._transactions[start_index + i].message = fragments[i]
