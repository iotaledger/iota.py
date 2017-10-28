# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from codecs import decode, encode
from itertools import chain
from math import ceil
from random import SystemRandom
from typing import Any, AnyStr, Generator, Iterable, Iterator, List, \
  MutableSequence, Optional, Text, Union

from six import PY2, binary_type, itervalues, python_2_unicode_compatible, \
  text_type

from iota import AsciiTrytesCodec, TRITS_PER_TRYTE
from iota.crypto import HASH_LENGTH
from iota.crypto.kerl import Kerl
from iota.exceptions import with_context
from iota.json import JsonSerializable
from iota.trits import int_from_trits, trits_from_int

__all__ = [
  'Address',
  'AddressChecksum',
  'Hash',
  'Tag',
  'TryteString',
  'TrytesCompatible',
]


# Custom types for type hints and docstrings.
TrytesCompatible = Union[AnyStr, bytearray, 'TryteString']


@python_2_unicode_compatible
class TryteString(JsonSerializable):
  """
  A string representation of a sequence of trytes.

  A tryte string is similar in concept to Python's byte string, except
  it has a more limited alphabet.  Byte strings are limited to ASCII
  (256 possible values), while the tryte string alphabet only has 27
  characters (one for each possible tryte configuration).

  IMPORTANT: A TryteString does not represent a numeric value!
  """
  @classmethod
  def random(cls, length):
    # type: (int) -> TryteString
    """
    Generates a random sequence of trytes.

    :param length:
      Number of trytes to generate.
    """
    alphabet  = list(itervalues(AsciiTrytesCodec.alphabet))
    generator = SystemRandom()

    # :py:meth:`SystemRandom.choices` wasn't added until Python 3.6;
    # for compatibility, we will continue to use ``choice`` in a loop.
    # https://docs.python.org/3/library/random.html#random.choices
    return cls(
      ''.join(chr(generator.choice(alphabet)) for _ in range(length))
        .encode('ascii')
    )

  @classmethod
  def from_bytes(cls, bytes_, codec=AsciiTrytesCodec.name, *args, **kwargs):
    # type: (Union[binary_type, bytearray], Text, *Any, **Any) -> TryteString
    """
    Creates a TryteString from a sequence of bytes.

    :param bytes_:
      Source bytes.

    :param codec:
      Which codec to use:

        - 'binary': Converts each byte into a sequence of trits with
          the same value (this is usually what you want).
        - 'ascii': Uses the legacy ASCII codec.

    :param args:
      Additional positional arguments to pass to the initializer.

    :param kwargs:
      Additional keyword arguments to pass to the initializer.
    """
    return cls(encode(bytes_, codec), *args, **kwargs)

  @classmethod
  def from_string(cls, string, *args, **kwargs):
    # type: (Text, *Any, **Any) -> TryteString
    """
    Creates a TryteString from a Unicode string.

    :param string:
      Source string.

    :param args:
      Additional positional arguments to pass to the initializer.

    :param kwargs:
      Additional keyword arguments to pass to the initializer.
    """
    return cls.from_bytes(
      bytes_  = string.encode('utf-8'),
      codec   = AsciiTrytesCodec.name,
      *args,
      **kwargs
    )

  @classmethod
  def from_trytes(cls, trytes, *args, **kwargs):
    # type: (Iterable[Iterable[int]], *Any, **Any) -> TryteString
    """
    Creates a TryteString from a sequence of trytes.

    :param trytes:
      Iterable of tryte values.
      In this context, a tryte is defined as a list containing 3 trits.

    :param args:
      Additional positional arguments to pass to the initializer.

    :param kwargs:
      Additional keyword arguments to pass to the initializer.

    References:
      - :py:meth:`as_trytes`
    """
    chars = bytearray()

    for t in trytes:
      converted = int_from_trits(t)

      # :py:meth:`_tryte_from_int`
      if converted < 0:
        converted += 27

      chars.append(AsciiTrytesCodec.alphabet[converted])

    return cls(chars, *args, **kwargs)

  @classmethod
  def from_trits(cls, trits, *args, **kwargs):
    # type: (Iterable[int], *Any, **Any) -> TryteString
    """
    Creates a TryteString from a sequence of trits.

    :param trits:
      Iterable of trit values (-1, 0, 1).

    :param args:
      Additional positional arguments to pass to the initializer.

    :param kwargs:
      Additional keyword arguments to pass to the initializer.

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
      (trits[i:i+3] for i in range(0, len(trits), 3)),

      *args,
      **kwargs
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
      if isinstance(trytes, text_type):
        trytes = trytes.encode('ascii')

      if not isinstance(trytes, bytearray):
        trytes = bytearray(trytes)

      for i, ordinal in enumerate(trytes):
        if ordinal not in AsciiTrytesCodec.index:
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

  def __hash__(self):
    # type: () -> int
    return hash(binary_type(self._trytes))

  def __repr__(self):
    # type: () -> Text
    return '{cls}({trytes!r})'.format(
      cls     = type(self).__name__,
      trytes  = binary_type(self._trytes),
    )

  def __bytes__(self):
    """
    Converts the TryteString into an ASCII representation.

    Note: This does not decode the trytes into bytes/characters; it
    only returns an ASCII representation of the trytes themselves!

    If you want to...
    - ... decode trytes into bytes: use :py:meth:`as_bytes`.
    - ... decode trytes into Unicode: use :py:meth:`as_string`.
    """
    return binary_type(self._trytes)

  def __str__(self):
    """
    Same as :py:meth:`__bytes__`, except this method returns a unicode
    string.
    """
    # This causes infinite recursion in Python 2.
    # return binary_type(self).decode('ascii')
    return binary_type(self._trytes).decode('ascii')

  def __bool__(self):
    # type: () -> bool
    return bool(self._trytes) and any(t != b'9' for t in self)

  if PY2:
    # Magic methods have different names in Python 2.
    __nonzero__ = __bool__

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
    elif isinstance(other, text_type):
      return other.encode('ascii') in self._trytes
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

  def __setitem__(self, item, trytes):
    # type: (Union[int, slice], TrytesCompatible) -> None
    new_trytes = TryteString(trytes)

    if isinstance(item, slice):
      self._trytes[item] = new_trytes._trytes
    elif len(new_trytes) > 1:
      raise with_context(
        exc = ValueError(
          'Cannot assign multiple trytes to the same index '
          '(``exc.context`` has more info).'
        ),

        context = {
          'self':       self,
          'index':      item,
          'new_trytes': new_trytes,
        },
      )
    else:
      self._trytes[item] = new_trytes._trytes[0]

  def __add__(self, other):
    # type: (TrytesCompatible) -> TryteString
    if isinstance(other, TryteString):
      return TryteString(self._trytes + other._trytes)
    elif isinstance(other, text_type):
      return TryteString(self._trytes + other.encode('ascii'))
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
    elif isinstance(other, text_type):
      return self._trytes == other.encode('ascii')
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

  def count_chunks(self, chunk_size):
    # type: (int) -> int
    """
    Returns the number of constant-size chunks the TryteString can be
    divided into (rounded up).

    :param chunk_size:
      Number of trytes per chunk.
    """
    return len(self.iter_chunks(chunk_size))

  def iter_chunks(self, chunk_size):
    # type: (int) -> ChunkIterator
    """
    Iterates over the TryteString, in chunks of constant size.

    :param chunk_size:
      Number of trytes per chunk.
      The final chunk will be padded if it is too short.
    """
    return ChunkIterator(self, chunk_size)

  def as_bytes(self, errors='strict', codec=AsciiTrytesCodec.name):
    # type: (Text, Text) -> binary_type
    """
    Converts the TryteString into a byte string.

    :param errors:
      How to handle trytes that can't be converted:
        - 'strict':   raise an exception (recommended).
        - 'replace':  replace with '?'.
        - 'ignore':   omit the tryte from the result.

    :param codec:
      Which codec to use:

      - 'binary': Converts each sequence of 5 trits into a byte with
        the same value (this is usually what you want).
      - 'ascii': Uses the legacy ASCII codec.

    :raise:
      - :py:class:`iota.codecs.TrytesDecodeError` if the trytes cannot
        be decoded into bytes.
    """
    # In Python 2, :py:func:`decode` does not accept keyword arguments.
    return decode(self._trytes, codec, errors)

  def as_string(self, errors='strict', strip_padding=True):
    # type: (Text, bool) -> Text
    """
    Attempts to interpret the TryteString as a UTF-8 encoded Unicode
    string.

    :param errors:
      How to handle trytes that can't be converted, or bytes that can't
      be decoded using UTF-8:
        - 'strict':   raise an exception (recommended).
        - 'replace':  replace with a placeholder character.
        - 'ignore':   omit the invalid tryte/byte sequence.

    :param strip_padding:
      Whether to strip trailing null trytes before converting.

    :raise:
      - :py:class:`iota.codecs.TrytesDecodeError` if the trytes cannot
        be decoded into bytes.
      - :py:class:`UnicodeDecodeError` if the resulting bytes cannot be
        decoded using UTF-8.
    """
    trytes = self._trytes
    if strip_padding and (trytes[-1] == ord(b'9')):
      trytes = trytes.rstrip(b'9')

      # Put one back to preserve even length for ASCII codec.
      trytes += b'9' * (len(trytes) % 2)

    return decode(trytes, AsciiTrytesCodec.name, errors).decode('utf-8', errors)

  def as_json_compatible(self):
    # type: () -> Text
    """
    Returns a JSON-compatible representation of the object.

    References:
      - :py:class:`iota.json.JsonEncoder`.
    """
    return self._trytes.decode('ascii')

  def as_integers(self):
    # type: () -> List[int]
    """
    Converts the TryteString into a sequence of integers.

    Each integer is a value between -13 and 13.
    """
    return [
      self._normalize(AsciiTrytesCodec.index[c])
        for c in self._trytes
    ]

  def as_trytes(self):
    # type: () -> List[List[int]]
    """
    Converts the TryteString into a sequence of trytes.

    Each tryte is represented as a list with 3 trit values.

    See :py:meth:`as_trits` for more info.

    IMPORTANT: TryteString is not a numeric type, so the result of this
    method should not be interpreted as an integer!
    """
    return [
      trits_from_int(n, pad=3)
        for n in self.as_integers()
    ]

  def as_trits(self):
    # type: () -> List[int]
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

  def _repr_pretty_(self, p, cycle):
    """
    Makes JSON-serializable objects play nice with IPython's default
    pretty-printer.

    Sadly, :py:func:`pprint.pprint` does not have a similar mechanism.

    References:
      - http://ipython.readthedocs.io/en/stable/api/generated/IPython.lib.pretty.html
      - :py:meth:`IPython.lib.pretty.RepresentationPrinter.pretty`
      - :py:func:`pprint._safe_repr`
    """
    return p.text(repr(self))

  @staticmethod
  def _normalize(n):
    # type: (int) -> int
    if n > 26:
      raise ValueError('{n} cannot be represented by a single tryte.'.format(
        n = n,
      ))

    # For values greater than 13, trigger an overflow.
    # E.g., 14 => -13, 15 => -12, etc.
    return (n - 27) if n > 13 else n


class ChunkIterator(Iterator[TryteString]):
  """
  Iterates over a TryteString, in chunks of constant size.
  """
  def __init__(self, trytes, chunk_size):
    # type: (TryteString, int) -> None
    """
    :param trytes:
      TryteString to iterate over.

    :param chunk_size:
      Number of trytes per chunk.
      The final chunk will be padded if it is too short.
    """
    super(ChunkIterator, self).__init__()

    self.trytes     = trytes
    self.chunk_size = chunk_size

    self._offset = 0

  def __iter__(self):
    # type: () -> ChunkIterator
    return self

  def __len__(self):
    # type: () -> int
    """
    Returns how many chunks this iterator will return.

    Note: This method always returns the same result, no matter how
    many iterations have been completed.
    """
    return int(ceil(len(self.trytes) / self.chunk_size))

  def __next__(self):
    # type: () -> TryteString
    """
    Returns the next chunk in the iterator.

    :raise:
      - :py:class:`StopIteration` if there are no more chunks
        available.
    """
    if self._offset >= len(self.trytes):
      raise StopIteration

    chunk = self.trytes[self._offset:self._offset+self.chunk_size]
    chunk += b'9' * max(0, self.chunk_size - len(chunk))

    self._offset += self.chunk_size

    return chunk

  if PY2:
    # In Python 2, iterator methods are named a little differently.
    next = __next__


class Hash(TryteString):
  """
  A TryteString that is exactly one hash long.
  """
  # Divide by 3 to convert trits to trytes.
  LEN = HASH_LENGTH // TRITS_PER_TRYTE

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

  def __init__(self, trytes, balance=None, key_index=None, security_level=None):
    # type: (TrytesCompatible, Optional[int], Optional[int], Optional[int]) -> None
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

    self.balance = balance
    """
    Balance owned by this address.
    Must be set manually via the ``getInputs`` command.

    References:
      - :py:class:`iota.commands.extended.get_inputs`
      - :py:meth:`ProposedBundle.add_inputs`
    """

    self.key_index = key_index
    """
    Index of the key used to generate this address.
    Must be set manually via ``AddressGenerator``.

    References:
      - :py:class:`iota.crypto.addresses.AddressGenerator`
    """

    self.security_level = security_level
    """
    Number of hashes in the digest that was used to generate this
    address.
    """

  def as_json_compatible(self):
    # type: () -> dict
    return {
      'trytes':         self._trytes.decode('ascii'),
      'balance':        self.balance,
      'key_index':      self.key_index,
      'security_level': self.security_level,
    }

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
    return Address(
      trytes = self.address + self._generate_checksum(),

      # Make sure to copy all of the ancillary attributes, too!
      balance         = self.balance,
      key_index       = self.key_index,
      security_level  = self.security_level,
    )

  def _generate_checksum(self):
    # type: () -> TryteString
    """
    Generates the correct checksum for this address.
    """
    checksum_trits = [] # type: MutableSequence[int]

    sponge = Kerl()
    sponge.absorb(self.address.as_trits())
    sponge.squeeze(checksum_trits)

    checksum_length = AddressChecksum.LEN * TRITS_PER_TRYTE

    return TryteString.from_trits(checksum_trits[-checksum_length:])


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
