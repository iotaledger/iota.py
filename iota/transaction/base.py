from operator import attrgetter
from typing import Iterable, Iterator, List, MutableSequence, \
    Optional, Sequence, TypeVar, Type

from iota.codecs import TrytesDecodeError
from iota.crypto import Curl, HASH_LENGTH
from iota.json import JsonSerializable
from iota.transaction.types import BundleHash, Fragment, Nonce, \
    TransactionHash, TransactionTrytes
from iota.trits import int_from_trits, trits_from_int
from iota.types import Address, Tag, TryteString, TrytesCompatible

__all__ = [
    'Bundle',
    'Transaction',
]

T = TypeVar('T', bound='Transaction')


class Transaction(JsonSerializable):
    """
    A transaction that has been attached to the Tangle.

    :param Optional[TransactionHash] hash_:
        Transaction ID

    :param Optional[Fragment] signature_message_fragment:
        Signature or message fragment.

    :param Address address:
        The address associated with this transaction.

    :param int value:
        Value of the transaction in iotas. Can be negative as well
        (spending from address).

    :param int timestamp:
        Unix timestamp in seconds.

    :param Optional[int] current_index:
        Index of the transaction within the bundle.

    :param Optional[int] last_index:
        Index of head transaction in the bundle.

    :param Optional[BundleHash] bundle_hash:
        Bundle hash of the bundle containing the transaction.

    :param Optional[TransactionHash] trunk_transaction_hash:
        Hash of trunk transaction.

    :param Optional[TransactionHash] branch_transaction_hash:
        Hash of branch transaction.

    :param Optional[Tag] tag:
        Optional classification tag applied to this transaction.

    :param Optional[int] attachment_timestamp:
        Unix timestamp in milliseconds, decribes when the proof-of-work for this
        transaction was done.

    :param Optional[int] attachment_timestamp_lower_bound:
        Unix timestamp in milliseconds, lower bound of attachment.

    :param Optional[int] attachment_timestamp_upper_bound:
        Unix timestamp in milliseconds, upper bound of attachment.

    :param Optional[Nonce] nonce:
        Unique value used to increase security of the transaction hash. Result of
        the proof-of-work aglorithm.

    :param Optional[Tag] legacy_tag:
        Optional classification legacy_tag applied to this transaction.

    :return:
        :py:class:`Transaction` object.
    """

    @classmethod
    def from_tryte_string(
            cls: Type[T],
            trytes: TrytesCompatible,
            hash_: Optional[TransactionHash] = None
    ) -> T:
        """
        Creates a Transaction object from a sequence of trytes.

        :param TrytesCompatible trytes:
            Raw trytes.  Should be exactly 2673 trytes long.

        :param Optional[TransactionHash] hash_:
            The transaction hash, if available.

            If not provided, it will be computed from the transaction
            trytes.

        :return:
            :py:class:`Transaction` object.

        Example usage::

            from iota import Transaction

            txn =\\
              Transaction.from_tryte_string(
                b'GYPRVHBEZOOFXSHQBLCYW9ICTCISLHDBNMMVYD9JJHQMPQCTIQAQTJNNNJ9IDXLRCC'
                b'OYOXYPCLR9PBEY9ORZIEPPDNTI9CQWYZUOTAVBXPSBOFEQAPFLWXSWUIUSJMSJIIIZ'
                b'WIKIRH9GCOEVZFKNXEVCUCIIWZQCQEUVRZOCMEL9AMGXJNMLJCIA9UWGRPPHCEOPTS'
                b'VPKPPPCMQXYBHMSODTWUOABPKWFFFQJHCBVYXLHEWPD9YUDFTGNCYAKQKVEZYRBQRB'
                b'XIAUX9SVEDUKGMTWQIYXRGSWYRK9SRONVGTW9YGHSZRIXWGPCCUCDRMAXBPDFVHSRY'
                b'WHGB9DQSQFQKSNICGPIPTRZINYRXQAFSWSEWIFRMSBMGTNYPRWFSOIIWWT9IDSELM9'
                b'JUOOWFNCCSHUSMGNROBFJX9JQ9XT9PKEGQYQAWAFPRVRRVQPUQBHLSNTEFCDKBWRCD'
                b'X9EYOBB9KPMTLNNQLADBDLZPRVBCKVCYQEOLARJYAGTBFR9QLPKZBOYWZQOVKCVYRG'
                b'YI9ZEFIQRKYXLJBZJDBJDJVQZCGYQMROVHNDBLGNLQODPUXFNTADDVYNZJUVPGB9LV'
                b'PJIYLAPBOEHPMRWUIAJXVQOEM9ROEYUOTNLXVVQEYRQWDTQGDLEYFIYNDPRAIXOZEB'
                b'CS9P99AZTQQLKEILEVXMSHBIDHLXKUOMMNFKPYHONKEYDCHMUNTTNRYVMMEYHPGASP'
                b'ZXASKRUPWQSHDMU9VPS99ZZ9SJJYFUJFFMFORBYDILBXCAVJDPDFHTTTIYOVGLRDYR'
                b'TKHXJORJVYRPTDH9ZCPZ9ZADXZFRSFPIQKWLBRNTWJHXTOAUOL9FVGTUMMPYGYICJD'
                b'XMOESEVDJWLMCVTJLPIEKBE9JTHDQWV9MRMEWFLPWGJFLUXI9BXPSVWCMUWLZSEWHB'
                b'DZKXOLYNOZAPOYLQVZAQMOHGTTQEUAOVKVRRGAHNGPUEKHFVPVCOYSJAWHZU9DRROH'
                b'BETBAFTATVAUGOEGCAYUXACLSSHHVYDHMDGJP9AUCLWLNTFEVGQGHQXSKEMVOVSKQE'
                b'EWHWZUDTYOBGCURRZSJZLFVQQAAYQO9TRLFFN9HTDQXBSPPJYXMNGLLBHOMNVXNOWE'
                b'IDMJVCLLDFHBDONQJCJVLBLCSMDOUQCKKCQJMGTSTHBXPXAMLMSXRIPUBMBAWBFNLH'
                b'LUJTRJLDERLZFUBUSMF999XNHLEEXEENQJNOFFPNPQ9PQICHSATPLZVMVIWLRTKYPI'
                b'XNFGYWOJSQDAXGFHKZPFLPXQEHCYEAGTIWIJEZTAVLNUMAFWGGLXMBNUQTOFCNLJTC'
                b'DMWVVZGVBSEBCPFSM99FLOIDTCLUGPSEDLOKZUAEVBLWNMODGZBWOVQT9DPFOTSKRA'
                b'BQAVOQ9RXWBMAKFYNDCZOJGTCIDMQSQQSODKDXTPFLNOKSIZEOY9HFUTLQRXQMEPGO'
                b'XQGLLPNSXAUCYPGZMNWMQWSWCKAQYKXJTWINSGPPZG9HLDLEAWUWEVCTVRCBDFOXKU'
                b'ROXH9HXXAXVPEJFRSLOGRVGYZASTEBAQNXJJROCYRTDPYFUIQJVDHAKEG9YACV9HCP'
                b'JUEUKOYFNWDXCCJBIFQKYOXGRDHVTHEQUMHO999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999RKWEEVD99A99999999A99999999NFDPEEZCWVYLKZGSLCQNOFUSENI'
                b'XRHWWTZFBXMPSQHEDFWZULBZFEOMNLRNIDQKDNNIELAOXOVMYEI9PGTKORV9IKTJZQ'
                b'UBQAWTKBKZ9NEZHBFIMCLV9TTNJNQZUIJDFPTTCTKBJRHAITVSKUCUEMD9M9SQJ999'
                b'999TKORV9IKTJZQUBQAWTKBKZ9NEZHBFIMCLV9TTNJNQZUIJDFPTTCTKBJRHAITVSK'
                b'UCUEMD9M9SQJ999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999'
              )

        """
        tryte_string = TransactionTrytes(trytes)

        if not hash_:
            hash_trits: MutableSequence[int] = [0] * HASH_LENGTH

            sponge = Curl()
            sponge.absorb(tryte_string.as_trits())
            sponge.squeeze(hash_trits)

            hash_ = TransactionHash.from_trits(hash_trits)

        return cls(
                hash_=hash_,
                signature_message_fragment=Fragment(tryte_string[0:2187]),
                address=Address(tryte_string[2187:2268]),
                value=int_from_trits(tryte_string[2268:2295].as_trits()),
                legacy_tag=Tag(tryte_string[2295:2322]),
                timestamp=int_from_trits(tryte_string[2322:2331].as_trits()),
                current_index=int_from_trits(tryte_string[2331:2340].as_trits()),
                last_index=int_from_trits(tryte_string[2340:2349].as_trits()),
                bundle_hash=BundleHash(tryte_string[2349:2430]),
                trunk_transaction_hash=TransactionHash(tryte_string[2430:2511]),
                branch_transaction_hash=TransactionHash(tryte_string[2511:2592]),
                tag=Tag(tryte_string[2592:2619]),

                attachment_timestamp=int_from_trits(
                        tryte_string[2619:2628].as_trits()),

                attachment_timestamp_lower_bound=int_from_trits(
                        tryte_string[2628:2637].as_trits()),

                attachment_timestamp_upper_bound=int_from_trits(
                        tryte_string[2637:2646].as_trits()),

                nonce=Nonce(tryte_string[2646:2673]),
        )

    def __init__(
            self,
            hash_: Optional[TransactionHash],
            signature_message_fragment: Optional[Fragment],
            address: Address,
            value: int,
            timestamp: int,
            current_index: Optional[int],
            last_index: Optional[int],
            bundle_hash: Optional[BundleHash],
            trunk_transaction_hash: Optional[TransactionHash],
            branch_transaction_hash: Optional[TransactionHash],
            tag: Optional[Tag],
            attachment_timestamp: Optional[int],
            attachment_timestamp_lower_bound: Optional[int],
            attachment_timestamp_upper_bound: Optional[int],
            nonce: Optional[Nonce],
            legacy_tag: Optional[Tag] = None
    ) -> None:
        self.hash: TransactionHash = hash_
        """
        The transaction hash, used to uniquely identify the transaction on the
        Tangle.

        This value is generated by taking a hash of the raw transaction trits.

        :type: :py:class:`TransactionHash`
        """

        self.bundle_hash: Optional[BundleHash] = bundle_hash
        """
        The bundle hash, used to identify transactions that are part of the same
        bundle.

        This value is generated by taking a hash of the metadata from all
        transactions in the bundle.

        :type: :py:class:`BundleHash`
        """

        self.address: Address = address
        """
        The address associated with this transaction.

        Depending on the transaction's ``value``, this address may be a sender
        or a recipient. If ``value`` is != 0, the associated address' balance is
        adjusted as a result of this transaction.

        :type: :py:class:`Address`
        """

        self.value: int = value
        """
        The number of iotas being transferred in this transaction:

        - If this value is negative, then the ``address`` is spending iotas.
        - If it is positive, then the ``address`` is receiving iotas.
        - If it is zero, then this transaction is being used to carry metadata
          (such as a signature fragment or a message) instead of transferring
          iotas.

        :type: ``int``
        """

        self._legacy_tag: Optional[Tag] = legacy_tag
        """
        A short message attached to the transaction.

        .. warning::
            Deprecated, use :py:attr:`Transaction.tag` instead.

        :type: :py:class:`Tag`
        """

        self.nonce: Optional[Nonce] = nonce
        """
        Unique value used to increase security of the transaction hash.

        This is the product of the PoW process.

        :type: :py:class:`Nonce`
        """

        self.timestamp: int = timestamp
        """
        Timestamp used to increase the security of the transaction hash.

        Describes when the transaction was created.

        .. important::
            This value is easy to forge!
            Do not rely on it when resolving conflicts!

        :type: ``int``, unix timestamp in seconds.
        """

        self.current_index: Optional[int] = current_index
        """
        The position of the transaction inside the bundle.

           - If the ``current_index`` value is 0, then this is the "head transaction".
           - If it is equal to ``last_index``, then this is the "tail transaction".

        For value transfers, the "spend" transaction is generally in the
        0th position, followed by inputs, and the "change" transaction
        is last.

        :type: ``int``
        """

        self.last_index: Optional[int] = last_index
        """
        The index of the final transaction in the bundle.

        This value is attached to every transaction to make it easier to
        traverse and verify bundles.

        :type: ``int``
        """

        self.trunk_transaction_hash: Optional[TransactionHash] = trunk_transaction_hash
        """
        The transaction hash of the next transaction in the bundle.

        In order to add a transaction to the Tangle, the client must
        perform PoW to "approve" two existing transactions, called the
        "trunk" and "branch" transactions.

        The trunk transaction is generally used to link transactions
        within a bundle.

        :type: :py:class:`TransactionHash`
        """

        self.branch_transaction_hash: Optional[TransactionHash] = branch_transaction_hash
        """
        An unrelated transaction that this transaction "approves".

        In order to add a transaction to the Tangle, the client must
        perform PoW to "approve" two existing transactions, called the
        "trunk" and "branch" transactions.

        The branch transaction may be selected strategically to maximize
        the bundle's chances of getting confirmed; otherwise it usually
        has no significance.

        :type: :py:class:`TransactionHash`
        """

        self.tag: Optional[Tag] = tag
        """
        Optional classification tag applied to this transaction.

        Many transactions have empty tags (``Tag(b'999999999999999999999999999')``).

        :type: :py:class:`Tag`
        """

        self.attachment_timestamp: Optional[int] = attachment_timestamp
        """
        Estimated epoch time of the attachment to the tangle.

        Decribes when the proof-of-work for this transaction was done.

        :type: ``int``, unix timestamp in milliseconds,
        """

        self.attachment_timestamp_lower_bound: Optional[int] = attachment_timestamp_lower_bound
        """
        The lowest possible epoch time of the attachment to the tangle.

        :type: ``int``, unix timestamp in milliseconds.
        """

        self.attachment_timestamp_upper_bound: Optional[int] = attachment_timestamp_upper_bound
        """
        The highest possible epoch time of the attachment to the tangle.

        :type: ``int``, unix timestamp in milliseconds.
        """

        self.signature_message_fragment: Optional[Fragment] = signature_message_fragment
        """
        "Signature/Message Fragment" (note the slash):

        - For inputs, this contains a fragment of the cryptographic
          signature, used to verify the transaction (depending on the
          security level of the corresponding address, the entire
          signature is usually too large to fit into a single
          transaction, so it is split across multiple transactions
          instead).

        - For other transactions, this contains a fragment of the
          message attached to the transaction (if any).  This can be
          pretty much any value.  Like signatures, the message may be
          split across multiple transactions if it is too large to fit
          inside a single transaction.

        :type: :py:class:`Fragment`
        """

        self.is_confirmed: bool = None
        """
        Whether this transaction has been confirmed by neighbor nodes.
        Must be set manually via the ``getInclusionStates`` API command.

        :type: ``Optional[bool]``

        References:

        - :py:meth:`Iota.get_inclusion_states`
        - :py:meth:`Iota.get_transfers`
        """

    @property
    def is_tail(self) -> bool:
        """
        Returns whether this transaction is a tail (first one in the
        bundle).

        Because of the way the Tangle is organized, the tail transaction
        is generally the last one in the bundle that gets attached, even
        though it occupies the first logical position inside the bundle.
        """
        return self.current_index == 0

    @property
    def value_as_trytes(self) -> TryteString:
        """
        Returns a TryteString representation of the transaction's
        :py:attr:`value`.
        """
        # Note that we are padding to 81 *trits*.
        return TryteString.from_trits(trits_from_int(self.value, pad=81))

    @property
    def timestamp_as_trytes(self) -> TryteString:
        """
        Returns a TryteString representation of the transaction's
        :py:attr:`timestamp`.
        """
        # Note that we are padding to 27 *trits*.
        return TryteString.from_trits(trits_from_int(self.timestamp, pad=27))

    @property
    def current_index_as_trytes(self) -> TryteString:
        """
        Returns a TryteString representation of the transaction's
        :py:attr:`current_index`.
        """
        # Note that we are padding to 27 *trits*.
        return TryteString.from_trits(
                trits_from_int(self.current_index, pad=27),
        )

    @property
    def last_index_as_trytes(self) -> TryteString:
        """
        Returns a TryteString representation of the transaction's
        :py:attr:`last_index`.
        """
        # Note that we are padding to 27 *trits*.
        return TryteString.from_trits(trits_from_int(self.last_index, pad=27))

    @property
    def attachment_timestamp_as_trytes(self) -> TryteString:
        """
        Returns a TryteString representation of the transaction's
        :py:attr:`attachment_timestamp`.
        """
        # Note that we are padding to 27 *trits*.
        return TryteString.from_trits(
                trits_from_int(self.attachment_timestamp, pad=27),
        )

    @property
    def attachment_timestamp_lower_bound_as_trytes(self) -> TryteString:
        """
        Returns a TryteString representation of the transaction's
        :py:attr:`attachment_timestamp_lower_bound`.
        """
        # Note that we are padding to 27 *trits*.
        return TryteString.from_trits(
                trits_from_int(self.attachment_timestamp_lower_bound, pad=27),
        )

    @property
    def attachment_timestamp_upper_bound_as_trytes(self) -> TryteString:
        """
        Returns a TryteString representation of the transaction's
        :py:attr:`attachment_timestamp_upper_bound`.
        """
        # Note that we are padding to 27 *trits*.
        return TryteString.from_trits(
                trits_from_int(self.attachment_timestamp_upper_bound, pad=27),
        )

    def as_json_compatible(self) -> dict:
        """
        Returns a JSON-compatible representation of the object.

        :return:
            ``dict`` with the following structure::

                {
                    'hash_': TransactionHash,
                    'signature_message_fragment': Fragment,
                    'address': Address,
                    'value': int,
                    'legacy_tag': Tag,
                    'timestamp': int,
                    'current_index': int,
                    'last_index': int,
                    'bundle_hash': BundleHash,
                    'trunk_transaction_hash': TransactionHash,
                    'branch_transaction_hash': TransactionHash,
                    'tag': Tag,
                    'attachment_timestamp': int,
                    'attachment_timestamp_lower_bound': int,
                    'attachment_timestamp_upper_bound': int,
                    'nonce': Nonce,
                }

        References:

        - :py:class:`iota.json.JsonEncoder`.
        """
        return {
            'hash_': self.hash,
            'signature_message_fragment': self.signature_message_fragment,
            'address': self.address,
            'value': self.value,
            'legacy_tag': self.legacy_tag,
            'timestamp': self.timestamp,
            'current_index': self.current_index,
            'last_index': self.last_index,
            'bundle_hash': self.bundle_hash,
            'trunk_transaction_hash': self.trunk_transaction_hash,
            'branch_transaction_hash': self.branch_transaction_hash,
            'tag': self.tag,
            'attachment_timestamp': self.attachment_timestamp,

            'attachment_timestamp_lower_bound':
                self.attachment_timestamp_lower_bound,

            'attachment_timestamp_upper_bound':
                self.attachment_timestamp_upper_bound,

            'nonce': self.nonce,
        }

    def as_tryte_string(self) -> TransactionTrytes:
        """
        Returns a TryteString representation of the transaction.

        :return:
            :py:class:`TryteString` object.
        """
        return TransactionTrytes(
                self.signature_message_fragment
                + self.address.address
                + self.value_as_trytes
                + self.legacy_tag
                + self.timestamp_as_trytes
                + self.current_index_as_trytes
                + self.last_index_as_trytes
                + self.bundle_hash
                + self.trunk_transaction_hash
                + self.branch_transaction_hash
                + self.tag
                + self.attachment_timestamp_as_trytes
                + self.attachment_timestamp_lower_bound_as_trytes
                + self.attachment_timestamp_upper_bound_as_trytes
                + self.nonce
        )

    def get_bundle_essence_trytes(self) -> TryteString:
        """
        Returns the values needed for calculating bundle hash.
        The bundle hash is the hash of the bundle essence, which is itself
        the hash of the following fields of transactions in the bundle:

            - ``address``,
            - ``value``,
            - ``legacy_tag``,
            - ``current_index``,
            - ``last_index``,
            - and ``timestamp``.

        The transaction's ``signature_message_fragment`` field contains
        the signature generated by signing the bundle hash with the address's
        private key.

        :return:
            :py:class:`TryteString` object.
        """
        return (
                self.address.address
                + self.value_as_trytes
                + self.legacy_tag
                + self.timestamp_as_trytes
                + self.current_index_as_trytes
                + self.last_index_as_trytes
        )

    @property
    def legacy_tag(self) -> Tag:
        """
        Return the legacy tag of the transaction.
        If no legacy tag was set, returns the tag instead.
        """
        return self._legacy_tag or self.tag


B = TypeVar('B', bound='Bundle')


class Bundle(JsonSerializable, Sequence[Transaction]):
    """
    A collection of transactions, treated as an atomic unit when
    attached to the Tangle.

    Note: unlike a block in a blockchain, bundles are not first-class
    citizens in IOTA; only transactions get stored in the Tangle.

    Instead, Bundles must be inferred by following linked transactions
    with the same bundle hash.

    :param Optional[Iterable[Transaction]] transactions:
        Transactions in the bundle. Note that transactions will be sorted into
        ascending order based on their ``current_index``.

    :return:
        :py:class:`Bundle` object.

    References:

    - :py:class:`Iota.get_transfers`
    """

    @classmethod
    def from_tryte_strings(cls: Type[B], trytes: Iterable[TryteString]) -> B:
        """
        Creates a Bundle object from a list of tryte values.

        Note, that this is effectively calling
        :py:meth:`Transaction.from_tryte_string` on the iterbale elements and
        constructing the bundle from the created transactions.

        :param Iterable[TryteString] trytes:
            List of raw transaction trytes.

        :return:
            :py:class:`Bundle` object.

        Example usage::

            from iota import Bundle
            bundle = Bundle.from_tryte_strings([
                b'GYPRVHBEZOOFXSHQBLCYW9ICTCISLHDBNMMVYD9JJHQMPQCTIQAQTJNNNJ9IDXLRCC...',
                b'OYOXYPCLR9PBEY9ORZIEPPDNTI9CQWYZUOTAVBXPSBOFEQAPFLWXSWUIUSJMSJIIIZ...',
                # etc.
            ])

        """
        return cls(map(Transaction.from_tryte_string, trytes))

    def __init__(
            self,
            transactions: Optional[Iterable[Transaction]] = None
    ) -> None:
        super(Bundle, self).__init__()

        self.transactions: List[Transaction] = []
        """
        List of :py:class:`Transaction` objects that are in the bundle.
        """
        if transactions:
            self.transactions.extend(
                    sorted(transactions, key=attrgetter('current_index')),
            )

        self._is_confirmed: Optional[bool] = None
        """
        Whether this bundle has been confirmed by neighbor nodes.
        Must be set manually.

        References:

        - :py:class:`Iota.get_transfers`
        """

    def __contains__(self, transaction: Transaction) -> bool:
        return transaction in self.transactions

    def __getitem__(self, index: int) -> Transaction:
        return self.transactions[index]

    def __iter__(self) -> Iterator[Transaction]:
        return iter(self.transactions)

    def __len__(self) -> int:
        return len(self.transactions)

    @property
    def is_confirmed(self) -> Optional[bool]:
        """
        Returns whether this bundle has been confirmed by neighbor
        nodes.

        This attribute must be set manually.

        :return: ``bool``

        References:

        - :py:class:`Iota.get_transfers`
        """
        return self._is_confirmed

    @is_confirmed.setter
    def is_confirmed(self, new_is_confirmed: bool) -> None:
        """
        Sets the ``is_confirmed`` for the bundle.
        """
        self._is_confirmed = new_is_confirmed

        for txn in self:
            txn.is_confirmed = new_is_confirmed

    @property
    def hash(self) -> Optional[BundleHash]:
        """
        Returns the hash of the bundle.

        This value is determined by inspecting the bundle's tail
        transaction, so in a few edge cases, it may be incorrect.

        :return:
            - :py:class:`BundleHash` object, or
            - If the bundle has no transactions, this method returns ``None``.
        """
        try:
            return self.tail_transaction.bundle_hash
        except IndexError:
            return None

    @property
    def tail_transaction(self) -> Transaction:
        """
        Returns the tail transaction of the bundle.

        :return: :py:class:`Transaction`
        """
        return self[0]

    def get_messages(self, errors: str = 'drop') -> List[str]:
        """
        Attempts to decipher encoded messages from the transactions in
        the bundle.

        :param str errors:
            How to handle trytes that can't be converted, or bytes that
            can't be decoded using UTF-8:

            'drop'
                Drop the trytes from the result.

            'strict'
                Raise an exception.

            'replace'
                Replace with a placeholder character.

            'ignore'
                Omit the invalid tryte/byte sequence.

        :return: ``List[str]``
        """
        decode_errors = 'strict' if errors == 'drop' else errors

        messages = []

        for group in self.group_transactions():
            # Ignore inputs.
            if group[0].value < 0:
                continue

            message_trytes = TryteString(b'')
            for txn in group:
                message_trytes += txn.signature_message_fragment

            if message_trytes:
                try:
                    messages.append(message_trytes.decode(decode_errors))
                except (TrytesDecodeError, UnicodeDecodeError):
                    if errors != 'drop':
                        raise

        return messages

    def as_tryte_strings(self, head_to_tail: bool = False) -> List[TransactionTrytes]:
        """
        Returns TryteString representations of the transactions in this
        bundle.

        :param bool head_to_tail:
            Determines the order of the transactions:

            - ``True``: head txn first, tail txn last.
            - ``False`` (default): tail txn first, head txn last.

            Note that the order is reversed by default, as this is the
            way bundles are typically broadcast to the Tangle.

        :return: ``List[TransactionTrytes]``
        """
        transactions = self if head_to_tail else reversed(self)
        return [t.as_tryte_string() for t in transactions]

    def as_json_compatible(self) -> List[dict]:
        """
        Returns a JSON-compatible representation of the object.

        :return:
            ``List[dict]``. The ``dict`` list elements contain individual
            transactions as in :py:meth:`Transaction.as_json_compatible`.

        References:

        - :py:class:`iota.json.JsonEncoder`.
        """
        return [txn.as_json_compatible() for txn in self]

    def group_transactions(self) -> List[List[Transaction]]:
        """
        Groups transactions in the bundle by address.

        :return:
            ``List[List[Transaction]]``
        """
        groups = []

        if self:
            last_txn = self.tail_transaction
            current_group = [last_txn]
            for current_txn in self.transactions[1:]:
                # Transactions are grouped by address, so as long as the
                # address stays consistent from one transaction to
                # another, we are still in the same group.
                if current_txn.address == last_txn.address:
                    current_group.append(current_txn)
                else:
                    groups.append(current_group)
                    current_group = [current_txn]

                last_txn = current_txn

            if current_group:
                groups.append(current_group)

        return groups
