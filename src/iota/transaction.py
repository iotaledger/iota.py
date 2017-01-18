# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from calendar import timegm as unix_timestamp
from datetime import datetime
from typing import Generator, Iterable, Iterator, List, MutableSequence, \
  Optional, Sequence, Text, Tuple

from iota import Address, Hash, Tag, TrytesCompatible, TryteString, \
  int_from_trits, trits_from_int
from iota.crypto import Curl, FRAGMENT_LENGTH, HASH_LENGTH
from iota.crypto.addresses import AddressGenerator
from iota.crypto.signing import KeyGenerator, SignatureFragmentGenerator, \
  validate_signature_fragments
from iota.exceptions import with_context
from iota.json import JsonSerializable
from six import PY2

__all__ = [
  'Bundle',
  'BundleHash',
  'Fragment',
  'ProposedBundle',
  'ProposedTransaction',
  'Transaction',
  'TransactionHash',
  'TransactionTrytes',
]

def get_current_timestamp():
  # type: () -> int
  """
  Returns the current timestamp, used to set ``timestamp`` for new
  :py:class:`ProposedTransaction` objects.

  Split out into a separate function so that it can be mocked during
  unit tests.
  """
  # Python 3.3 introduced a :py:meth:`datetime.timestamp` method, but
  # for compatibility with Python 2, we have to do it the old-fashioned
  # way.
  # :see: http://stackoverflow.com/q/2775864/
  return unix_timestamp(datetime.utcnow().timetuple())


class BundleHash(Hash):
  """
  A TryteString that acts as a bundle hash.
  """
  pass


class TransactionHash(Hash):
  """
  A TryteString that acts as a transaction hash.
  """
  pass


class Fragment(TryteString):
  """
  A signature/message fragment in a transaction.
  """
  LEN = FRAGMENT_LENGTH

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(Fragment, self).__init__(trytes, pad=self.LEN)

    if len(self._trytes) > self.LEN:
      raise with_context(
        exc = ValueError('{cls} values must be {len} trytes long.'.format(
          cls = type(self).__name__,
          len = self.LEN
        )),

        context = {
          'trytes': trytes,
        },
      )


class TransactionTrytes(TryteString):
  """
  A TryteString representation of a Transaction.
  """
  LEN = 2673

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(TransactionTrytes, self).__init__(trytes, pad=self.LEN)

    if len(self._trytes) > self.LEN:
      raise with_context(
        exc = ValueError('{cls} values must be {len} trytes long.'.format(
          cls = type(self).__name__,
          len = self.LEN
        )),

        context = {
          'trytes': trytes,
        },
      )


class Transaction(JsonSerializable):
  """
  A transaction that has been attached to the Tangle.
  """
  @classmethod
  def from_tryte_string(cls, trytes):
    # type: (TrytesCompatible) -> Transaction
    """
    Creates a Transaction object from a sequence of trytes.
    """
    tryte_string = TransactionTrytes(trytes)

    hash_ = [0] * HASH_LENGTH # type: MutableSequence[int]

    sponge = Curl()
    sponge.absorb(tryte_string.as_trits())
    sponge.squeeze(hash_)

    return cls(
      hash_ = TransactionHash.from_trits(hash_),
      signature_message_fragment = tryte_string[0:2187],
      address = Address(tryte_string[2187:2268]),
      value = int_from_trits(tryte_string[2268:2295].as_trits()),
      tag = Tag(tryte_string[2295:2322]),
      timestamp = int_from_trits(tryte_string[2322:2331].as_trits()),
      current_index = int_from_trits(tryte_string[2331:2340].as_trits()),
      last_index = int_from_trits(tryte_string[2340:2349].as_trits()),
      bundle_hash = BundleHash(tryte_string[2349:2430]),
      trunk_transaction_hash = TransactionHash(tryte_string[2430:2511]),
      branch_transaction_hash = TransactionHash(tryte_string[2511:2592]),
      nonce = Hash(tryte_string[2592:2673]),
    )

  def __init__(
      self,
      hash_,
      signature_message_fragment,
      address,
      value,
      tag,
      timestamp,
      current_index,
      last_index,
      bundle_hash,
      trunk_transaction_hash,
      branch_transaction_hash,
      nonce,
  ):
    # type: (Optional[TransactionHash], Optional[Fragment], Address, int, Optional[Tag], int, Optional[int], Optional[int], Optional[BundleHash], Optional[TransactionHash], Optional[TransactionHash], Optional[Hash]) -> None
    self.hash = hash_ # type: Optional[TransactionHash]
    """
    Transaction ID, generated by taking a hash of the transaction
    trits.
    """

    self.bundle_hash = bundle_hash # type: Optional[BundleHash]
    """
    Bundle hash, generated by taking a hash of metadata from all the
    transactions in the bundle.
    """

    self.address = address # type: Address
    """
    The address associated with this transaction.
    If ``value`` is != 0, the associated address' balance is adjusted
    as a result of this transaction.
    """

    self.value = value # type: int
    """
    Amount to adjust the balance of ``address``.
    Can be negative (i.e., for spending inputs).
    """

    self.tag = tag # type: Optional[Tag]
    """
    Optional classification tag applied to this transaction.
    """

    self.nonce = nonce # type: Optional[Hash]
    """
    Unique value used to increase security of the transaction hash.
    """

    self.timestamp = timestamp # type: int
    """
    Timestamp used to increase the security of the transaction hash.

    IMPORTANT: This value is easy to forge!
    Do not rely on it when resolving conflicts!
    """

    self.current_index = current_index # type: Optional[int]
    """
    The position of the transaction inside the bundle.

    For value transfers, the "spend" transaction is generally in the
    0th position, followed by inputs, and the "change" transaction is
    last.
    """

    self.last_index = last_index # type: Optional[int]
    """
    The position of the final transaction inside the bundle.
    """

    self.trunk_transaction_hash = trunk_transaction_hash # type: Optional[TransactionHash]
    """
    In order to add a transaction to the Tangle, you must perform PoW
    to "approve" two existing transactions, called the "trunk" and
    "branch" transactions.

    The trunk transaction is generally used to link transactions within
    a bundle.
    """

    self.branch_transaction_hash = branch_transaction_hash # type: Optional[TransactionHash]
    """
    In order to add a transaction to the Tangle, you must perform PoW
    to "approve" two existing transactions, called the "trunk" and
    "branch" transactions.

    The branch transaction generally has no significance.
    """

    self.signature_message_fragment = signature_message_fragment # type: Optional[Fragment]
    """
    "Signature/Message Fragment" (note the slash):

    - For inputs, this contains a fragment of the cryptographic
      signature, used to verify the transaction (the entire signature
      is too large to fit into a single transaction, so it is split
      across multiple transactions instead).

    - For other transactions, this contains a fragment of the message
      attached to the transaction (if any).  This can be pretty much
      any value.  Like signatures, the message may be split across
      multiple transactions if it is too large to fit inside a single
      transaction.
    """

    self.is_confirmed = None # type: Optional[bool]
    """
    Whether this transaction has been confirmed by neighbor nodes.
    Must be set manually via the ``getInclusionStates`` API command.

    References:
      - :py:meth:`iota.api.StrictIota.get_inclusion_states`
      - :py:meth:`iota.api.Iota.get_transfers`
    """

  @property
  def is_tail(self):
    # type: () -> bool
    """
    Returns whether this transaction is a tail.
    """
    return self.current_index == 0

  @property
  def value_as_trytes(self):
    # type: () -> TryteString
    """
    Returns a TryteString representation of the transaction's value.
    """
    # Note that we are padding to 81 _trits_.
    return TryteString.from_trits(trits_from_int(self.value, pad=81))

  @property
  def timestamp_as_trytes(self):
    # type: () -> TryteString
    """
    Returns a TryteString representation of the transaction's
    timestamp.
    """
    # Note that we are padding to 27 _trits_.
    return TryteString.from_trits(trits_from_int(self.timestamp, pad=27))

  @property
  def current_index_as_trytes(self):
    # type: () -> TryteString
    """
    Returns a TryteString representation of the transaction's
    ``current_index`` value.
    """
    # Note that we are padding to 27 _trits_.
    return TryteString.from_trits(trits_from_int(self.current_index, pad=27))

  @property
  def last_index_as_trytes(self):
    # type: () -> TryteString
    """
    Returns a TryteString representation of the transaction's
    ``last_index`` value.
    """
    # Note that we are padding to 27 _trits_.
    return TryteString.from_trits(trits_from_int(self.last_index, pad=27))

  def as_json_compatible(self):
    # type: () -> dict
    """
    Returns a JSON-compatible representation of the object.

    References:
      - :py:class:`iota.json.JsonEncoder`.
    """
    return {
      'hash':                       self.hash,
      'signature_message_fragment': self.signature_message_fragment,
      'address':                    self.address,
      'value':                      self.value,
      'tag':                        self.tag,
      'timestamp':                  self.timestamp,
      'current_index':              self.current_index,
      'last_index':                 self.last_index,
      'bundle_hash':                self.bundle_hash,
      'trunk_transaction_hash':     self.trunk_transaction_hash,
      'branch_transaction_hash':    self.branch_transaction_hash,
      'nonce':                      self.nonce,
    }

  def as_tryte_string(self):
    # type: () -> TransactionTrytes
    """
    Returns a TryteString representation of the transaction.
    """
    return TransactionTrytes(
        self.signature_message_fragment
      + self.address.address
      + self.value_as_trytes
      + self.tag
      + self.timestamp_as_trytes
      + self.current_index_as_trytes
      + self.last_index_as_trytes
      + self.bundle_hash
      + self.trunk_transaction_hash
      + self.branch_transaction_hash
      + self.nonce
    )

  def get_signature_validation_trytes(self):
    # type: () -> TryteString
    """
    Returns the values needed to validate the transaction's
    ``signature_message_fragment`` value.
    """
    return (
        self.address.address
      + self.value_as_trytes
      + self.tag
      + self.timestamp_as_trytes
      + self.current_index_as_trytes
      + self.last_index_as_trytes
    )


class ProposedTransaction(Transaction):
  """
  A transaction that has not yet been attached to the Tangle.

  Provide to :py:meth:`iota.api.Iota.send_transfer` to attach to
  tangle and publish/store.
  """
  def __init__(self, address, value, tag=None, message=None, timestamp=None):
    # type: (Address, int, Optional[Tag], Optional[TryteString], Optional[int]) -> None
    if not timestamp:
      timestamp = get_current_timestamp()

    super(ProposedTransaction, self).__init__(
      address                     = address,
      tag                         = Tag(b'') if tag is None else tag,
      timestamp                   = timestamp,
      value                       = value,

      # These values will be populated when the bundle is finalized.
      bundle_hash                 = None,
      current_index               = None,
      hash_                       = None,
      last_index                  = None,
      signature_message_fragment  = None,

      # These values start out empty; they will be populated when the
      # node does PoW.
      branch_transaction_hash     = TransactionHash(b''),
      nonce                       = Hash(b''),
      trunk_transaction_hash      = TransactionHash(b''),
    )

    self.message = TryteString(b'') if message is None else message

  def as_tryte_string(self):
    # type: () -> TryteString
    """
    Returns a TryteString representation of the transaction.
    """
    if not self.bundle_hash:
      raise with_context(
        exc = RuntimeError(
          'Cannot get TryteString representation of {cls} instance '
          'without a bundle hash; call ``bundle.finalize()`` first '
          '(``exc.context`` has more info).'.format(
            cls = type(self).__name__,
          ),
        ),

        context = {
          'transaction': self,
        },
      )

    return super(ProposedTransaction, self).as_tryte_string()


class Bundle(JsonSerializable, Sequence[Transaction]):
  """
  A collection of transactions, treated as an atomic unit when
  attached to the Tangle.

  Note: unlike a block in a blockchain, bundles are not first-class
  citizens in IOTA; only transactions get stored in the Tangle.

  Instead, Bundles must be inferred by following linked transactions
  with the same bundle hash.

  References:
    - :py:class:`iota.commands.extended.get_bundles.GetBundlesCommand`
  """
  @classmethod
  def from_tryte_strings(cls, trytes):
    # type: (Iterable[TryteString]) -> Bundle
    """
    Creates a Bundle object from a list of tryte values.
    """
    return cls(map(Transaction.from_tryte_string, trytes))

  def __init__(self, transactions=None):
    # type: (Optional[Iterable[Transaction]]) -> None
    super(Bundle, self).__init__()

    self.transactions = [] # type: List[Transaction]
    if transactions:
      self.transactions.extend(transactions)

    self._is_confirmed = None # type: Optional[bool]
    """
    Whether this bundle has been confirmed by neighbor nodes.
    Must be set manually.

    References:
      - :py:class:`iota.commands.extended.get_transfers.GetTransfersCommand`
    """

  def __contains__(self, transaction):
    # type: (Transaction) -> bool
    return transaction in self.transactions

  def __getitem__(self, index):
    # type: (int) -> Transaction
    return self.transactions[index]

  def __iter__(self):
    # type: () -> Iterator[Transaction]
    return iter(self.transactions)

  def __len__(self):
    # type: () -> int
    return len(self.transactions)

  @property
  def is_confirmed(self):
    # type: () -> Optional[bool]
    """
    Returns whether this bundle has been confirmed by neighbor nodes.

    This attribute must be set manually.

    References:
      - :py:class:`iota.commands.extended.get_transfers.GetTransfersCommand`
    """
    return self._is_confirmed

  @is_confirmed.setter
  def is_confirmed(self, new_is_confirmed):
    # type: (bool) -> None
    """
    Sets the ``is_confirmed`` for the bundle.
    """
    self._is_confirmed = new_is_confirmed

    for txn in self:
      txn.is_confirmed = new_is_confirmed

  @property
  def hash(self):
    # type: () -> Optional[BundleHash]
    """
    Returns the hash of the bundle.

    This value is determined by inspecting the bundle's tail
    transaction, so in a few edge cases, it may be incorrect.

    If the bundle has no transactions, this method returns `None`.
    """
    try:
      return self.tail_transaction.bundle_hash
    except IndexError:
      return None

  @property
  def tail_transaction(self):
    # type: () -> Transaction
    """
    Returns the tail transaction of the bundle.
    """
    return self[0]

  def as_json_compatible(self):
    # type: () -> List[dict]
    """
    Returns a JSON-compatible representation of the object.

    References:
      - :py:class:`iota.json.JsonEncoder`.
    """
    return [txn.as_json_compatible() for txn in self]


class BundleValidator(object):
  """
  Checks a bundle and its transactions for problems.
  """
  def __init__(self, bundle):
    # type: (Bundle) -> None
    super(BundleValidator, self).__init__()

    self.bundle = bundle

    self._errors    = [] # type: Optional[List[Text]]
    self._validator = self._create_validator()

  @property
  def errors(self):
    # type: () -> List[Text]
    """
    Returns all errors found with the bundle.
    """
    try:
      self._errors.extend(self._validator) # type: List[Text]
    except StopIteration:
      pass

    return self._errors

  def is_valid(self):
    # type: () -> bool
    """
    Returns whether the bundle is valid.
    """
    if not self._errors:
      try:
        # We only have to check for a single error to determine if the
        # bundle is valid or not.
        self._errors.append(next(self._validator))
      except StopIteration:
        pass

    return not self._errors

  def _create_validator(self):
    # type: () -> Generator[Text]
    """
    Creates a generator that does all the work.
    """
    bundle_hash = self.bundle.hash
    last_index  = len(self.bundle) - 1

    balance = 0
    for (i, txn) in enumerate(self.bundle): # type: Tuple[int, Transaction]
      balance += txn.value

      if txn.bundle_hash != bundle_hash:
        yield 'Transaction {i} has invalid bundle hash.'.format(
          i = i,
        )

      if txn.current_index != i:
        yield (
          'Transaction {i} has invalid current index value '
          '(expected {i}, actual {actual}).'.format(
            actual  = txn.current_index,
            i       = i,
          )
        )

      if txn.last_index != last_index:
        yield (
          'Transaction {i} has invalid last index value '
          '(expected {expected}, actual {actual}).'.format(
            actual    = txn.last_index,
            expected  = last_index,
            i         = i,
          )
        )

    if balance != 0:
      yield (
        'Bundle has invalid balance (expected 0, actual {actual}).'.format(
          actual = balance,
        )
      )

    # Signature validation is only meaningful if the transactions are
    # otherwise valid.
    if not self._errors:
      i = 0
      while i <= last_index:
        txn = self.bundle[i]

        if txn.value < 0:
          signature_fragments = [txn.signature_message_fragment]

          # The following transaction(s) should contain additional
          # fragments.
          fragments_valid = True
          j = 0
          for j in range(1, AddressGenerator.DIGEST_ITERATIONS):
            i += 1
            try:
              next_txn = self.bundle[i]
            except IndexError:
              yield (
                'Reached end of bundle while looking for '
                'signature fragment {j} for transaction {i}.'.format(
                  i = txn.current_index,
                  j = j+1,
                )
              )
              fragments_valid = False
              break

            if next_txn.address != txn.address:
              yield (
                'Unable to find signature fragment {j} '
                'for transaction {i}.'.format(
                  i = txn.current_index,
                  j = j+1,
                )
              )
              fragments_valid = False
              break

            if next_txn.value != 0:
              yield (
                'Transaction {i} has invalid amount '
                '(expected 0, actual {actual}).'.format(
                  actual  = next_txn.value,
                  i       = next_txn.current_index,
                )
              )
              fragments_valid = False
              # Keep going, just in case there's another signature
              # fragment next (so that we skip it in the next iteration
              # of the outer loop).
              continue

            signature_fragments.append(next_txn.signature_message_fragment)

          if fragments_valid:
            signature_valid = validate_signature_fragments(
              fragments   = signature_fragments,
              hash_       = txn.bundle_hash,
              public_key  = txn.address,
            )

            if not signature_valid:
              yield (
                'Transaction {i} has invalid signature '
                '(using {fragments} fragments).'.format(
                  fragments = len(signature_fragments),
                  i         = txn.current_index,
                )
              )

          # Skip signature fragments in the next iteration.
          # Note that it's possible to have
          # ``j < AddressGenerator.DIGEST_ITERATIONS`` if the bundle is
          # badly malformed.
          i += j

        else:
          # No signature to validate; skip this transaction.
          i += 1


class ProposedBundle(JsonSerializable, Sequence[ProposedTransaction]):
  """
  A collection of proposed transactions, to be treated as an atomic
  unit when attached to the Tangle.
  """
  def __init__(self, transactions=None, inputs=None, change_address=None):
    # type: (Optional[Iterable[ProposedTransaction]], Optional[Iterable[Address]], Optional[Address]) -> None
    super(ProposedBundle, self).__init__()

    self.hash = None # type: Optional[Hash]

    self._transactions = [] # type: List[ProposedTransaction]

    if transactions:
      for t in transactions:
        self.add_transaction(t)

    if inputs:
      self.add_inputs(inputs)

    self.change_address = change_address

  def __bool__(self):
    # type: () -> bool
    """
    Returns whether this bundle has any transactions.
    """
    return bool(self._transactions)

  # :bc: Magic methods have different names in Python 2.
  if PY2:
    __nonzero__ = __bool__

  def __contains__(self, transaction):
    # type: (ProposedTransaction) -> bool
    return transaction in self._transactions

  def __getitem__(self, index):
    # type: (int) -> ProposedTransaction
    """
    Returns the transaction at the specified index.
    """
    return self._transactions[index]

  def __iter__(self):
    # type: () -> Iterator[ProposedTransaction]
    """
    Iterates over transactions in the bundle.
    """
    return iter(self._transactions)

  def __len__(self):
    # type: () -> int
    """
    Returns te number of transactions in the bundle.
    """
    return len(self._transactions)

  @property
  def balance(self):
    # type: () -> int
    """
    Returns the bundle balance.
    In order for a bundle to be valid, its balance must be 0:

      - A positive balance means that there aren't enough inputs to
        cover the spent amount.
        Add more inputs using :py:meth:`add_inputs`.
      - A negative balance means that there are unspent inputs.
        Use :py:meth:`send_unspent_inputs_to` to send the unspent
        inputs to a "change" address.
    """
    return sum(t.value for t in self._transactions)

  @property
  def tag(self):
    # type: () -> Tag
    """
    Determines the most relevant tag for the bundle.
    """
    for txn in reversed(self): # type: ProposedTransaction
      if txn.tag:
        # noinspection PyTypeChecker
        return txn.tag

    return Tag(b'')

  def as_json_compatible(self):
    # type: () -> List[dict]
    """
    Returns a JSON-compatible representation of the object.

    References:
      - :py:class:`iota.json.JsonEncoder`.
    """
    return [txn.as_json_compatible() for txn in self]

  def as_tryte_strings(self):
    # type: () -> List[TryteString]
    """
    Returns the bundle as a list of TryteStrings, suitable as inputs
    for :py:meth:`iota.api.Iota.send_trytes`.
    """
    # Return the transaction trytes in reverse order, so that the tail
    # transaction is last.  This will allow the node to link the
    # transactions properly when it performs PoW.
    return [t.as_tryte_string() for t in reversed(self)]

  def add_transaction(self, transaction):
    # type: (ProposedTransaction) -> None
    """
    Adds a transaction to the bundle.

    If the transaction message is too long, it will be split
    automatically into multiple transactions.
    """
    if self.hash:
      raise RuntimeError('Bundle is already finalized.')

    if transaction.value < 0:
      raise ValueError('Use ``add_inputs`` to add inputs to the bundle.')

    self._transactions.append(ProposedTransaction(
      address   = transaction.address,
      value     = transaction.value,
      tag       = transaction.tag,
      message   = transaction.message[:Fragment.LEN],
      timestamp = transaction.timestamp,
    ))

    # If the message is too long to fit in a single transactions,
    # it must be split up into multiple transactions so that it will
    # fit.
    fragment = transaction.message[Fragment.LEN:]
    while fragment:
      self._transactions.append(ProposedTransaction(
        address   = transaction.address,
        value     = 0,
        tag       = transaction.tag,
        message   = fragment[:Fragment.LEN],
        timestamp = transaction.timestamp,
      ))

      fragment = fragment[Fragment.LEN:]

  def add_inputs(self, inputs):
    # type: (Iterable[Address]) -> None
    """
    Adds inputs to spend in the bundle.

    Note that each input requires two transactions, in order to
    hold the entire signature.

    :param inputs:
      Addresses to use as the inputs for this bundle.

      IMPORTANT: Must have ``balance`` and ``key_index`` attributes!
      Use :py:meth:`iota.api.get_inputs` to prepare inputs.
    """
    if self.hash:
      raise RuntimeError('Bundle is already finalized.')

    for addy in inputs:
      if addy.balance is None:
        raise with_context(
          exc = ValueError(
            'Address {address} has null ``balance`` '
            '(``exc.context`` has more info).'.format(
              address = addy,
            ),
          ),

          context = {
            'address': addy,
          },
        )

      if addy.key_index is None:
        raise with_context(
          exc = ValueError(
            'Address {address} has null ``key_index`` '
            '(``exc.context`` has more info).'.format(
              address = addy,
            ),
          ),

          context = {
            'address': addy,
          },
        )

      # Add the input as a transaction.
      self._transactions.append(ProposedTransaction(
        address = addy,
        tag     = self.tag,

        # Spend the entire address balance; if necessary, we will add a
        # change transaction to the bundle.
        value = -addy.balance,
      ))

      # Signatures require additional transactions to store, due to
      # transaction length limit.
      # Subtract 1 to account for the transaction we just added.
      for _ in range(AddressGenerator.DIGEST_ITERATIONS - 1):
        self._transactions.append(ProposedTransaction(
          address = addy,
          tag     = self.tag,

          # Note zero value; this is a meta transaction.
          value = 0,
        ))

  def send_unspent_inputs_to(self, address):
    # type: (Address) -> None
    """
    Adds a transaction to send "change" (unspent inputs) to the
    specified address.

    If the bundle has no unspent inputs, this method does nothing.
    """
    if self.hash:
      raise RuntimeError('Bundle is already finalized.')

    self.change_address = address

  def finalize(self):
    # type: () -> None
    """
    Finalizes the bundle, preparing it to be attached to the Tangle.
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
          address = self.change_address,
          value   = -balance,
          tag     = self.tag,
        ))
      else:
        raise ValueError(
          'Bundle has unspent inputs (balance: {balance}); '
          'use ``send_unspent_inputs_to`` to create '
          'change transaction.'.format(
            balance = balance,
          ),
        )
    elif balance > 0:
      raise ValueError(
        'Inputs are insufficient to cover bundle spend '
        '(balance: {balance}).'.format(
          balance = balance,
        ),
      )

    # Generate bundle hash.
    sponge      = Curl()
    last_index  = len(self) - 1

    for (i, txn) in enumerate(self): # type: Tuple[int, ProposedTransaction]
      txn.current_index = i
      txn.last_index    = last_index

      sponge.absorb(txn.get_signature_validation_trytes().as_trits())

    bundle_hash = [0] * HASH_LENGTH # type: MutableSequence[int]
    sponge.squeeze(bundle_hash)
    self.hash = Hash.from_trits(bundle_hash)

    # Copy bundle hash to individual transactions.
    for txn in self:
      txn.bundle_hash = self.hash

      # Initialize signature/message fragment.
      txn.signature_message_fragment = Fragment(txn.message or b'')

  def sign_inputs(self, key_generator):
    # type: (KeyGenerator) -> None
    """
    Sign inputs in a finalized bundle.
    """
    if not self.hash:
      raise RuntimeError('Cannot sign inputs until bundle is finalized.')

    # Use a counter for the loop so that we can skip ahead as we go.
    i = 0
    while i < len(self):
      txn = self[i]

      if txn.value < 0:
        # In order to sign the input, we need to know the index of
        # the private key used to generate it.
        if txn.address.key_index is None:
          raise with_context(
            exc = ValueError(
              'Unable to sign input {input}; ``key_index`` is None '
              '(``exc.context`` has more info).'.format(
                input = txn.address,
              ),
            ),

            context = {
              'transaction': txn,
            },
          )

        signature_fragment_generator =\
          self._create_signature_fragment_generator(key_generator, txn)

        # We can only fit one signature fragment into each transaction,
        # so we have to split the entire signature among the extra
        # transactions we created for this input in
        # :py:meth:`add_inputs`.
        for j in range(AddressGenerator.DIGEST_ITERATIONS):
          self[i+j].signature_message_fragment =\
            next(signature_fragment_generator)

        i += AddressGenerator.DIGEST_ITERATIONS
      else:
        # No signature needed (nor even possible, in some cases); skip
        # this transaction.
        i += 1

  @staticmethod
  def _create_signature_fragment_generator(key_generator, txn):
    # type: (KeyGenerator, ProposedTransaction) -> SignatureFragmentGenerator
    """
    Creates the SignatureFragmentGenerator to sign inputs.

    Split into a separate method so that it can be mocked for unit
    tests.
    """
    return SignatureFragmentGenerator(
      private_key = key_generator.get_keys(
        start       = txn.address.key_index,
        iterations  = AddressGenerator.DIGEST_ITERATIONS
      )[0],

      hash_= txn.bundle_hash,
    )
