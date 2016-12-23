# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from calendar import timegm as unix_timestamp
from codecs import encode, decode
from datetime import datetime
from itertools import chain
from typing import Generator, Iterable, List, MutableSequence, \
  Optional, Text, Tuple, Union

from iota import TrytesCodec
from iota.crypto import Curl, HASH_LENGTH
from iota.exceptions import with_context
from six import PY2, binary_type


__all__ = [
  'Address',
  'AddressChecksum',
  'Bundle',
  'BundleHash',
  'Hash',
  'ProposedBundle',
  'ProposedTransaction',
  'Tag',
  'Transaction',
  'TransactionHash',
  'TryteString',
  'TrytesCompatible',
  'int_from_trits',
  'trits_from_int',
]


# Custom types for type hints and docstrings.
Bundle            = Iterable['Transaction']
TrytesCompatible  = Union[binary_type, bytearray, 'TryteString']


def trits_from_int(n, pad=None):
  # type: (int, Optional[int]) -> List[int]
  """
  Returns a trit representation of an integer value.

  :param n:
    Integer value to convert.

  :param pad:
    Ensure the result has at least this many trits.

  References:
    - https://dev.to/buntine/the-balanced-ternary-machines-of-soviet-russia
    - https://en.wikipedia.org/wiki/Balanced_ternary
    - https://rosettacode.org/wiki/Balanced_ternary#Python
  """
  if n == 0:
    trits = []
  else:
    quotient, remainder = divmod(n, 3)

    if remainder == 2:
      # Lend 1 to the next place so we can make this trit negative.
      quotient  += 1
      remainder = -1

    trits = [remainder] + trits_from_int(quotient)

  if pad:
    trits += [0] * max(0, pad - len(trits))

  return trits


def int_from_trits(trits):
  # type: (Iterable[int]) -> int
  """
  Converts a sequence of trits into an integer value.
  """
  # Normally we'd have to wrap ``enumerate`` inside ``reversed``, but
  # balanced ternary puts least significant digits first.
  return sum(base * (3 ** power) for power, base in enumerate(trits))


class TryteString(object):
  """
  A string representation of a sequence of trytes.

  A tryte string is similar in concept to Python's byte string, except
  it has a more limited alphabet.  Byte strings are limited to ASCII
  (256 possible values), while the tryte string alphabet only has 27
  characters (one for each possible tryte configuration).

  IMPORTANT: A TryteString does not represent a numeric value!
  """
  @classmethod
  def from_bytes(cls, bytes_):
    # type: (Union[binary_type, bytearray]) -> TryteString
    """
    Creates a TryteString from a sequence of bytes.
    """
    return cls(encode(bytes_, 'trytes'))

  @classmethod
  def from_trytes(cls, trytes):
    # type: (Iterable[Iterable[int]]) -> TryteString
    """
    Creates a TryteString from a sequence of trytes.

    :param trytes:
      Iterable of tryte values.
      In this context, a tryte is defined as a list containing 3 trits.

    References:
      - :py:meth:`as_trytes`
    """
    chars = bytearray()

    for t in trytes:
      converted = int_from_trits(t)

      # :py:meth:`_tryte_from_int`
      if converted < 0:
        converted += 27

      chars.append(TrytesCodec.alphabet[converted])

    return cls(chars)

  @classmethod
  def from_trits(cls, trits):
    # type: (Iterable[int]) -> TryteString
    """
    Creates a TryteString from a sequence of trits.

    :param trits:
      Iterable of trit values (-1, 0, 1).

    References:
      - :py:func:`int_from_trits`
      - :py:meth:`as_trits`
    """
    # Allow passing a generator or other non-Sized value to this
    # method.
    trits = list(trits)

    if len(trits) % 3:
      # Pad the trits so that it is cleanly divisible into trytes.
      trits += [0] * (3 - (len(trits) % 3))

    return cls.from_trytes(
      # :see: http://stackoverflow.com/a/1751478/
      trits[i:i+3] for i in range(0, len(trits), 3)
    )

  def __init__(self, trytes, pad=None):
    # type: (TrytesCompatible, Optional[int]) -> None
    """
    :param trytes:
      Byte string or bytearray.

    :param pad:
      Ensure at least this many trytes.

      If there are too few, null trytes will be appended to the
      TryteString.

      Note:  If the TryteString is too long, it will _not_ be
      truncated!
    """
    super(TryteString, self).__init__()

    if isinstance(trytes, (int, float)):
      raise with_context(
        exc = TypeError(
          'Converting {type} is not supported; '
          '{cls} is not a numeric type.'.format(
            type  = type(trytes).__name__,
            cls   = type(self).__name__,
          ),
        ),

        context = {
          'trytes': trytes,
        },
      )

    if isinstance(trytes, TryteString):
      incoming_type = type(trytes)

      if incoming_type is TryteString or issubclass(incoming_type, type(self)):
        # Create a copy of the incoming TryteString's trytes, to ensure
        # we don't modify it when we apply padding.
        trytes = bytearray(trytes._trytes)

      else:
        raise with_context(
          exc = TypeError(
            '{cls} cannot be initialized from a(n) {type}.'.format(
              type  = type(trytes).__name__,
              cls   = type(self).__name__,
            ),
          ),

          context = {
            'trytes': trytes,
          },
        )

    else:
      if not isinstance(trytes, bytearray):
        trytes = bytearray(trytes)

      for i, ordinal in enumerate(trytes):
        if ordinal not in TrytesCodec.index:
          raise with_context(
            exc = ValueError(
              'Invalid character {char!r} at position {i} '
              '(expected A-Z or 9).'.format(
                char  = chr(ordinal),
                i     = i,
              ),
            ),

            context = {
              'trytes': trytes,
            },
          )

    if pad:
      trytes += b'9' * max(0, pad - len(trytes))

    self._trytes = trytes # type: bytearray

  def __repr__(self):
    # type: () -> Text
    return 'TryteString({trytes!r})'.format(trytes=binary_type(self._trytes))

  def __bytes__(self):
    # type: () -> binary_type
    """
    Converts the TryteString into a string representation.

    Note that this method will NOT convert the trytes back into bytes;
    use :py:meth:`as_bytes` for that.
    """
    return binary_type(self._trytes)

  def __bool__(self):
    # type: () -> bool
    return bool(self._trytes) and any(t != b'9' for t in self)

  # :bc: Magic methods have different names in Python 2.
  if PY2:
    __nonzero__ = __bool__
    __str__     = __bytes__

  def __len__(self):
    # type: () -> int
    return len(self._trytes)

  def __iter__(self):
    # type: () -> Generator[binary_type]
    # :see: http://stackoverflow.com/a/14267935/
    return (binary_type(self._trytes[i:i + 1]) for i in range(len(self)))

  def __contains__(self, other):
    # type: (TrytesCompatible) -> bool
    if isinstance(other, TryteString):
      return other._trytes in self._trytes
    elif isinstance(other, (binary_type, bytearray)):
      return other in self._trytes
    else:
      raise with_context(
        exc = TypeError(
          'Invalid type for TryteString contains check '
          '(expected Union[TryteString, {binary_type}, bytearray], '
          'actual {type}).'.format(
            binary_type = binary_type.__name__,
            type        = type(other).__name__,
          ),
        ),

        context = {
          'other': other,
        },
      )

  def __getitem__(self, item):
    # type: (Union[int, slice]) -> TryteString
    new_trytes = bytearray()

    sliced = self._trytes[item]

    if isinstance(sliced, int):
      new_trytes.append(sliced)
    else:
      new_trytes.extend(sliced)

    return TryteString(new_trytes)

  def __add__(self, other):
    # type: (TrytesCompatible) -> TryteString
    if isinstance(other, TryteString):
      return TryteString(self._trytes + other._trytes)
    elif isinstance(other, (binary_type, bytearray)):
      return TryteString(self._trytes + other)
    else:
      raise with_context(
        exc = TypeError(
          'Invalid type for TryteString concatenation '
          '(expected Union[TryteString, {binary_type}, bytearray], '
          'actual {type}).'.format(
            binary_type = binary_type.__name__,
            type        = type(other).__name__,
          ),
        ),

        context = {
          'other': other,
        },
      )

  def __eq__(self, other):
    # type: (TrytesCompatible) -> bool
    if isinstance(other, TryteString):
      return self._trytes == other._trytes
    elif isinstance(other, (binary_type, bytearray)):
      return self._trytes == other
    else:
      raise with_context(
        exc = TypeError(
          'Invalid type for TryteString comparison '
          '(expected Union[TryteString, {binary_type}, bytearray], '
          'actual {type}).'.format(
            binary_type = binary_type.__name__,
            type        = type(other).__name__,
          ),
        ),

        context = {
          'other': other,
        },
      )

  # :bc: In Python 2 this must be defined explicitly.
  def __ne__(self, other):
    # type: (TrytesCompatible) -> bool
    return not (self == other)

  def as_bytes(self, errors='strict'):
    # type: (Text) -> binary_type
    """
    Converts the TryteString into a byte string.

    :param errors:
      How to handle trytes that can't be converted:
        - 'strict':   raise a TrytesDecodeError.
        - 'replace':  replace with '?'.
        - 'ignore':   omit the tryte from the byte string.
    """
    # :bc: In Python 2, `decode` does not accept keyword arguments.
    return decode(self._trytes, 'trytes', errors)

  def as_json(self):
    # type: () -> Text
    """
    Converts the TryteString into a JSON representation.

    See :py:class:`iota.json.JsonEncoder`.
    """
    return self._trytes.decode('ascii')

  def as_trytes(self):
    """
    Converts the TryteString into a sequence of trytes.

    Each tryte is represented as a list with 3 trit values.

    See :py:meth:`as_trits` for more info.

    IMPORTANT: TryteString is not a numeric type, so the result of this
    method should not be interpreted as an integer!
    """
    return [
      self._tryte_from_int(TrytesCodec.index[c])
        for c in self._trytes
    ]

  def as_trits(self):
    """
    Converts the TryteString into a sequence of trit values.

    A trit may have value 1, 0, or -1.

    References:
      - https://en.wikipedia.org/wiki/Balanced_ternary

    IMPORTANT: TryteString is not a numeric type, so the result of this
    method should not be interpreted as an integer!
    """
    # http://stackoverflow.com/a/952952/5568265#comment4204394_952952
    return list(chain.from_iterable(self.as_trytes()))

  @staticmethod
  def _tryte_from_int(n):
    """
    Converts an integer into a single tryte.

    This method is specialized for TryteStrings:
      - The value must fit inside a single tryte.
      - If the value is greater than 13, it will trigger an overflow.
    """
    if n > 26:
      raise ValueError('{n} cannot be represented by a single tryte.'.format(
        n = n,
      ))

    # For values greater than 13, trigger an overflow.
    # E.g., 14 => -13, 15 => -12, etc.
    if n > 13:
      n -= 27

    return trits_from_int(n, pad=3)


class Hash(TryteString):
  """
  A TryteString that is exactly one hash long.
  """
  # Divide by 3 to convert trits to trytes.
  LEN = HASH_LENGTH // 3

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(Hash, self).__init__(trytes, pad=self.LEN)

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


class Address(TryteString):
  """
  A TryteString that acts as an address, with support for generating
  and validating checksums.
  """
  LEN = Hash.LEN

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(Address, self).__init__(trytes, pad=self.LEN)

    self.checksum = None
    if len(self._trytes) == (self.LEN + AddressChecksum.LEN):
      self.checksum = AddressChecksum(self[self.LEN:]) # type: Optional[AddressChecksum]

    elif len(self._trytes) > self.LEN:
      raise with_context(
        exc = ValueError(
          'Address values must be {len_no_checksum} trytes (no checksum), '
          'or {len_with_checksum} trytes (with checksum).'.format(
            len_no_checksum   = self.LEN,
            len_with_checksum = self.LEN + AddressChecksum.LEN,
          ),
        ),

        context = {
          'trytes': trytes,
        },
      )

    # Make the address sans checksum accessible.
    self.address = self[:self.LEN] # type: TryteString

    self.balance = None # type: Optional[int]
    """
    Balance owned by this address.
    Must be set manually via the ``getInputs`` command.

    References:
      - :py:class:`iota.commands.extended.get_inputs`
      - :py:meth:`ProposedBundle.add_inputs`
    """

  def is_checksum_valid(self):
    # type: () -> bool
    """
    Returns whether this address has a valid checksum.
    """
    if self.checksum:
      return self.checksum == self._generate_checksum()

    return False

  def with_valid_checksum(self):
    # type: () -> Address
    """
    Returns the address with a valid checksum attached.
    """
    return Address(self.address + self._generate_checksum())

  def _generate_checksum(self):
    # type: () -> TryteString
    """
    Generates the correct checksum for this address.
    """
    checksum_trits = [] # type: MutableSequence[int]

    sponge = Curl()
    sponge.absorb(self.address.as_trits())
    sponge.squeeze(checksum_trits)

    # Multiply by 3 to convert trytes into trits.
    checksum_length = (AddressChecksum.LEN * 3)

    return TryteString.from_trits(checksum_trits[:checksum_length])


class AddressChecksum(TryteString):
  """
  A TryteString that acts as an address checksum.
  """
  LEN = 9

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(AddressChecksum, self).__init__(trytes, pad=None)

    if len(self._trytes) != self.LEN:
      raise with_context(
        exc = ValueError(
          '{cls} values must be exactly {len} trytes long.'.format(
            cls = type(self).__name__,
            len = self.LEN,
          ),
        ),

        context = {
          'trytes': trytes,
        },
      )


class BundleHash(Hash):
  """
  A TryteString that acts as a bundle hash.
  """
  pass


class Tag(TryteString):
  """
  A TryteString that acts as a transaction tag.
  """
  LEN = 27

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(Tag, self).__init__(trytes, pad=self.LEN)

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


class TransactionHash(Hash):
  """
  A TryteString that acts as a transaction hash.
  """
  pass


class ProposedTransaction(object):
  """
  A transaction that has not yet been attached to the Tangle.

  Provide to :py:meth:`iota.api.Iota.prepare_transfers` to attach to
  tangle and publish/store.
  """
  MESSAGE_LEN = 2187
  """
  Max number of trytes allowed in a transaction message.

  If a transaction's message is longer than this, it will be split into
  multiple transactions automatically when it is added to a bundle.

  See :py:meth:`ProposedBundle.add_transaction` for more info.
  """

  def __init__(self, address, value, tag=None, message=None, timestamp=None):
    # type: (Address, int, Optional[Tag], Optional[TrytesCompatible], Optional[int]) -> None
    super(ProposedTransaction, self).__init__()

    # See :py:class:`Transaction` for descriptions of these attributes.
    self.address  = address
    self.message  = TryteString(message or b'', pad=2187)
    self.tag      = Tag(tag or b'')
    self.value    = value

    # Python 3.3 introduced a :py:meth:`datetime.timestamp` method,
    # but for compatibility with Python 2, we have to do this the
    # old-fashioned way.
    # :see: http://stackoverflow.com/q/2775864/
    self.timestamp = timestamp or unix_timestamp(datetime.utcnow().timetuple())

    # These attributes are set by :py:meth:`ProposedBundle.finalize`.
    self.current_index              = None # type: Optional[int]
    self.last_index                 = None # type: Optional[int]
    self.trunk_transaction_hash     = None # type: Optional[TransactionHash]
    self.branch_transaction_hash    = None # type: Optional[TransactionHash]
    self.signature_message_fragment = None # type: Optional[TryteString]
    self.nonce                      = None # type: Optional[Hash]

  @property
  def timestamp_trits(self):
    # type: () -> List[int]
    """
    Returns the ``timestamp`` attribute expressed as trits.
    """
    return trits_from_int(self.timestamp, pad=27)

  @property
  def value_trits(self):
    # type: () -> List[int]
    """
    Returns the ``value`` attribute expressed as trits.
    """
    return trits_from_int(self.value, pad=81)

  @property
  def current_index_trits(self):
    # type: () -> List[int]
    """
    Returns the ``current_index`` attribute expressed as trits.
    """
    return trits_from_int(self.current_index, pad=27)

  @property
  def last_index_trits(self):
    # type: () -> List[int]
    """
    Returns the ``last_index`` attribute expressed as trits.
    """
    return trits_from_int(self.last_index, pad=27)


class ProposedBundle(object):
  """
  A collection of proposed transactions, to be treated as an atomic
  unit when attached to the Tangle.

  Conceptually, a bundle is similar to a block in a blockchain.
  """
  def __init__(self, transactions=None):
    # type: (Optional[Iterable[ProposedTransaction]]) -> None
    super(ProposedBundle, self).__init__()

    self.hash = None # type: Optional[Hash]
    self.tag  = None # type: Optional[Tag]

    self.transactions = [] # type: List[ProposedTransaction]

    if transactions:
      for t in transactions:
        self.add_transaction(t)

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
    return sum(t.value for t in self.transactions)

  def __len__(self):
    # type: () -> int
    """
    Returns te number of transactions in the bundle.
    """
    return len(self.transactions)

  def __iter__(self):
    # type: () -> Generator[ProposedTransaction]
    """
    Iterates over transactions in the bundle.
    """
    return iter(self.transactions)

  def add_transaction(self, transaction):
    # type: (ProposedTransaction) -> None
    """
    Adds a transaction to the bundle.

    If the transaction message is too long, it will be split
    automatically into multiple transactions.
    """
    if self.hash:
      raise RuntimeError('Bundle is already finalized.')

    self.transactions.append(ProposedTransaction(
      address   = transaction.address,
      value     = transaction.value,
      tag       = transaction.tag,
      message   = transaction.message[:ProposedTransaction.MESSAGE_LEN],
      timestamp = transaction.timestamp,
    ))

    # Last-added transaction determines the bundle tag.
    self.tag = transaction.tag or self.tag

    # If the message is too long to fit in a single transactions,
    # it must be split up into multiple transactions so that it will
    # fit.
    fragment = transaction.message[ProposedTransaction.MESSAGE_LEN:]
    while fragment:
      self.transactions.append(ProposedTransaction(
        address   = transaction.address,
        value     = 0,
        tag       = transaction.tag,
        message   = fragment[:ProposedTransaction.MESSAGE_LEN],
        timestamp = transaction.timestamp,
      ))

      fragment = fragment[ProposedTransaction.MESSAGE_LEN:]

  def add_inputs(self, inputs):
    # type: (Iterable[Address]) -> None
    """
    Adds inputs to spend in the bundle.

    :param inputs:
      Addresses to use as the inputs for this bundle.

      IMPORTANT: Must have ``balance`` attribute set!
      Use :py:meth:`iota.api.get_inputs` to load inputs with balances.
    """
    if self.hash:
      raise RuntimeError('Bundle is already finalized.')

    for i in inputs:
      # Add the input as a transaction.
      self.add_transaction(ProposedTransaction(
        address = i,
        value   = -i.balance,
        tag     = self.tag,
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

    # Negative balance means that there are unspent inputs.
    # See :py:meth:`balance` for more info.
    unspent_inputs = -self.balance

    if unspent_inputs > 0:
      self.add_transaction(ProposedTransaction(
        address = address,
        value   = unspent_inputs,
        tag     = self.tag,
      ))

  def finalize(self):
    # type: () -> None
    """
    Finalizes the bundle, preparing it to be attached to the Tangle.
    """
    if self.hash:
      raise RuntimeError('Bundle is already finalized.')

    balance = self.balance
    if balance > 0:
      raise ValueError(
        'Inputs are insufficient to cover bundle spend '
        '(balance: {balance}).'.format(
          balance = balance,
        ),
      )
    elif balance < 0:
      raise ValueError(
        'Bundle has unspent inputs (balance: {balance}).'.format(
          balance = balance,
        ),
      )

    sponge      = Curl()
    last_index  = len(self) - 1

    for (i, t) in enumerate(self): # type: Tuple[int, ProposedTransaction]
      t.current_index = i
      t.last_index    = last_index

      sponge.absorb(
          # Ensure checksum is not included.
          t.address.address.as_trits()
        + t.value_trits
        + t.tag.as_trits()
        + t.timestamp_trits
        + t.current_index_trits
        + t.last_index_trits
      )

    bundle_hash = [0] * HASH_LENGTH # type: MutableSequence[int]
    sponge.squeeze(bundle_hash)
    self.hash = Hash.from_trits(bundle_hash)

    for t in self:
      t.bundle_hash = self.hash


class Transaction(object):
  """
  A transaction that has been attached to the Tangle.
  """
  @classmethod
  def from_tryte_string(cls, trytes):
    # type: (TrytesCompatible) -> Transaction
    """
    Creates a Transaction object from a sequence of trytes.
    """
    tryte_string = TryteString(trytes)

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
      bundle_id = BundleHash(tryte_string[2349:2430]),
      trunk_transaction_id = TransactionHash(tryte_string[2430:2511]),
      branch_transaction_id = TransactionHash(tryte_string[2511:2592]),
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
      bundle_id,
      trunk_transaction_id,
      branch_transaction_id,
      nonce,
  ):
    # type: (Hash, TryteString, Address, int, Tag, int, int, int, Hash, TransactionHash, TransactionHash, Hash) -> None
    self.hash = hash_
    """
    Transaction ID, generated by taking a hash of the transaction
    trits.
    """

    self.bundle_id = bundle_id
    """
    Bundle ID, generated by taking a hash of all the transactions in
    the bundle.
    """

    self.address = address
    """
    The address associated with this transaction.
    If ``value`` is != 0, the associated address' balance is adjusted
    as a result of this transaction.
    """

    self.value = value
    """
    Amount to adjust the balance of ``address``.
    Can be negative (i.e., for spending inputs).
    """

    self.tag = tag
    """
    Optional classification tag applied to this transaction.
    """

    self.nonce = nonce
    """
    Unique value used to increase security of the transaction hash.
    """

    self.timestamp = timestamp
    """
    Timestamp used to increase the security of the transaction hash.

    IMPORTANT: This value is easy to forge!
    Do not rely on it when resolving conflicts!
    """

    self.current_index = current_index
    """
    The position of the transaction inside the bundle.

    For value transfers, the "spend" transaction is generally in the
    0th position, followed by inputs, and the "change" transaction is
    last.
    """

    self.last_index = last_index
    """
    The position of the final transaction inside the bundle.
    """

    self.branch_transaction_id  = branch_transaction_id
    self.trunk_transaction_id   = trunk_transaction_id

    self.signature_message_fragment =\
      TryteString(signature_message_fragment or b'')

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

  def as_tryte_string(self):
    # type: () -> TryteString
    """
    Returns a TryteString representation of the transaction.
    """
    return (
        self.signature_message_fragment
      + self.address
      + TryteString.from_trits(trits_from_int(self.value, pad=81))
      + self.tag
      + TryteString.from_trits(trits_from_int(self.timestamp, pad=27))
      + TryteString.from_trits(trits_from_int(self.current_index, pad=27))
      + TryteString.from_trits(trits_from_int(self.last_index, pad=27))
      + self.bundle_id
      + self.trunk_transaction_id
      + self.branch_transaction_id
      + self.nonce
    )
