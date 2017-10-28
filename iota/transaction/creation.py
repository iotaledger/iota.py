# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Iterable, Iterator, List, MutableSequence, Optional, \
  Sequence, Tuple

from six import PY2

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

  Provide to :py:meth:`iota.api.Iota.send_transfer` to attach to
  tangle and publish/store.
  """
  def __init__(self, address, value, tag=None, message=None, timestamp=None):
    # type: (Address, int, Optional[Tag], Optional[TryteString], Optional[int]) -> None
    if not timestamp:
      timestamp = get_current_timestamp()

    super(ProposedTransaction, self).__init__(
      address                           = address,
      tag                               = Tag(b'') if tag is None else tag,
      timestamp                         = timestamp,
      value                             = value,

      # These values will be populated when the bundle is finalized.
      bundle_hash                       = None,
      current_index                     = None,
      hash_                             = None,
      last_index                        = None,
      signature_message_fragment        = None,
      attachment_timestamp              = 0,
      attachment_timestamp_lower_bound  = 0,
      attachment_timestamp_upper_bound  = 0,

      # These values start out empty; they will be populated when the
      # node does PoW.
      branch_transaction_hash           = TransactionHash(b''),
      nonce                             = Nonce(b''),
      trunk_transaction_hash            = TransactionHash(b''),
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

  def increment_legacy_tag(self):
    """
    Increments the transaction's legacy tag, used to fix insecure
    bundle hashes when finalizing a bundle.

    References:
      - https://github.com/iotaledger/iota.lib.py/issues/84
    """
    self._legacy_tag =\
      Tag.from_trits(add_trits(self.legacy_tag.as_trits(), [1]))


Transfer = ProposedTransaction
"""
Follow naming convention of other libs.
https://github.com/iotaledger/iota.lib.py/issues/72
"""


class ProposedBundle(Bundle, Sequence[ProposedTransaction]):
  """
  A collection of proposed transactions, to be treated as an atomic
  unit when attached to the Tangle.
  """
  def __init__(self, transactions=None, inputs=None, change_address=None):
    # type: (Optional[Iterable[ProposedTransaction]], Optional[Iterable[Address]], Optional[Address]) -> None
    super(ProposedBundle, self).__init__()

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

    Note that each input may require multiple transactions, in order to
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

      self._create_input_transactions(addy)

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
    while True:
      sponge      = Kerl()
      last_index  = len(self) - 1

      for (i, txn) in enumerate(self): # type: Tuple[int, ProposedTransaction]
        txn.current_index = i
        txn.last_index    = last_index

        sponge.absorb(txn.get_signature_validation_trytes().as_trits())

      bundle_hash_trits = [0] * HASH_LENGTH # type: MutableSequence[int]
      sponge.squeeze(bundle_hash_trits)

      bundle_hash = BundleHash.from_trits(bundle_hash_trits)

      # Check that we generated a secure bundle hash.
      # https://github.com/iotaledger/iota.lib.py/issues/84
      if any(13 in part for part in normalize(bundle_hash)):
        # Increment the legacy tag and try again.
        tail_transaction = self.tail_transaction # type: ProposedTransaction
        tail_transaction.increment_legacy_tag()
      else:
        break

    # Copy bundle hash to individual transactions.
    for txn in self:
      txn.bundle_hash = bundle_hash

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

        if txn.address.security_level is None:
          raise with_context(
            exc = ValueError(
              'Unable to sign input {input}; ``security_level`` is None '
              '(``exc.context`` has more info).'.format(
                input = txn.address,
              ),
            ),

            context = {
              'transaction': txn,
            },
          )

        self.sign_input_at(i, key_generator.get_key_for(txn.address))

        i += txn.address.security_level
      else:
        # No signature needed (nor even possible, in some cases); skip
        # this transaction.
        i += 1

  def sign_input_at(self, start_index, private_key):
    # type: (int, PrivateKey) -> None
    """
    Signs the input at the specified index.

    :param start_index:
      The index of the first input transaction.

      If necessary, the resulting signature will be split across
      multiple transactions automatically (i.e., if an input has
      ``security_level=2``, you still only need to call
      :py:meth:`sign_input_at` once).

    :param private_key:
      The private key that will be used to generate the signature.

      Important: be sure that the private key was generated using the
      correct seed, or the resulting signature will be invalid!
    """
    if not self.hash:
      raise RuntimeError('Cannot sign inputs until bundle is finalized.')

    private_key.sign_input_transactions(self, start_index)

  def _create_input_transactions(self, addy):
    # type: (Address) -> None
    """
    Creates transactions for the specified input address.
    """
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
    for _ in range(addy.security_level - 1):
      self._transactions.append(ProposedTransaction(
        address = addy,
        tag     = self.tag,

        # Note zero value; this is a meta transaction.
        value = 0,
      ))
