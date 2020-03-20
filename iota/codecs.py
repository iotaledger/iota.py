from codecs import Codec, CodecInfo, register as lookup_function
from typing import Union, Tuple
from warnings import warn

from iota.exceptions import with_context

__all__ = [
    'AsciiTrytesCodec',
    'TrytesDecodeError',
]


class TrytesDecodeError(ValueError):
    """
    Indicates that a tryte string could not be decoded to bytes.
    """
    pass


class AsciiTrytesCodec(Codec):
    """
    Legacy codec for converting byte strings into trytes, and vice
    versa.

    This method encodes each pair of trytes as an ASCII code point (and
    vice versa when decoding).

    The end result requires more space than if the trytes were converted
    mathematically, but because the result is ASCII, it's easier to work
    with.

    Think of this kind of like Base 64 for balanced ternary (:
    """
    name = 'trytes_ascii'

    compat_name = 'trytes'
    """
    Old name for this codec.
    Note:  Will be removed in PyOTA v2.1!
    """

    # :bc: Without the bytearray cast, Python 2 will populate the dict
    # with characters instead of integers.
    alphabet = dict(enumerate(bytearray(b'9ABCDEFGHIJKLMNOPQRSTUVWXYZ')))
    """
    Used to encode bytes into trytes.
    """

    index = dict(zip(alphabet.values(), alphabet.keys()))
    """
    Used to decode trytes into bytes.
    """

    @classmethod
    def get_codec_info(cls) -> CodecInfo:
        """
        Returns information used by the codecs library to configure the
        codec for use.
        """
        codec = cls()

        codec_info = {
            'encode': codec.encode,
            'decode': codec.decode,
            
            # In Python 2, all codecs are made equal.
            # In Python 3, some codecs are more equal than others.
            '_is_text_encoding': False
        }

        return CodecInfo(**codec_info)

    def encode(self,
               input: Union[memoryview, bytes, bytearray],
               errors: str = 'strict') -> Tuple[bytes, int]:
        """
        Encodes a byte string into trytes.
        """
        if isinstance(input, memoryview):
            input = input.tobytes()

        if not isinstance(input, (bytes, bytearray)):
            raise with_context(
                exc=TypeError(
                    "Can't encode {type}; byte string expected.".format(
                        type=type(input).__name__,
                    )),

                context={
                    'input': input,
                },
            )

        # :bc: In Python 2, iterating over a byte string yields
        # characters instead of integers.
        if not isinstance(input, bytearray):
            input = bytearray(input)

        trytes = bytearray()

        for c in input:
            second, first = divmod(c, len(self.alphabet))

            trytes.append(self.alphabet[first])
            trytes.append(self.alphabet[second])

        return bytes(trytes), len(input)

    def decode(self,
               input: Union[memoryview, bytes, bytearray],
               errors: str = 'strict') -> Tuple[bytes, int]:
        """
        Decodes a tryte string into bytes.
        """
        if isinstance(input, memoryview):
            input = input.tobytes()

        if not isinstance(input, (bytes, bytearray)):
            raise with_context(
                exc=TypeError(
                    "Can't decode {type}; byte string expected.".format(
                        type=type(input).__name__,
                    )),

                context={
                    'input': input,
                },
            )

        # :bc: In Python 2, iterating over a byte string yields
        # characters instead of integers.
        if not isinstance(input, bytearray):
            input = bytearray(input)

        bytes_ = bytearray()

        for i in range(0, len(input), 2):
            try:
                first, second = input[i:i + 2]
            except ValueError:
                if errors == 'strict':
                    raise with_context(
                        exc=TrytesDecodeError(
                            "'{name}' codec can't decode value; "
                            "tryte sequence has odd length.".format(
                                name=self.name,
                            ),
                        ),

                        context={
                            'input': input,
                        },
                    )
                elif errors == 'replace':
                    bytes_ += b'?'

                continue

            try:
                bytes_.append(
                    self.index[first]
                    + (self.index[second] * len(self.index))
                )
            except ValueError:
                # This combination of trytes yields a value > 255 when
                # decoded.
                # Naturally, we can't represent this using ASCII.
                if errors == 'strict':
                    raise with_context(
                        exc=TrytesDecodeError(
                            "'{name}' codec can't decode trytes {pair} "
                            "at position {i}-{j}: "
                            "ordinal not in range(255)".format(
                                name=self.name,
                                pair=chr(first) + chr(second),
                                i=i,
                                j=i + 1,
                            ),
                        ),

                        context={
                            'input': input,
                        }
                    )
                elif errors == 'replace':
                    bytes_ += b'?'

        return bytes(bytes_), len(input)


@lookup_function
def check_trytes_codec(encoding):
    """
    Determines which codec to use for the specified encoding.

    References:

    - https://docs.python.org/3/library/codecs.html#codecs.register
    """
    if encoding == AsciiTrytesCodec.name:
        return AsciiTrytesCodec.get_codec_info()

    elif encoding == AsciiTrytesCodec.compat_name:
        warn(
            '"{old_codec}" codec will be removed in PyOTA v2.1. '
            'Use "{new_codec}" instead.'.format(
                new_codec=AsciiTrytesCodec.name,
                old_codec=AsciiTrytesCodec.compat_name,
            ),

            DeprecationWarning,
        )
        return AsciiTrytesCodec.get_codec_info()

    return None
