
from codecs import decode, encode
from itertools import chain
from math import ceil
from random import SystemRandom
from typing import Any, AnyStr, Generator, Iterable, Iterator, List, \
    MutableSequence, Optional, Type, TypeVar, Union, Dict
from warnings import warn

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
    'TrytesCompatible',
    'TryteString',
]

# Custom types for type hints and docstrings.
TrytesCompatible = Union[AnyStr, bytearray, 'TryteString']

T = TypeVar('T', bound='TryteString')


class TryteString(JsonSerializable):
    """
    A string representation of a sequence of trytes.

    A :py:class:`TryteString` is an ASCII representation of a sequence of trytes.
    In many respects, it is similar to a Python ``bytes`` object (which is an
    ASCII representation of a sequence of bytes).

    In fact, the two objects behave very similarly; they support
    concatenation, comparison, can be used as dict keys, etc.

    However, unlike ``bytes``, a :py:class:`TryteString` can only contain
    uppercase letters and the number 9 (as a regular expression: ``^[A-Z9]*$``).

    .. important::
        A TryteString does not represent a numeric value!

    :param TrytesCompatible trytes:
        Byte string or bytearray.

    :param Optional[int] pad:
        Ensure at least this many trytes.

        If there are too few, null trytes will be appended to the
        TryteString.

        .. note::
            If the TryteString is too long, it will *not* be
            truncated!
    """

    @classmethod
    def random(cls: Type[T], length: Optional[int] = None) -> T:
        """
        Generates a random sequence of trytes.

        :param Optional[int] length:
            Number of trytes to generate.

        :return:
            :py:class:`TryteString` object.

        :raises TypeError:
            - if ``length`` is negative,
            - if ``length`` is not defined, and the class doesn't have ``LEN`` attribute.
        """
        alphabet = [chr(x) for x in AsciiTrytesCodec.alphabet.values()]
        generator = SystemRandom()
        try:
            if length is None:
                length = cls.LEN

            if length <= 0:
                raise TypeError("length parameter needs to be greater than zero")
        except AttributeError:  # class has no LEN attribute
            if length is None:
                raise TypeError("{class_name} does not define a length property".format(class_name=cls.__name__))

        return cls(
            ''.join(
                generator.choices(population=alphabet, k=length)
            ).encode('ascii')
        )

    @classmethod
    def from_bytes(cls: Type[T],
                   bytes_: Union[bytes, bytearray],
                   codec: str = AsciiTrytesCodec.name,
                   *args: Any,
                   **kwargs: Any) -> T:
        """
        Creates a TryteString from a sequence of bytes.

        :param  Union[bytes,bytearray] bytes\_:
            Source bytes. ASCII representation of a sequence of bytes.
            Note that only tryte alphabet supported!

        :param str codec:
            Reserved for future use.
            Currently supports only the 'trytes_ascii' codec.
            See https://github.com/iotaledger/iota.py/issues/62 for
            more information.

        :param args:
            Additional positional arguments to pass to the initializer.

        :param kwargs:
            Additional keyword arguments to pass to the initializer.

        :return:
            :py:class:`TryteString` object.

        Example usage::

            from iota import TryteString
            message_trytes = TryteString.from_bytes(b'HELLO999IOTA')

        """
        return cls(encode(bytes_, codec), *args, **kwargs)

    @classmethod
    def from_unicode(cls: Type[T],
                     string: str,
                     *args: Any,
                     **kwargs: Any) -> T:
        """
        Creates a TryteString from a Unicode string.

        :param str string:
            Source Unicode string.

        :param args:
            Additional positional arguments to pass to the initializer.

        :param kwargs:
            Additional keyword arguments to pass to the initializer.

        :return:
            :py:class:`TryteString` object.

        Example usage::

            from iota import TryteString
            message_trytes = TryteString.from_unicode('Hello, IOTA!')

        """
        return cls.from_bytes(
            bytes_=string.encode('utf-8'),
            codec=AsciiTrytesCodec.name,
            *args,
            **kwargs
        )

    @classmethod
    def from_string(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """
        Deprecated; use :py:meth:`from_unicode` instead.

        https://github.com/iotaledger/iota.py/issues/90
        """
        warn(
            category=DeprecationWarning,

            message=(
                '`from_string()` is deprecated; use `from_unicode()` instead.'
            ),
        )
        return cls.from_unicode(*args, **kwargs)

    @classmethod
    def from_trytes(cls: Type[T],
                    trytes: Iterable[Iterable[int]],
                    *args: Any,
                    **kwargs: Any) -> T:
        """
        Creates a TryteString from a sequence of trytes.

        :param Iterable[Iterable[int]] trytes:
            Iterable of tryte values.

            In this context, a tryte is defined as a list containing 3
            trits.

        :param args:
            Additional positional arguments to pass to the initializer.

        :param kwargs:
            Additional keyword arguments to pass to the initializer.

        :return:
            :py:class:`TryteString` object.

        Example usage::

            from iota import TryteString
            message_trytes = TryteString.from_trytes(
                [
                    [1, 0, -1],
                    [-1, 1, 0],
                    [1, -1, 0],
                    [-1, 1, 0],
                    [0, 1, 0],
                    [0, 1, 0],
                    [-1, 1, 1],
                    [-1, 1, 0],
                ]
            )

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
    def from_trits(cls: Type[T],
                   trits: Iterable[int],
                   *args: Any,
                   **kwargs: Any) -> T:
        """
        Creates a TryteString from a sequence of trits.

        :param Iterable[int] trits:
            Iterable of trit values (-1, 0, 1).

        :param args:
            Additional positional arguments to pass to the initializer.

        :param kwargs:
            Additional keyword arguments to pass to the initializer.

        :return:
            :py:class:`TryteString` object.

        Example usage::

            from iota import TryteString
            message_trytes = TryteString.from_trits(
                [1, 0, -1, -1, 1, 0, 1, -1, 0, -1, 1, 0, 0, 1, 0, 0, 1, 0, -1, 1, 1, -1, 1, 0]
            )

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
            # http://stackoverflow.com/a/1751478/
            (trits[i:i + 3] for i in range(0, len(trits), 3)),

            *args,
            **kwargs
        )

    def __init__(self, trytes: TrytesCompatible, pad: Optional[int] = None) -> None:
        """
        :param TrytesCompatible trytes:
            Byte string or bytearray.

        :param Optional[int] pad:
            Ensure at least this many trytes.

            If there are too few, null trytes will be appended to the
            TryteString.

            .. note::
                If the TryteString is too long, it will *not* be
                truncated!
        """
        super(TryteString, self).__init__()

        if isinstance(trytes, (int, float)):
            raise with_context(
                exc=TypeError(
                    'Converting {type} is not supported; '
                    '{cls} is not a numeric type.'.format(
                        type=type(trytes).__name__,
                        cls=type(self).__name__,
                    ),
                ),

                context={
                    'trytes': trytes,
                },
            )

        if isinstance(trytes, TryteString):
            incoming_type = type(trytes)

            if (
                    (incoming_type is TryteString) or
                    issubclass(incoming_type, type(self))
            ):
                # Create a copy of the incoming TryteString's trytes, to
                # ensure we don't modify it when we apply padding.
                trytes = bytearray(trytes._trytes)

            else:
                raise with_context(
                    exc=TypeError(
                        '{cls} cannot be initialized from a(n) {type}.'.format(
                            type=type(trytes).__name__,
                            cls=type(self).__name__,
                        ),
                    ),

                    context={
                        'trytes': trytes,
                    },
                )

        else:
            if isinstance(trytes, str):
                trytes = encode(trytes, 'ascii')

            if not isinstance(trytes, bytearray):
                trytes = bytearray(trytes)

            for i, ordinal in enumerate(trytes):
                if ordinal not in AsciiTrytesCodec.index:
                    raise with_context(
                        exc=ValueError(
                            'Invalid character {char!r} at position {i} '
                            '(expected A-Z or 9).'.format(
                                char=chr(ordinal),
                                i=i,
                            ),
                        ),

                        context={
                            'trytes': trytes,
                        },
                    )

        if pad:
            trytes += b'9' * max(0, pad - len(trytes))

        self._trytes: bytearray = trytes

    def __hash__(self) -> int:
        return hash(bytes(self._trytes))

    def __repr__(self) -> str:
        return '{cls}({trytes!r})'.format(
            cls=type(self).__name__,
            trytes=bytes(self._trytes),
        )

    def __bytes__(self) -> bytes:
        """
        Converts the TryteString into an ASCII representation.

        .. note::
            This does not decode the trytes into bytes/characters; it
            only returns an ASCII representation of the trytes
            themselves!

        If you want to...

        - ... encode trytes into bytes: use :py:meth:`encode`.
        - ... decode trytes into Unicode: use :py:meth:`decode`.
        """
        return bytes(self._trytes)

    def __str__(self) -> str:
        """
        Same as :py:meth:`__bytes__`, except this method returns a
        unicode string.
        """
        # This causes infinite recursion in Python 2.
        # return binary_type(self).decode('ascii')

        return bytes(self._trytes).decode('ascii')

    def __bool__(self) -> bool:
        return bool(self._trytes) and any(t != b'9' for t in self)

    def __len__(self) -> int:
        return len(self._trytes)

    def __iter__(self) -> Generator[bytes, None, None]:
        # :see: http://stackoverflow.com/a/14267935/
        return (bytes(self._trytes[i:i + 1]) for i in range(len(self)))

    def __contains__(self, other: TrytesCompatible) -> bool:
        if isinstance(other, TryteString):
            return other._trytes in self._trytes
        elif isinstance(other, str):
            return other.encode('ascii') in self._trytes
        elif isinstance(other, (bytes, bytearray)):
            return other in self._trytes
        else:
            raise with_context(
                exc=TypeError(
                    'Invalid type for TryteString contains check '
                    '(expected Union[TryteString, {bytes}, bytearray], '
                    'actual {type}).'.format(
                        bytes=bytes.__name__,
                        type=type(other).__name__,
                    ),
                ),

                context={
                    'other': other,
                },
            )

    def __getitem__(self, item: Union[int, slice]) -> T:
        new_trytes = bytearray()

        sliced = self._trytes[item]

        if isinstance(sliced, int):
            new_trytes.append(sliced)
        else:
            new_trytes.extend(sliced)

        return TryteString(new_trytes)

    def __setitem__(self,
                    item: Union[int, slice],
                    trytes: TrytesCompatible) -> None:
        new_trytes = TryteString(trytes)

        if isinstance(item, slice):
            self._trytes[item] = new_trytes._trytes
        elif len(new_trytes) > 1:
            raise with_context(
                exc=ValueError(
                    'Cannot assign multiple trytes to the same index '
                    '(``exc.context`` has more info).'
                ),

                context={
                    'self': self,
                    'index': item,
                    'new_trytes': new_trytes,
                },
            )
        else:
            self._trytes[item] = new_trytes._trytes[0]

    def __add__(self, other: TrytesCompatible) -> T:
        if isinstance(other, TryteString):
            return TryteString(self._trytes + other._trytes)
        elif isinstance(other, str):
            return TryteString(self._trytes + other.encode('ascii'))
        elif isinstance(other, (bytes, bytearray)):
            return TryteString(self._trytes + other)
        else:
            raise with_context(
                exc=TypeError(
                    'Invalid type for TryteString concatenation '
                    '(expected Union[TryteString, {bytes}, bytearray], '
                    'actual {type}).'.format(
                        bytes=bytes.__name__,
                        type=type(other).__name__,
                    ),
                ),

                context={
                    'other': other,
                },
            )

    def __eq__(self, other: TrytesCompatible) -> bool:
        if isinstance(other, TryteString):
            return self._trytes == other._trytes
        elif isinstance(other, str):
            return self._trytes == other.encode('ascii')
        elif isinstance(other, (bytes, bytearray)):
            return self._trytes == other
        else:
            raise with_context(
                exc=TypeError(
                    'Invalid type for TryteString comparison '
                    '(expected Union[TryteString, {bytes}, bytearray], '
                    'actual {type}).'.format(
                        bytes=bytes.__name__,
                        type=type(other).__name__,
                    ),
                ),

                context={
                    'other': other,
                },
            )

    def count_chunks(self, chunk_size: int) -> int:
        """
        Returns the number of constant-size chunks the TryteString can
        be divided into (rounded up).

        :param chunk_size:
            Number of trytes per chunk.
        """
        return len(self.iter_chunks(chunk_size))

    # Declare forward reference as string until
    # https://www.python.org/dev/peps/pep-0563/
    def iter_chunks(self, chunk_size: int) -> 'ChunkIterator':
        """
        Iterates over the TryteString, in chunks of constant size.

        :param chunk_size:
            Number of trytes per chunk.

            The final chunk will be padded if it is too short.
        """
        return ChunkIterator(self, chunk_size)

    def encode(self,
               errors: str = 'strict',
               codec: str = AsciiTrytesCodec.name) -> bytes:
        """
        Encodes the TryteString into a lower-level primitive (usually
        bytes).

        :param str errors:
            How to handle trytes that can't be converted:

            'strict'
                raise an exception (recommended).

            'replace'
                replace with '?'.

            'ignore'
                omit the tryte from the result.

        :param str codec:
            Reserved for future use.

            See https://github.com/iotaledger/iota.py/issues/62 for
            more information.

        :raises:
            - :py:class:`iota.codecs.TrytesDecodeError` if the trytes
              cannot be decoded into bytes.

        :return:
            Python ``bytes`` object.

        Example usage::

            from iota import TryteString

            # Message payload as unicode string
            message = 'Hello, iota!'

            # Create TryteString
            message_trytes = TryteString.from_unicode(message)

            # Encode TryteString into bytes
            encoded_message_bytes = message_trytes.encode()

            # This will be b'Hello, iota'
            print(encoded_message_bytes)

            # Get the original message
            decoded = encoded_message_bytes.decode()

            print(decoded == message)

        """
        # Converting ASCII-encoded trytes into bytes is considered to be
        # a *decode* operation according to
        # :py:class:`AsciiTrytesCodec`.
        #
        # Once we add more codecs, we may need to revisit this.
        # See https://github.com/iotaledger/iota.py/issues/62 for
        # more information.
        return decode(self._trytes, codec, errors)

    def as_bytes(self, *args, **kwargs):
        """
        Deprecated; use :py:meth:`encode` instead.

        https://github.com/iotaledger/iota.py/issues/90
        """
        warn(
            category=DeprecationWarning,
            message='`as_bytes()` is deprecated; use `encode()` instead.',
        )
        return self.encode(*args, **kwargs)

    def decode(self, errors: str = 'strict',
               strip_padding: bool = True) -> str:
        """
        Decodes the TryteString into a higher-level abstraction (usually
        Unicode characters).

        :param str errors:
            How to handle trytes that can't be converted, or bytes that can't
            be decoded using UTF-8:

            'strict'
                raise an exception (recommended).

            'replace'
                replace with a placeholder character.

            'ignore'
                omit the invalid tryte/byte sequence.

        :param bool strip_padding:
            Whether to strip trailing null trytes before converting.

        :raises:
            - :py:class:`iota.codecs.TrytesDecodeError` if the trytes
              cannot be decoded into bytes.
            - :py:class:`UnicodeDecodeError` if the resulting bytes
              cannot be decoded using UTF-8.

        :return:
            ``Unicode string`` object.

        Example usage::

            from iota import TryteString

            trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

            message = trytes.decode()

        """
        trytes = self._trytes
        if strip_padding and (trytes[-1] == ord(b'9')):
            trytes = trytes.rstrip(b'9')

            # Put one back to preserve even length for ASCII codec.
            trytes += b'9' * (len(trytes) % 2)

        bytes_ = decode(trytes, AsciiTrytesCodec.name, errors)

        return bytes_.decode('utf-8', errors)

    def as_string(self, *args, **kwargs):
        """
        Deprecated; use :py:meth:`decode` instead.

        https://github.com/iotaledger/iota.py/issues/90
        """
        warn(
            category=DeprecationWarning,
            message='`as_string()` is deprecated; use `decode()` instead.',
        )
        return self.decode(*args, **kwargs)

    def as_json_compatible(self) -> str:
        """
        Returns a JSON-compatible representation of the object.

        References:

        - :py:class:`iota.json.JsonEncoder`.

        :return:
            JSON-compatible representation of the object (string).

        Example usage::

            from iota import TryteString

            trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

            json_payload = trytes.as_json_compatible()

        """
        return self._trytes.decode('ascii')

    def as_integers(self) -> List[int]:
        """
        Converts the TryteString into a sequence of integers.

        Each integer is a value between -13 and 13.

        See the
        `tryte alphabet <https://docs.iota.org/docs/getting-started/0.1/introduction/ternary>`_
        for more info.

        :return:
            ``List[int]``

        Example usage::

            from iota import TryteString

            trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

            tryte_ints = trytes.as_integers()

        """
        return [
            self._normalize(AsciiTrytesCodec.index[c])
            for c in self._trytes
        ]

    def as_trytes(self) -> List[List[int]]:
        """
        Converts the TryteString into a sequence of trytes.

        Each tryte is represented as a list with 3 trit values.

        See :py:meth:`as_trits` for more info.

        .. important::
            :py:class:`TryteString` is not a numeric type, so the result
            of this method should not be interpreted as an integer!

        :return:
            ``List[List[int]]``

        Example usage::

            from iota import TryteString

            trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

            tryte_list = trytes.as_trytes()

        """
        return [
            trits_from_int(n, pad=3)
            for n in self.as_integers()
        ]

    def as_trits(self) -> List[int]:
        """
        Converts the TryteString into a sequence of trit values.

        A trit may have value 1, 0, or -1.

        References:

        - https://en.wikipedia.org/wiki/Balanced_ternary

        .. important::
            :py:class:`TryteString` is not a numeric type, so the result
            of this method should not be interpreted as an integer!

        :return:
            ``List[int]``

        Example usage::

            from iota import TryteString

            trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

            trits = trytes.as_trits()

        """
        # http://stackoverflow.com/a/952952/5568265#comment4204394_952952
        return list(chain.from_iterable(self.as_trytes()))

    def _repr_pretty_(self, p, cycle):
        """
        Makes JSON-serializable objects play nice with IPython's default
        pretty-printer.

        Sadly, :py:func:`pprint.pprint` does not have a similar
        mechanism.

        References:

        - http://ipython.readthedocs.io/en/stable/api/generated/IPython.lib.pretty.html
        - :py:meth:`IPython.lib.pretty.RepresentationPrinter.pretty`
        - :py:func:`pprint._safe_repr`
        """
        return p.text(repr(self))

    @staticmethod
    def _normalize(n: int) -> int:
        if n > 26:
            raise ValueError(
                '{n} cannot be represented by a single tryte.'.format(
                    n=n,
                ))

        # For values greater than 13, trigger an overflow.
        # E.g., 14 => -13, 15 => -12, etc.
        return (n - 27) if n > 13 else n


class ChunkIterator(Iterator[TryteString]):
    """
    Iterates over a TryteString, in chunks of constant size.
    """

    def __init__(self, trytes: TryteString, chunk_size: int) -> None:
        """
        :param trytes:
            :py:class:`TryteString` to iterate over.

        :param chunk_size:
            Number of trytes per chunk.

            The final chunk will be padded if it is too short.
        """
        super(ChunkIterator, self).__init__()

        self.trytes = trytes
        self.chunk_size = chunk_size

        self._offset = 0

    # ChunkIterator class is not defined yet here, so we can't use
    # it as a type... Forward ref type annotation as available from PY3.7
    def __iter__(self) -> 'ChunkIterator':
        return self

    def __len__(self) -> int:
        """
        Returns how many chunks this iterator will return.

        .. note::
            This method always returns the same result, no matter how
            many iterations have been completed.
        """
        return int(ceil(len(self.trytes) / self.chunk_size))

    def __next__(self) -> TryteString:
        """
        Returns the next chunk in the iterator.

        :raises:
            - :py:class:`StopIteration` if there are no more chunks
              available.
        """
        if self._offset >= len(self.trytes):
            raise StopIteration

        chunk = self.trytes[self._offset:self._offset + self.chunk_size]
        chunk += b'9' * max(0, self.chunk_size - len(chunk))

        self._offset += self.chunk_size

        return chunk


class Hash(TryteString):
    """
    A :py:class:`TryteString` that is exactly one hash long.

    :param TrytesCompatible trytes:
        Object to construct the hash from.

    :raises ValueError: if ``trytes`` is longer than 81 trytes.

    """
    # Divide by 3 to convert trits to trytes.
    LEN = HASH_LENGTH // TRITS_PER_TRYTE
    """
    Length is always 81 trytes long.
    """

    def __init__(self, trytes: TrytesCompatible) -> None:
        super(Hash, self).__init__(trytes, pad=self.LEN)

        if len(self._trytes) > self.LEN:
            raise with_context(
                exc=ValueError('{cls} values must be {len} trytes long.'.format(
                    cls=type(self).__name__,
                    len=self.LEN
                )),

                context={
                    'trytes': trytes,
                },
            )


class Address(TryteString):
    """
    A :py:class:`TryteString` that acts as an address, with support for generating
    and validating checksums.

    :param TrytesCompatible trytes:
        Object to construct the address from.

    :param Optional[int] balance:
        Known balance of the address.

    :param Optional[int] key_index:
        Index of the address that was used during address generation.
        Must be greater than zero.

    :param Optional[int] security_level:
        Security level that was used during address generation.
        Might be 1, 2 or 3.

    :raises
        ValueError: if ``trytes`` is longer than 81 trytes, unless it is
        exactly 90 trytes long (address + checksum).
    """
    LEN = Hash.LEN
    """
    Length of an address.
    """

    def __init__(
            self,
            trytes: TrytesCompatible,
            balance: Optional[int] = None,
            key_index: Optional[int] = None,
            security_level: Optional[int] = None,) -> None:
        super(Address, self).__init__(trytes, pad=self.LEN)

        self.checksum = None
        if len(self._trytes) == (self.LEN + AddressChecksum.LEN):
            self.checksum: Optional[AddressChecksum] = AddressChecksum(
                self[self.LEN:]
            )

        elif len(self._trytes) > self.LEN:
            raise with_context(
                exc=ValueError(
                    'Address values must be '
                    '{len_no_checksum} trytes (no checksum), '
                    'or {len_with_checksum} trytes (with checksum).'.format(
                        len_no_checksum=self.LEN,
                        len_with_checksum=self.LEN + AddressChecksum.LEN,
                    ),
                ),

                context={
                    'trytes': trytes,
                },
            )

        # Make the address sans checksum accessible.
        self.address: TryteString = self[:self.LEN]
        """
        Address trytes without the checksum.
        """

        self.balance = balance
        """
        Balance owned by this address.
        Defaults to ``None``; usually set via the ``getInputs`` command.

        References:

        - :py:meth:`Iota.get_inputs`
        - :py:meth:`ProposedBundle.add_inputs`
        """

        self.key_index = key_index
        """
        Index of the key used to generate this address.
        Defaults to ``None``; usually set via :py:class:`AddressGenerator`.

        References:

        - :py:class:`iota.crypto.addresses.AddressGenerator`
        """

        self.security_level = security_level
        """
        Number of hashes in the digest that was used to generate this
        address.
        """

    def as_json_compatible(self) -> Dict[str, Union[str, int]]:
        """
        Returns a JSON-compatible representation of the Address.

        :return:
            ``dict`` with the following structure::

                {
                    'trytes': str,
                    'balance': int,
                    'key_index': int,
                    'security_level': int,
                }

        Example usage::

            from iota import Address

            # Example address only, do not use in your code!
            addy = Address(
                b'LVHHIXQNYKWQMGXGLFOKOCDFHPKXAUKWMSZVDRAT'
                b'TICUZXFACM9DNJELJGMLMK99KDVVOOWLINVBZIGWZ'
            )

            print(addy.as_json_compatible())

        """
        return {
            'trytes': self._trytes.decode('ascii'),
            'balance': self.balance,
            'key_index': self.key_index,
            'security_level': self.security_level,
        }

    def is_checksum_valid(self) -> bool:
        """
        Returns whether this address has a valid checksum.

        :return:
            ``bool``

        Example usage::

            from iota import Address

            # Example address only, do not use in your code!
            addy = Address(
                b'LVHHIXQNYKWQMGXGLFOKOCDFHPKXAUKWMSZVDRAT'
                b'TICUZXFACM9DNJELJGMLMK99KDVVOOWLINVBZIGWZ'
            )

            # Should be ``False``
            print(addy.is_checksum_valid())

            addy.add_checksum()

            # Should be ``True``
            print(addy.is_checksum_valid())

        """
        if self.checksum:
            return self.checksum == self._generate_checksum()

        return False

    def with_valid_checksum(self) -> 'Address':
        """
        Returns the address with a valid checksum attached.

        :return:
            :py:class:`Address` object.

        Example usage::

            from iota import Address

            # Example address only, do not use in your code!
            addy = Address(
                b'LVHHIXQNYKWQMGXGLFOKOCDFHPKXAUKWMSZVDRAT'
                b'TICUZXFACM9DNJELJGMLMK99KDVVOOWLINVBZIGWZ'
            )

            addy_with_checksum = addy.with_valid_checksum()

            print(addy_with_checksum)

            # Should be ``True``
            print(addy_with_checksum.is_checksum_valid())

        """
        return Address(
            trytes=self.address + self._generate_checksum(),

            # Make sure to copy all of the ancillary attributes, too!
            balance=self.balance,
            key_index=self.key_index,
            security_level=self.security_level,
        )

    def _generate_checksum(self) -> 'AddressChecksum':
        """
        Generates the correct checksum for this address.
        """
        checksum_trits: MutableSequence[int] = []

        sponge = Kerl()
        sponge.absorb(self.address.as_trits())
        sponge.squeeze(checksum_trits)

        checksum_length = AddressChecksum.LEN * TRITS_PER_TRYTE

        return AddressChecksum.from_trits(checksum_trits[-checksum_length:])

    def add_checksum(self) -> None:
        """
        Adds checksum to :py:class:`Address` object.

        :return: ``None``

        Example usage::

            from iota import Address

            # Example address only, do not use in your code!
            addy = Address(
                b'LVHHIXQNYKWQMGXGLFOKOCDFHPKXAUKWMSZVDRAT'
                b'TICUZXFACM9DNJELJGMLMK99KDVVOOWLINVBZIGWZ'
            )

            # Should be ``False``
            print(addy.is_checksum_valid())

            print(addy.checksum)

            addy.add_checksum()

            # Should be ``True``
            print(addy.is_checksum_valid())

            print(addy.checksum)

        """
        if self.is_checksum_valid():
            # Address already has a valid checksum.
            return

        # Fill checksum attribute
        self.checksum = self._generate_checksum()

        # Add generated checksum to internal buffer.
        self._trytes = self._trytes + self.checksum._trytes

    def remove_checksum(self) -> None:
        """
        Removes checksum from :py:class:`Address` object.

        :return: ``None``

        Example usage::

            from iota import Address

            # Example address only, do not use in your code!
            addy = Address(
                b'LVHHIXQNYKWQMGXGLFOKOCDFHPKXAUKWMSZVDRAT'
                b'TICUZXFACM9DNJELJGMLMK99KDVVOOWLINVBZIGWZ'
                b'AACAMCWUW'  # 9 checksum trytes
            )

            # Should be ``True``
            print(addy.is_checksum_valid())

            print(addy.checksum)

            addy.remove_checksum()

            # Should be ``False``
            print(addy.is_checksum_valid())

            print(addy.checksum)

        """
        self.checksum = None
        self._trytes = self._trytes[:self.LEN]


class AddressChecksum(TryteString):
    """
    A :py:class:`TryteString` that acts as an address checksum.

    :param TrytesCompatible trytes:
        Checksum trytes.

    :raises ValueError: if ``trytes`` is not exactly 9 trytes in length.
    """
    LEN = 9
    """
    Length of an address checksum.
    """

    def __init__(self, trytes: TrytesCompatible) -> None:
        super(AddressChecksum, self).__init__(trytes, pad=None)

        if len(self._trytes) != self.LEN:
            raise with_context(
                exc=ValueError(
                    '{cls} values must be exactly {len} trytes long.'.format(
                        cls=type(self).__name__,
                        len=self.LEN,
                    ),
                ),

                context={
                    'trytes': trytes,
                },
            )


class Tag(TryteString):
    """
    A TryteString that acts as a transaction tag.

    :param TrytesCompatible trytes:
        Tag trytes.

    :raises ValueError: if ``trytes`` is longer than 27 trytes in length.
    """
    LEN = 27
    """
    Length of a tag.
    """

    def __init__(self, trytes: TrytesCompatible) -> None:
        super(Tag, self).__init__(trytes, pad=self.LEN)

        if len(self._trytes) > self.LEN:
            raise with_context(
                exc=ValueError('{cls} values must be {len} trytes long.'.format(
                    cls=type(self).__name__,
                    len=self.LEN
                )),

                context={
                    'trytes': trytes,
                },
            )
